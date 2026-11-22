"""Data model and shared calculations for FortCloud Ballast."""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

# src/fortcloud_ballast/core.py -> parents[2] is the tool's root directory.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

MAX_RETRIES = 3
MAX_FAILURE_THRESHOLD = 10
MAX_RESET_TIMEOUT_MS = 30_000
DOMINANT_STEP_RATIO = 0.70

FILES = {
    "services": ("services.yaml", "service.schema.json"),
    "dependencies": ("dependencies.yaml", "dependency.schema.json"),
    "policies": ("policies.yaml", "policy.schema.json"),
    "flows": ("flows.yaml", "flow.schema.json"),
}

TYPE_LABELS = {
    "database": "Database",
    "cache": "Cache",
    "http_api": "API HTTP",
    "grpc": "gRPC",
    "queue": "Event queue",
    "search": "Search engine",
}

FALLBACK_LABELS = {
    "none": "None",
    "cached": "Cached data",
    "default": "Default value",
    "degraded": "Degraded mode",
    "queue": "Queuing",
}

# Since timeouts are often sub-second, all durations are stored in ms.
_DURATION_PATTERN = re.compile(r"^(0|([0-9]+(ms|s|m|h|d))+)$")
_TOKEN_PATTERN = re.compile(r"([0-9]+)(ms|s|m|h|d)")
_UNIT_MS = {"ms": 1, "s": 1000, "m": 60_000, "h": 3_600_000, "d": 86_400_000}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Find the schema directory, even when the tool is installed outside the repository."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_BALLAST_SCHEMA_DIR")
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
    """Load the four YAML collections of the Ballast model."""
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
    """Convert `0` or a sequence of `<number><ms|s|m|h|d>` to milliseconds."""
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


def format_duration(milliseconds: int | None) -> str:
    """Format a duration that can be reused as a model value (`1m30s`, `150ms`)."""
    if milliseconds is None:
        return "?"
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


def service_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("services", [])}


def dependency_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("dependencies", [])}


def policy_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("policies", [])}


def flow_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("flows", [])}


def policy_for_dependency(model: dict, dependency_id: str) -> dict | None:
    for item in model.get("policies", []):
        if item.get("dependency") == dependency_id:
            return item
    return None


def flows_using_dependency(model: dict, dependency_id: str) -> list[dict]:
    return [
        flow
        for flow in model.get("flows", [])
        if any(step.get("dependency") == dependency_id for step in flow.get("steps", []))
    ]


def worst_case_ms(policy: dict) -> int:
    """Maximum time for a step: attempts plus exponential backoff."""
    timeout = parse_duration(policy.get("timeout")) or 0
    retries = policy.get("retries", 0)
    backoff = parse_duration(policy.get("backoff")) or 0
    multiplier = policy.get("backoff_multiplier", 1)
    delays = sum(backoff * (multiplier ** index) for index in range(retries))
    return timeout * (retries + 1) + delays


def step_duration_ms(model: dict, step: dict) -> int:
    policy = policy_map(model).get(step.get("policy"))
    return worst_case_ms(policy) if policy else 0


def flow_total_ms(model: dict, flow: dict) -> int:
    return sum(step_duration_ms(model, step) for step in flow.get("steps", []))


def budget_ms(model: dict, flow: dict) -> int | None:
    service = service_map(model).get(flow.get("service"))
    return parse_duration(service.get("latency_budget")) if service else None


def utilization(model: dict, flow: dict) -> float | None:
    budget = budget_ms(model, flow)
    if not budget:
        return None
    return flow_total_ms(model, flow) / budget


def dominant_step(model: dict, flow: dict) -> tuple[dict, float] | None:
    """Return the step that consumes the largest share of the budget."""
    budget = budget_ms(model, flow)
    if not budget:
        return None
    best = None
    for step in flow.get("steps", []):
        ratio = step_duration_ms(model, step) / budget
        if best is None or ratio > best[1]:
            best = (step, ratio)
    return best
