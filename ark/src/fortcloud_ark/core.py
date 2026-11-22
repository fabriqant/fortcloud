"""Data model and shared rules for FortCloud Ark."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_ark/core.py -> parents[2] is the tool's root folder.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

RESTORE_MAX_AGE_DAYS = 90
BACKUP_MAX_AGE_DAYS = 2
MIN_RETENTION_DAYS = 30

FILES = {
    "assets": ("assets.yaml", "asset.schema.json"),
    "backups": ("backups.yaml", "backup.schema.json"),
    "restores": ("restores.yaml", "restore.schema.json"),
    "services": ("services.yaml", "service.schema.json"),
}

CATEGORY_LABELS = {
    "database": "Database",
    "object_store": "Object store",
    "file_share": "File share",
    "queue": "Event queue",
    "config": "Configuration",
    "secrets": "Secrets",
    "log": "Logs",
}

SCENARIO_LABELS = {
    "point_in_time": "Point-in-time restore",
    "full_loss": "Full loss",
    "region_loss": "Region loss",
    "deletion": "Accidental deletion",
    "ransomware": "Ransomware",
}

_DURATION_PATTERN = re.compile(r"^(0|[0-9]+[smhd]([0-9]+[smhd])*)$")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Find the schema directory, even when the tool is installed outside the repository."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_ARK_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "asset.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Load the four YAML collections of the Ark model."""
    base = Path(model_dir)
    model = {}
    for key, (filename, _) in FILES.items():
        path = base / filename
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        document = load_yaml(path)
        if key not in document:
            raise ValueError(f"{path.name}: key '{key}' missing")
        model[key] = document[key] or []
    return model


def load_schema(key: str, schema_dir: str | Path | None = None) -> dict:
    filename = FILES[key][1]
    path = resolve_schema_dir(schema_dir) / filename
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    return load_yaml(path)


def parse_duration(value) -> int | None:
    """Convert `0` or a sequence of `<number><s|m|h|d>` into seconds."""
    if value is None:
        return None
    text = str(value).strip()
    if not _DURATION_PATTERN.match(text):
        return None
    if text == "0":
        return 0
    return sum(
        int(amount) * _UNIT_SECONDS[unit]
        for amount, unit in re.findall(r"([0-9]+)([smhd])", text)
    )


def format_duration(seconds: int | None) -> str:
    """Format as a reusable duration for a model value (`2m12s`)."""
    if seconds is None:
        return "?"
    if seconds == 0:
        return "0"
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    for amount, unit in ((days, "d"), (hours, "h"), (minutes, "m"), (secs, "s")):
        if amount:
            parts.append(f"{amount}{unit}")
    return "".join(parts)


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def age_days(value, today: date | None = None):
    dated = parse_date(value)
    if dated is None:
        return None
    return ((today or date.today()) - dated).days


def asset_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("assets", [])}


def backup_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("backups", [])}


def service_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("services", [])}


def backups_for_asset(model: dict, asset_id: str) -> list[dict]:
    return [item for item in model.get("backups", []) if item.get("asset") == asset_id]


def restores_for_backup(model: dict, backup_id: str) -> list[dict]:
    return [item for item in model.get("restores", []) if item.get("backup") == backup_id]


def restores_for_asset(model: dict, asset_id: str) -> list[dict]:
    identifiers = {item["id"] for item in backups_for_asset(model, asset_id)}
    return [item for item in model.get("restores", []) if item.get("backup") in identifiers]


def services_using_asset(model: dict, asset_id: str) -> list[dict]:
    return [item for item in model.get("services", []) if asset_id in item.get("assets", [])]


def targets_for_asset(model: dict, asset_id: str) -> tuple[int | None, int | None]:
    """Tightest RTO and RPO among the services that use the asset."""
    services = services_using_asset(model, asset_id)
    rto_values = [parse_duration(item.get("rto")) for item in services]
    rpo_values = [parse_duration(item.get("rpo")) for item in services]
    rto = [value for value in rto_values if value is not None]
    rpo = [value for value in rpo_values if value is not None]
    return (min(rto) if rto else None, min(rpo) if rpo else None)


def covered_assets(model: dict) -> set:
    return {item.get("asset") for item in model.get("backups", [])}
