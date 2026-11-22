"""Data model and shared rules for FortCloud Failover."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_failover/core.py -> parents[2] is the repository root.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

DRILL_MAX_AGE_DAYS = 90

FILES = {
    "topology": ("topology.yaml", "topology.schema.json"),
    "services": ("services.yaml", "service.schema.json"),
    "strategies": ("strategies.yaml", "strategy.schema.json"),
    "drills": ("drills.yaml", "drill.schema.json"),
}

MODE_LABELS = {
    "active_active": "Active/active",
    "active_passive": "Active/passive",
    "warm": "Warm",
    "cold": "Cold",
}

ROLE_LABELS = {
    "primary": "Primary",
    "standby": "Standby",
    "standalone": "Standalone",
}

_DURATION_PATTERN = re.compile(r"^(0|[0-9]+[smhd]([0-9]+[smhd])*)$")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Find the schema directory, even when the tool is installed outside the repository."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_FAILOVER_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "topology.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Load the four YAML collections of the Failover model."""
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
    return sum(int(amount) * _UNIT_SECONDS[unit] for amount, unit in re.findall(r"([0-9]+)([smhd])", text))


def format_duration(seconds: int | None) -> str:
    """Format a duration that can be reused as a model value (`2m12s`)."""
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


def drill_age_days(value, today: date | None = None):
    tested = parse_date(value)
    if tested is None:
        return None
    return ((today or date.today()) - tested).days


def component_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("topology", [])}


def service_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("services", [])}


def strategy_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("strategies", [])}


def services_using(model: dict, component_id: str) -> list[dict]:
    return [item for item in model.get("services", []) if component_id in item.get("components", [])]


def switchover_seconds(strategy: dict) -> int | None:
    detection = parse_duration(strategy.get("detection_time"))
    promotion = parse_duration(strategy.get("promotion_time"))
    if detection is None or promotion is None:
        return None
    return detection + promotion


def rto_budget(strategy: dict, model: dict) -> int | None:
    """The tightest RTO among the services covered by the strategy."""
    services = services_using(model, strategy.get("primary", "")) + services_using(
        model, strategy.get("standby", "")
    )
    unique = {item["id"]: item for item in services}
    values = [parse_duration(item.get("rto")) for item in unique.values()]
    budgets = [value for value in values if value is not None]
    return min(budgets) if budgets else None


def covered_components(model: dict) -> set:
    identifiers = set()
    for strategy in model.get("strategies", []):
        for field in ("primary", "standby"):
            if strategy.get(field):
                identifiers.add(strategy[field])
    return identifiers
