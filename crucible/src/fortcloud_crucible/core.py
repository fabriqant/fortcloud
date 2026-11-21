"""Modèle de données et helpers de planification de Fortcloud Crucible."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_crucible/core.py -> parents[2] est la racine du dossier de l'outil.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

MAX_EXERCISE_DURATION_MS = 4 * 3_600_000
MAX_UPDATE_INTERVAL_MS = 15 * 60_000

KINDS = ("restore", "failover", "recovery")
ISOLATION_LEVELS = ("full", "partial", "shared")
DATA_KINDS = ("synthetic", "masked", "production")
CONTROLLED_ISOLATION = ("full", "partial")
CONTROLLED_DATA = ("synthetic", "masked")
STATUSES = ("planned", "running", "passed", "failed")
REQUIRED_ROLES = ("coordinator", "operator", "communicator", "verifier")
REQUIRED_NOTIFICATIONS = ("start", "update", "end")
CHECK_KINDS = ("service", "data")
CHECK_RESULTS = ("passed", "failed", "pending")

KIND_LABELS = {
    "restore": "Restauration",
    "failover": "Bascule",
    "recovery": "Reprise après incident",
}

ROLE_LABELS = {
    "coordinator": "Coordinateur",
    "operator": "Opérateur",
    "communicator": "Communication",
    "verifier": "Vérification",
}

STATUS_LABELS = {
    "planned": "Planifié",
    "running": "En cours",
    "passed": "Réussi",
    "failed": "Échoué",
}

FILES = {
    "environments": ("environments.yaml", "environment.schema.json"),
    "scenarios": ("scenarios.yaml", "scenario.schema.json"),
    "communication": ("communication.yaml", "communication.schema.json"),
    "verification": ("verification.yaml", "verification.schema.json"),
}

ROOT_KEYS = {
    "environments": "environments",
    "scenarios": None,          # participants + scenarios
    "communication": None,      # channels + stakeholders + plan
    "verification": None,       # checks + signoffs
}

_DURATION_PATTERN = re.compile(r"^(0|([0-9]+(ms|s|m|h|d))+)$")
_TOKEN_PATTERN = re.compile(r"([0-9]+)(ms|s|m|h|d)")
_UNIT_MS = {"ms": 1, "s": 1000, "m": 60_000, "h": 3_600_000, "d": 86_400_000}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Trouve le dossier de schémas, même hors du dépôt."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_CRUCIBLE_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "environment.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Charge les quatre collections YAML du modèle Crucible."""
    base = Path(model_dir)
    model = {}
    for key, (filename, _) in FILES.items():
        path = base / filename
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        document = load_yaml(path)
        root_key = ROOT_KEYS[key]
        if root_key is None:
            model[key] = document
            continue
        if root_key not in document:
            raise ValueError(f"{path.name}: key '{root_key}' missing")
        model[key] = document[root_key] or []
    return model


def load_schema(key: str, schema_dir: str | Path | None = None) -> dict:
    filename = FILES[key][1]
    path = resolve_schema_dir(schema_dir) / filename
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    return load_yaml(path)


def parse_duration(value) -> int | None:
    """Convertit `0` ou une suite de `<nombre><ms|s|m|h|d>` en millisecondes."""
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
    """Formatte en durée réutilisable comme valeur de modèle (`1h30m`)."""
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


def env_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("environments", [])}


def participant_map(model: dict) -> dict:
    return {item["id"]: item for item in (model.get("scenarios") or {}).get("participants", [])}


def scenario_map(model: dict) -> dict:
    return {item["id"]: item for item in (model.get("scenarios") or {}).get("scenarios", [])}


def channel_map(model: dict) -> dict:
    return {item["id"]: item for item in (model.get("communication") or {}).get("channels", [])}


def stakeholder_map(model: dict) -> dict:
    return {
        item["id"]: item
        for item in (model.get("communication") or {}).get("stakeholders", [])
    }


def check_map(model: dict) -> dict:
    return {item["id"]: item for item in (model.get("verification") or {}).get("checks", [])}


def signoff_map(model: dict) -> dict:
    return {
        item["scenario"]: item
        for item in (model.get("verification") or {}).get("signoffs", [])
    }


def is_controlled(environment: dict | None) -> bool:
    """Un environnement contrôlé est isolé, non-productif et approuvé."""
    if not environment:
        return False
    return (
        environment.get("isolation") in CONTROLLED_ISOLATION
        and environment.get("data") in CONTROLLED_DATA
        and bool(environment.get("approved"))
    )


def controlled_first_evidence(model: dict, scenario: dict) -> dict | None:
    """Dernier exercice du même type réussi dans un environnement contrôlé."""
    envs = env_map(model)
    candidates = [
        item
        for item in (model.get("scenarios") or {}).get("scenarios", [])
        if item.get("kind") == scenario.get("kind")
        and item.get("status") == "passed"
        and is_controlled(envs.get(item.get("environment")))
    ]
    return max(candidates, key=lambda item: str(item.get("scheduled", ""))) if candidates else None


def checks_for_scenario(model: dict, scenario_id: str) -> list[dict]:
    return [
        item
        for item in (model.get("verification") or {}).get("checks", [])
        if item.get("scenario") == scenario_id
    ]


def assignment_for_role(scenario: dict, role: str) -> dict | None:
    for assignment in scenario.get("assignments", []):
        if assignment.get("role") == role:
            return assignment
    return None


def person_for_role(model: dict, scenario: dict, role: str) -> dict | None:
    assignment = assignment_for_role(scenario, role)
    if assignment is None:
        return None
    return participant_map(model).get(assignment.get("person"))


def scenario_duration(scenario: dict) -> int | None:
    return parse_duration(scenario.get("duration"))


def target_rto_ms(scenario: dict) -> int | None:
    return parse_duration(scenario.get("target_rto"))


def target_rpo_ms(scenario: dict) -> int | None:
    return parse_duration(scenario.get("target_rpo"))
