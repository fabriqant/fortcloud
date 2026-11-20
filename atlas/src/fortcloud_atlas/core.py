"""Modèle de données et règles partagées de Fortcloud Atlas."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_atlas/core.py -> parents[2] est la racine du dépôt.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

TEST_MAX_AGE_DAYS = 90

FILES = {
    "components": ("components.yaml", "component.schema.json"),
    "dependencies": ("dependencies.yaml", "dependency.schema.json"),
    "flows": ("flows.yaml", "flow.schema.json"),
    "risks": ("risks.yaml", "risk.schema.json"),
}

CATEGORY_LABELS = {
    "storage": "Stockage",
    "processing": "Traitements",
    "orchestration": "Orchestrateur",
    "network": "Réseau",
    "identity": "Identités",
    "external_service": "Service externe",
}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Trouve le dossier de schémas, même quand l'outil est installé hors du dépôt."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_ATLAS_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "component.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Charge les quatre collections YAML du modèle."""
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


def risk_score(risk: dict) -> int:
    return risk["likelihood"] * risk["impact"]


def severity(score: int) -> str:
    if score >= 15:
        return "critique"
    if score >= 8:
        return "élevé"
    if score >= 4:
        return "modéré"
    return "faible"


def is_spof(component: dict) -> bool:
    """Un composant en instance unique est un point de défaillance unique."""
    return component["redundancy"]["instances"] == 1


def is_single_region_p0(component: dict) -> bool:
    """Un composant P0 sur une seule région reste vulnérable à une panne régionale."""
    return component["criticality"] == "P0" and len(component["regions"]) < 2


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def test_age_days(value, today: date | None = None):
    tested = parse_date(value)
    if tested is None:
        return None
    return ((today or date.today()) - tested).days
