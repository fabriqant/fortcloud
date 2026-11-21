"""Validation structurelle et sémantique du modèle Fortcloud Vitals."""

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
    """Return (errors, warnings, issues keyed by 'objective:<id>' or 'check:<id>')."""
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    issues: dict[str, list[str]] = defaultdict(list)

    for key, label in (
        ("services", "services"),
        ("signals", "signals"),
        ("objectives", "objectives"),
        ("checks", "checks"),
    ):
        _check_duplicates(model.get(key, []), label, errors)

    services = core.service_map(model)
    signals = core.signal_map(model)
    objectives = core.objective_map(model)

    for objective in model.get("objectives", []):
        oid = objective["id"]
        subject = f"objective:{oid}"
        service = services.get(objective.get("service"))
        signal = signals.get(objective.get("signal"))
        kind = objective.get("kind")

        if service is None:
            message = f"service '{objective.get('service')}' not found"
            errors.append(f"objective {oid}: {message}")
            issues[subject].append(message)
            continue
        if signal is None:
            message = f"signal '{objective.get('signal')}' not found"
            errors.append(f"objective {oid}: {message}")
            issues[subject].append(message)
            continue
        if signal.get("kind") != kind:
            message = (
                f"signal kind '{signal.get('kind')}' does not match "
                f"objective kind '{kind}'"
            )
            errors.append(f"objective {oid}: {message}")
            issues[subject].append(message)

        metrics = core.objective_metrics(model, objective)

        if kind in core.PERCENT_KINDS:
            target = core.parse_percent(objective.get("target"))
            alert = core.parse_percent(objective.get("alert_threshold"))
            if target is None or alert is None:
                message = "invalid target or alert_threshold"
                errors.append(f"objective {oid}: {message}")
                issues[subject].append(message)
            elif alert <= target:
                message = (
                    f"alert threshold {core.format_percent(alert)}% is not tighter "
                    f"than target {core.format_percent(target)}%"
                )
                errors.append(f"objective {oid}: {message}")
                issues[subject].append(message)
        else:
            target_ms = core.parse_duration(objective.get("target"))
            alert_ms = core.parse_duration(objective.get("alert_threshold"))
            if target_ms is None or alert_ms is None:
                message = "invalid target or alert_threshold duration"
                errors.append(f"objective {oid}: {message}")
                issues[subject].append(message)
            elif alert_ms > target_ms:
                message = (
                    f"alert threshold {core.format_duration(alert_ms)} is looser "
                    f"than target {core.format_duration(target_ms)}"
                )
                errors.append(f"objective {oid}: {message}")
                issues[subject].append(message)

        used = metrics.get("budget_used")
        if used is not None and used > core.MAX_BUDGET_USED_AT_ALERT:
            message = (
                f"alert fires after {used:.0%} of the error budget is spent "
                f"(max {core.MAX_BUDGET_USED_AT_ALERT:.0%})"
            )
            warnings.append(f"objective {oid}: {message}")
            issues[subject].append(message)

        margin = metrics.get("margin_ratio")
        if margin is not None and margin < core.MIN_MARGIN_RATIO:
            message = (
                f"alert margin {margin:.0%} is below the "
                f"{core.MIN_MARGIN_RATIO:.0%} minimum"
            )
            warnings.append(f"objective {oid}: {message}")
            issues[subject].append(message)

        max_interval = metrics.get("max_interval_ms")
        interval = metrics.get("interval_ms")
        if max_interval is not None and interval is not None and interval > max_interval:
            message = (
                f"signal interval {core.format_duration(interval)} is too coarse "
                f"(max {core.format_duration_rounded(max_interval)})"
            )
            warnings.append(f"objective {oid}: {message}")
            issues[subject].append(message)

        window = metrics.get("window_ms")
        if window is None:
            message = "invalid window"
            errors.append(f"objective {oid}: {message}")
            issues[subject].append(message)
        elif window < core.MIN_WINDOW_MS:
            message = (
                f"window {core.format_duration(window)} is shorter than "
                f"{core.format_duration(core.MIN_WINDOW_MS)}"
            )
            warnings.append(f"objective {oid}: {message}")
            issues[subject].append(message)

    for service in model.get("services", []):
        if service.get("criticality") != "P0":
            continue
        related = core.objectives_for_service(model, service["id"])
        kinds = {item.get("kind") for item in related}
        if "availability" not in kinds:
            message = "P0 service has no availability objective"
            errors.append(f"service {service['id']}: {message}")
            issues[f"objective:{service['id']}"].append(message)
        if not kinds.intersection(core.DATA_QUALITY_KINDS):
            message = "P0 service has no data-quality objective"
            errors.append(f"service {service['id']}: {message}")
            issues[f"objective:{service['id']}"].append(message)

    for signal in model.get("signals", []):
        if not core.objectives_for_signal(model, signal["id"]):
            message = f"signal '{signal['id']}' is not used by any objective"
            warnings.append(message)

    for check in model.get("checks", []):
        cid = check["id"]
        subject = f"check:{cid}"
        objective = objectives.get(check.get("objective"))
        if objective is None:
            message = f"objective '{check.get('objective')}' not found"
            errors.append(f"check {cid}: {message}")
            issues[subject].append(message)
            continue
        service = services.get(objective.get("service"), {})
        critical = service.get("criticality") == "P0"

        age = core.age_days(check.get("last"), today)
        if age is None:
            message = "no valid check date"
            warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)
        elif age > core.MAX_CHECK_AGE_DAYS:
            message = (
                f"last check is {age} days old (max {core.MAX_CHECK_AGE_DAYS})"
            )
            warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)

        result = check.get("result")
        if result == "failed" and critical:
            message = "failed check on a P0 service"
            errors.append(f"check {cid}: {message}")
            issues[subject].append(message)
        elif result != "passed":
            message = f"result is '{result}'"
            warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)

        if not check.get("evidence"):
            message = "no evidence link"
            warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)

        if not check.get("runbook"):
            message = "no runbook"
            if critical:
                errors.append(f"check {cid}: {message}")
            else:
                warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)

    for objective in model.get("objectives", []):
        if not core.checks_for_objective(model, objective["id"]):
            message = f"objective '{objective['id']}' has no verification check"
            warnings.append(message)

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
