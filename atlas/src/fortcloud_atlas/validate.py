"""Structural and semantic validation of the FortCloud Atlas model."""

from __future__ import annotations

from collections import Counter
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


def _check_duplicates(items: list[dict], label: str, errors: list[str]) -> dict:
    counts = Counter(item.get("id") for item in items)
    for identifier, count in counts.items():
        if count > 1:
            errors.append(f"{label}: identifier '{identifier}' used {count} times")
    return {item.get("id"): item for item in items}


def semantic_checks(model: dict, today: date) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    components = _check_duplicates(model["components"], "components", errors)
    _check_duplicates(model["dependencies"], "dependencies", errors)
    _check_duplicates(model["flows"], "flows", errors)
    _check_duplicates(model["risks"], "risks", errors)

    for dependency in model["dependencies"]:
        for field in ("from", "to"):
            if dependency[field] not in components:
                errors.append(
                    f"dependency {dependency['id']}: component '{dependency[field]}' not found ({field})"
                )

    for flow in model["flows"]:
        for component_id in flow["components"] + flow["external_dependencies"]:
            if component_id not in components:
                errors.append(f"flow {flow['id']}: component '{component_id}' not found")
        age = core.test_age_days(flow["last_restore_test"], today)
        if age is None:
            warnings.append(f"flow {flow['id']}: no dated restore test")
        elif age > core.TEST_MAX_AGE_DAYS:
            warnings.append(
                f"flow {flow['id']}: last restore test {age} days ago "
                f"(max {core.TEST_MAX_AGE_DAYS})"
            )

    flow_ids = {flow["id"] for flow in model["flows"]}
    for risk in model["risks"]:
        for component_id in risk["components"]:
            if component_id not in components:
                errors.append(f"risk {risk['id']}: component '{component_id}' not found")
        for flow_id in risk["flows"]:
            if flow_id not in flow_ids:
                errors.append(f"risk {risk['id']}: flow '{flow_id}' not found")
        if core.risk_score(risk) >= 15 and risk["status"] not in ("mitigated", "closed"):
            warnings.append(
                f"risk {risk['id']}: score {core.risk_score(risk)} (critical) "
                f"and status '{risk['status']}'"
            )

    active_risks = [risk for risk in model["risks"] if risk["status"] != "closed"]

    for component in model["components"]:
        identifier = component["id"]
        linked_risks = [risk for risk in active_risks if identifier in risk["components"]]

        if core.is_spof(component) and component["criticality"] == "P0" and not linked_risks:
            errors.append(
                f"component {identifier}: P0 single instance without an active risk, "
                f"owner and corrective action"
            )
        if core.is_single_region_p0(component):
            warnings.append(
                f"component {identifier}: P0 in a single region — a regional outage "
                f"is enough to lose it"
            )
        if component["category"] == "storage" and component["criticality"] == "P0":
            backup = component.get("backup") or {}
            if not backup.get("enabled") or not backup.get("immutable"):
                errors.append(f"component {identifier}: P0 storage without an immutable backup")
            age = core.test_age_days(backup.get("last_restore_test"), today)
            if age is None or age > core.TEST_MAX_AGE_DAYS:
                warnings.append(f"component {identifier}: no recent restore test")

        inbound = [dep for dep in model["dependencies"] if dep["to"] == identifier]
        outbound = [dep for dep in model["dependencies"] if dep["from"] == identifier]
        if not inbound and not outbound:
            warnings.append(f"component {identifier}: no declared dependency")

    flow_ids_with_risk = {flow_id for risk in active_risks for flow_id in risk["flows"]}
    for flow in model["flows"]:
        if flow["criticality"] == "P0" and flow["id"] not in flow_ids_with_risk:
            warnings.append(f"flow {flow['id']}: P0 flow without an associated risk")

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
