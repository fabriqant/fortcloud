"""Data model and analysis helpers for Fortcloud Custodian."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import yaml

# src/fortcloud_custodian/core.py -> parents[2] is the tool's root folder.
ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = ROOT / "examples" / "hybrid-multicloud" / "model"
DEFAULT_OUTPUT = ROOT / "docs" / "generated"

RESTRICTED = "restricted"

MAX_PERMISSIONS = 8
MAX_TIME_BOUND_DAYS = 365
MAX_ROTATION_DAYS = 90
MAX_EVIDENCE_AGE_DAYS = 90
MIN_RETENTION_DAYS = 365
MIN_PROD_APPROVERS = 2

ELEVATED_ROLES = ("admin", "owner", "root", "superuser")
REQUIRED_AUDIT_KINDS = ("grant_change", "secret_access", "deploy", "pipeline_change")
REQUIRED_TESTS = ("unit", "integration")

CLASSIFICATION_LABELS = {
    "public": "Public",
    "internal": "Internal",
    "confidential": "Confidential",
    "restricted": "Restricted",
}

PRINCIPAL_LABELS = {
    "human": "Human",
    "service": "Service",
    "ci": "CI",
}

STORE_LABELS = {
    "vault": "Vault",
    "aws-secrets-manager": "AWS Secrets Manager",
    "azure-key-vault": "Azure Key Vault",
    "gcp-secret-manager": "GCP Secret Manager",
    "k8s-secret": "Kubernetes Secret",
}

KIND_LABELS = {
    "grant_change": "Access change",
    "secret_access": "Secret read",
    "deploy": "Deployment",
    "pipeline_change": "Pipeline change",
    "infra_change": "Infrastructure change",
}

FILES = {
    "access": ("access.yaml", "access.schema.json"),
    "secrets": ("secrets.yaml", "secret.schema.json"),
    "changes": ("changes.yaml", "change.schema.json"),
    "audit": ("audit.yaml", "audit.schema.json"),
}

# YAML root key holding the collection of each model file.
ROOT_KEYS = {
    "access": None,      # the whole document (environments, principals, grants)
    "secrets": "secrets",
    "changes": "pipelines",
    "audit": None,       # the whole document (sinks, operations)
}


def resolve_schema_dir(explicit: str | Path | None = None) -> Path:
    """Find the schema directory, even outside the repository."""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get("FORTCLOUD_CUSTODIAN_SCHEMA_DIR")
    if env_value:
        return Path(env_value)
    candidates = [
        Path.cwd() / "schema",
        ROOT / "schema",
        Path(__file__).resolve().parent / "schema",
    ]
    for candidate in candidates:
        if (candidate / "access.schema.json").exists():
            return candidate
    return candidates[-1]


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_model(model_dir: str | Path = DEFAULT_MODEL) -> dict:
    """Load the four YAML collections of the Custodian model."""
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


def days_until(value, today: date | None = None):
    dated = parse_date(value)
    if dated is None:
        return None
    return (dated - (today or date.today())).days


def env_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("access", {}).get("environments", [])}


def principal_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("access", {}).get("principals", [])}


def grant_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("access", {}).get("grants", [])}


def secret_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("secrets", [])}


def pipeline_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("changes", [])}


def sink_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("audit", {}).get("sinks", [])}


def operation_map(model: dict) -> dict:
    return {item["id"]: item for item in model.get("audit", {}).get("operations", [])}


def is_restricted(model: dict, environment: str | None) -> bool:
    environment_info = env_map(model).get(environment or "")
    return bool(environment_info and environment_info.get("classification") == RESTRICTED)


def is_elevated(role: str | None) -> bool:
    return str(role or "").lower() in ELEVATED_ROLES


def is_wildcard(permission: str | None) -> bool:
    return "*" in str(permission or "")


def crosses_environment(resource: str, environment: str, other_environments) -> bool:
    """True if an explicit resource targets another declared environment."""
    text = str(resource)
    for other in other_environments:
        if other == environment:
            continue
        pattern = rf"(?<![a-z0-9-]){re.escape(other)}(?![a-z0-9-])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def grants_for_principal(model: dict, principal_id: str) -> list[dict]:
    return [
        item
        for item in model.get("access", {}).get("grants", [])
        if item.get("principal") == principal_id
    ]


def grants_for_environment(model: dict, environment: str) -> list[dict]:
    return [
        item
        for item in model.get("access", {}).get("grants", [])
        if item.get("environment") == environment
    ]


def secrets_for_environment(model: dict, environment: str) -> list[dict]:
    return [
        item
        for item in model.get("secrets", [])
        if environment in item.get("environments", [])
    ]


def pipelines_for_environment(model: dict, environment: str) -> list[dict]:
    return [
        item for item in model.get("changes", []) if item.get("environment") == environment
    ]


def operations_for_kind(model: dict, kind: str) -> list[dict]:
    return [
        item
        for item in model.get("audit", {}).get("operations", [])
        if item.get("kind") == kind and item.get("logged")
    ]


def secret_age_days(secret: dict, today: date | None = None):
    return age_days(secret.get("last_rotated"), today)


def rollback_age_days(pipeline: dict, today: date | None = None):
    return age_days((pipeline.get("rollback") or {}).get("verified"), today)


def evidence_age_days(operation: dict, today: date | None = None):
    return age_days(operation.get("last_evidence"), today)
