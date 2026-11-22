"""Structural and semantic validation of the FortCloud Ark model."""

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
    """Return (errors, warnings, issues per asset)."""
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    issues: dict[str, list[str]] = defaultdict(list)

    for key, label in (
        ("assets", "assets"),
        ("backups", "backups"),
        ("restores", "restores"),
        ("services", "services"),
    ):
        _check_duplicates(model.get(key, []), label, errors)

    assets = core.asset_map(model)
    backups = core.backup_map(model)

    for service in model.get("services", []):
        for asset_id in service.get("assets", []):
            if asset_id not in assets:
                errors.append(f"service {service['id']}: asset '{asset_id}' not found")

    for backup in model.get("backups", []):
        bid = backup["id"]
        asset = assets.get(backup.get("asset"))
        if asset is None:
            errors.append(f"backup {bid}: asset '{backup.get('asset')}' not found")
            continue
        asset_id = asset["id"]
        critical = asset.get("criticality") == "P0"

        if critical and not backup.get("immutable"):
            message = "P0 backup is not immutable"
            errors.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

        if asset.get("classification") in ("confidential", "restricted") and not (
            asset.get("encryption_at_rest") and backup.get("encrypted")
        ):
            message = "sensitive asset without encryption at rest on source and backup"
            errors.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

        if critical and backup.get("retention_days", 0) < core.MIN_RETENTION_DAYS:
            message = (
                f"retention {backup.get('retention_days')} d is below "
                f"{core.MIN_RETENTION_DAYS} d for a P0 asset"
            )
            warnings.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

        if critical and not backup.get("cross_region"):
            message = "no cross-region copy for a P0 asset"
            warnings.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

        age = core.age_days(backup.get("last_successful"), today)
        if age is None:
            message = "no dated successful backup"
            warnings.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)
        elif age > core.BACKUP_MAX_AGE_DAYS:
            message = (
                f"last successful backup is {age} days old "
                f"(max {core.BACKUP_MAX_AGE_DAYS})"
            )
            warnings.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

        schedule = core.parse_duration(backup.get("schedule"))
        _, rpo_target = core.targets_for_asset(model, asset_id)
        if schedule is None:
            message = "invalid backup schedule"
            errors.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)
        elif rpo_target is not None and rpo_target > 0 and schedule > rpo_target:
            message = (
                f"backup schedule {core.format_duration(schedule)} cannot satisfy "
                f"RPO {core.format_duration(rpo_target)}"
            )
            errors.append(f"backup {bid}: {message}")
            issues[asset_id].append(message)

    for asset in model.get("assets", []):
        asset_id = asset["id"]
        critical = asset.get("criticality") == "P0"
        linked_backups = core.backups_for_asset(model, asset_id)
        if not linked_backups:
            message = "no backup policy"
            if critical:
                errors.append(f"asset {asset_id}: {message}")
            else:
                warnings.append(f"asset {asset_id}: {message}")
            issues[asset_id].append(message)

        restores = core.restores_for_asset(model, asset_id)
        if not restores:
            message = "no restore test"
            if critical:
                errors.append(f"asset {asset_id}: {message}")
            else:
                warnings.append(f"asset {asset_id}: {message}")
            issues[asset_id].append(message)

        if critical:
            scenarios = {item.get("scenario") for item in restores}
            if not scenarios.intersection({"ransomware", "deletion"}):
                message = "no ransomware or deletion restore scenario for a P0 asset"
                warnings.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)

        rto_target, rpo_target = core.targets_for_asset(model, asset_id)
        for restore in restores:
            rid = restore["id"]
            if restore.get("backup") not in backups:
                message = f"backup '{restore.get('backup')}' not found"
                errors.append(f"restore {rid}: {message}")
                issues[asset_id].append(message)
                continue

            age = core.age_days(restore.get("last"), today)
            if age is None:
                message = f"restore {rid}: no valid test date"
                warnings.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)
            elif age > core.RESTORE_MAX_AGE_DAYS:
                message = (
                    f"restore {rid} is {age} days old (max {core.RESTORE_MAX_AGE_DAYS})"
                )
                warnings.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)

            if restore.get("result") != "passed":
                message = f"restore {rid} result is '{restore.get('result')}'"
                warnings.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)

            if not restore.get("evidence"):
                message = f"restore {rid} has no evidence"
                warnings.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)

            measured_rto = core.parse_duration(restore.get("measured_rto"))
            measured_rpo = core.parse_duration(restore.get("measured_rpo"))
            if measured_rto is None or measured_rpo is None:
                message = f"restore {rid}: invalid measured_rto or measured_rpo"
                errors.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)
                continue

            if rto_target is not None and measured_rto > rto_target:
                message = (
                    f"restore {rid} measured RTO {core.format_duration(measured_rto)} "
                    f"exceeds target {core.format_duration(rto_target)}"
                )
                errors.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)
            if rpo_target is not None and measured_rpo > rpo_target:
                message = (
                    f"restore {rid} measured RPO {core.format_duration(measured_rpo)} "
                    f"exceeds target {core.format_duration(rpo_target)}"
                )
                errors.append(f"asset {asset_id}: {message}")
                issues[asset_id].append(message)

    for service in model.get("services", []):
        if not service.get("assets"):
            warnings.append(f"service {service['id']}: no data asset declared")

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
