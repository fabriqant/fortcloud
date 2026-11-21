"""Structural and semantic validation of the Fortcloud Failover model."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

from . import core


def schema_errors(model_dir: Path, schema_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    for key, (filename, _) in core.FILES.items():
        path = Path(model_dir) / filename
        if not path.exists():
            errors.append(f"{filename}: file missing")
            continue
        try:
            document = core.load_yaml(path)
            schema = core.load_schema(key, schema_dir)
        except (OSError, ValueError) as exc:
            errors.append(f"{filename}: {exc}")
            continue
        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
            location = "/".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{filename} [{location}]: {error.message}")
    return errors


def _check_duplicates(items: list[dict], label: str, errors: list[str]) -> None:
    counts = Counter(item.get("id") for item in items)
    for identifier, count in counts.items():
        if count > 1:
            errors.append(f"{label}: identifier '{identifier}' used {count} times")


def analyse(
    model: dict, today: date | None = None
) -> tuple[list[str], list[str], dict[str, list[str]]]:
    """Return (errors, warnings, issues per strategy).

    `issues` is the strategy-level detail used by the generated remediation plan.
    """
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    issues: dict[str, list[str]] = defaultdict(list)

    for key, label in (
        ("topology", "components"),
        ("services", "services"),
        ("strategies", "strategies"),
        ("drills", "drills"),
    ):
        _check_duplicates(model.get(key, []), label, errors)

    components = core.component_map(model)
    drills = model.get("drills", [])

    for service in model.get("services", []):
        for component_id in service.get("components", []):
            if component_id not in components:
                errors.append(
                    f"service {service['id']}: component '{component_id}' not found"
                )

    for strategy in model.get("strategies", []):
        sid = strategy["id"]
        for field in ("primary", "standby"):
            identifier = strategy.get(field)
            if identifier not in components:
                message = f"{field} component '{identifier}' not found"
                errors.append(f"strategy {sid}: {message}")
                issues[sid].append(message)

        primary = components.get(strategy.get("primary"))
        standby = components.get(strategy.get("standby"))
        if primary and standby:
            if primary.get("role") != "primary":
                message = f"primary '{primary['id']}' has role '{primary.get('role')}'"
                errors.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if standby.get("role") != "standby":
                message = f"standby '{standby['id']}' has role '{standby.get('role')}'"
                errors.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if primary.get("pair") != standby.get("pair"):
                message = (
                    f"primary and standby do not share the same pair "
                    f"('{primary.get('pair')}' vs '{standby.get('pair')}')"
                )
                errors.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if primary.get("region") == standby.get("region"):
                message = f"false redundancy: both instances are in '{primary.get('region')}'"
                errors.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            elif primary.get("provider") == standby.get("provider"):
                message = f"both instances use the same provider '{primary.get('provider')}'"
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if standby.get("capacity", 0) < primary.get("capacity", 0):
                message = (
                    f"standby capacity {standby.get('capacity')} is lower than "
                    f"primary capacity {primary.get('capacity')}"
                )
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)

        switchover = core.switchover_seconds(strategy)
        rto = core.rto_budget(strategy, model)
        if switchover is None:
            message = "invalid detection_time or promotion_time"
            errors.append(f"strategy {sid}: {message}")
            issues[sid].append(message)
        elif rto is not None and switchover > rto:
            message = (
                f"switchover {core.format_duration(switchover)} exceeds the tightest "
                f"RTO {core.format_duration(rto)}"
            )
            errors.append(f"strategy {sid}: {message}")
            issues[sid].append(message)

        ttl = core.parse_duration(strategy.get("dns_ttl"))
        if ttl is None:
            message = "invalid dns_ttl"
            errors.append(f"strategy {sid}: {message}")
            issues[sid].append(message)
        elif rto is not None and ttl > rto:
            message = f"DNS TTL {core.format_duration(ttl)} exceeds RTO {core.format_duration(rto)}"
            warnings.append(f"strategy {sid}: {message}")
            issues[sid].append(message)

        linked_services = core.services_using(model, strategy.get("primary", ""))
        rpo_zero = [
            service["id"]
            for service in linked_services
            if core.parse_duration(service.get("rpo")) == 0
        ]
        if rpo_zero and strategy.get("replication") in ("async", "none"):
            message = (
                f"'{strategy.get('replication')}' replication cannot satisfy RPO 0 "
                f"for {', '.join(rpo_zero)}"
            )
            errors.append(f"strategy {sid}: {message}")
            issues[sid].append(message)

        if not strategy.get("automated") and any(
            service.get("criticality") == "P0" for service in linked_services
        ):
            message = "switchover is manual for a P0 service"
            warnings.append(f"strategy {sid}: {message}")
            issues[sid].append(message)

        linked_drills = [item for item in drills if item.get("strategy") == sid]
        if not linked_drills:
            message = "no drill recorded"
            warnings.append(f"strategy {sid}: {message}")
            issues[sid].append(message)
        for drill in linked_drills:
            age = core.drill_age_days(drill.get("last"), today)
            if age is None:
                message = f"drill {drill['id']}: no valid drill date"
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            elif age > core.DRILL_MAX_AGE_DAYS:
                message = (
                    f"drill {drill['id']} is {age} days old "
                    f"(max {core.DRILL_MAX_AGE_DAYS})"
                )
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if drill.get("result") != "passed":
                message = f"drill {drill['id']} result is '{drill.get('result')}'"
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)
            if not drill.get("evidence"):
                message = f"drill {drill['id']} has no evidence"
                warnings.append(f"strategy {sid}: {message}")
                issues[sid].append(message)

        if not linked_services:
            message = "strategy covers no service"
            warnings.append(f"strategy {sid}: {message}")
            issues[sid].append(message)

    covered = core.covered_components(model)
    for component in model.get("topology", []):
        if component.get("criticality") == "P0" and component["id"] not in covered:
            errors.append(
                f"component {component['id']}: P0 component without a failover strategy"
            )

    return errors, warnings, dict(issues)


def semantic_checks(model: dict, today: date | None = None) -> tuple[list[str], list[str]]:
    errors, warnings, _ = analyse(model, today)
    return errors, warnings


def collect(
    model_dir: str | Path = core.DEFAULT_MODEL,
    schema_dir: str | Path | None = None,
    today: date | None = None,
) -> tuple[dict, list[str], list[str]]:
    """Return (model, errors, warnings)."""
    today = today or date.today()
    model_dir = Path(model_dir)
    errors = schema_errors(model_dir, schema_dir)
    warnings: list[str] = []
    model: dict = {}
    try:
        model = core.load_model(model_dir)
    except (FileNotFoundError, ValueError) as exc:
        errors.append(str(exc))
    if model:
        semantic_errors, warnings = semantic_checks(model, today)
        errors.extend(semantic_errors)
    return model, errors, warnings
