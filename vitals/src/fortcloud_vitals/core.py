"""Data model and error-budget calculations for Fortcloud Vitals."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_vitals/core.py -> parents[2] is the tool folder root.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

MAX_CHECK_AGE_DAYS = 90
MAX_BUDGET_USED_AT_ALERT = 0.50
MIN_MARGIN_RATIO = 0.20
MIN_WINDOW_MS = 7 * 86_400_000
INTERVAL_SAMPLES = 10

PERCENT_KINDS = ("availability", "completeness", "validity")
DURATION_KINDS = ("latency", "freshness")
DATA_QUALITY_KINDS = ("freshness", "completeness", "validity")

FILES = {
    "services": ("services.yaml", "service.schema.json"),
    "signals": ("signals.yaml", "signal.schema.json"),
    "objectives": ("objectives.yaml", "objective.schema.json"),
    "checks": ("checks.yaml", "check.schema.json"),
}

KIND_LABELS = {
    "availability": "Availability",
    "latency": "Latency",
    "freshness": "Freshness",
    "completeness": "Completeness",
    "validity": "Validity",
}

SOURCE_LABELS = {
    "prometheus": "Prometheus",
    "datadog": "Datadog",
    "cloudwatch": "CloudWatch",
    "sql": "SQL query",
    "custom": "Custom",
}

_DURATION_PATTERN = re.compile(r"^(0|([0-9]+(ms|s|m|h|d))+)$")
_TOKEN_PATTERN = re.compile(r"([0-9]+)(ms|s|m|h|d)")
_UNIT_MS = {"ms": 1, "s": 1000, "m": 60_000, "h": 3_600_000, "d": 86_400_000}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Find the schema directory, even outside the repository."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_VITALS_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "service.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Load the four YAML collections of the Vitals model."""
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
    """Convert `0` or a sequence of `<number><ms|s|m|h|d>` into milliseconds."""
    if value is None:
        return None
    text = str(value).strip()
    if not _DURATION_PATTERN.match(text):
        return None
    if text == "0":
        return 0
    return sum(
        int(amount) * _UNIT_MS[unit] for amount, unit in _TOKEN_PATTERN.findall(text)
    )


def format_duration(milliseconds) -> str:
    """Format as a duration reusable as a model value (`43m12s`)."""
    if milliseconds is None:
        return "?"
    milliseconds = int(round(milliseconds))
    if milliseconds == 0:
        return "0"
    days, remainder = divmod(milliseconds, 86_400_000)
    hours, remainder = divmod(remainder, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    parts = []
    for amount, unit in (
        (days, "d"),
        (hours, "h"),
        (minutes, "m"),
        (seconds, "s"),
        (millis, "ms"),
    ):
        if amount:
            parts.append(f"{amount}{unit}")
    return "".join(parts)


def format_duration_rounded(milliseconds) -> str:
    """Format in whole seconds for report labels."""
    if milliseconds is None:
        return "?"
    return format_duration(int(round(milliseconds / 1000)) * 1000)


def parse_percent(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_percent(value, digits: int = 3) -> str:
    if value is None:
        return "?"
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


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


def service_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("services", [])}


def signal_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("signals", [])}


def objective_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("objectives", [])}


def check_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("checks", [])}


def objectives_for_service(model: dict, service_id: str) -> list[dict]:
    return [
        item
        for item in model.get("objectives", [])
        if item.get("service") == service_id
    ]


def objectives_for_signal(model: dict, signal_id: str) -> list[dict]:
    return [
        item
        for item in model.get("objectives", [])
        if item.get("signal") == signal_id
    ]


def checks_for_objective(model: dict, objective_id: str) -> list[dict]:
    return [
        item
        for item in model.get("checks", [])
        if item.get("objective") == objective_id
    ]


def latest_check(model: dict, objective_id: str) -> dict | None:
    linked = checks_for_objective(model, objective_id)
    return max(linked, key=lambda item: str(item.get("last", ""))) if linked else None


def objective_metrics(model: dict, objective: dict) -> dict:
    """Compute the error budget, alert margin, and maximum sampling interval."""
    signals = signal_map(model)
    signal = signals.get(objective.get("signal"), {})
    kind = objective.get("kind")
    window_ms = parse_duration(objective.get("window"))
    interval_ms = parse_duration(signal.get("interval"))
    metrics = {
        "kind": kind,
        "window_ms": window_ms,
        "interval_ms": interval_ms,
        "budget_ms": None,
        "alert_budget_ms": None,
        "budget_used": None,
        "margin_ms": None,
        "margin_ratio": None,
        "max_interval_ms": None,
    }

    if kind in PERCENT_KINDS:
        target = parse_percent(objective.get("target"))
        alert = parse_percent(objective.get("alert_threshold"))
        if window_ms is not None and target is not None and alert is not None:
            metrics["budget_ms"] = round(window_ms * (100 - target) / 100)
            metrics["alert_budget_ms"] = round(window_ms * (100 - alert) / 100)
            metrics["max_interval_ms"] = metrics["budget_ms"] / INTERVAL_SAMPLES
            if metrics["budget_ms"] > 0:
                metrics["budget_used"] = (
                    metrics["alert_budget_ms"] / metrics["budget_ms"]
                )
        return metrics

    target_ms = parse_duration(objective.get("target"))
    alert_ms = parse_duration(objective.get("alert_threshold"))
    if target_ms is not None and alert_ms is not None:
        metrics["margin_ms"] = target_ms - alert_ms
        if target_ms > 0:
            metrics["margin_ratio"] = metrics["margin_ms"] / target_ms
        if kind == "freshness":
            metrics["max_interval_ms"] = target_ms / 2
    return metrics
