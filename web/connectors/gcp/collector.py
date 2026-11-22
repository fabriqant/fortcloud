"""Build an Atlas component proposal from read-only Google Cloud APIs.

The collector is deliberately SDK-agnostic: it accepts already-fetched iterables
for Compute Engine, Cloud SQL and Cloud Storage. The CLI fetches them with the
user's local ADC; tests pass simple dictionaries.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..common import as_dict, component, field

WEB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMPORT_FILE = WEB_ROOT / "workspaces" / "atlas" / "imports" / "components.yaml"


def _labels(value: Any) -> dict:
    data = as_dict(value)
    if isinstance(data, dict):
        return data
    try:
        return dict(value or {})
    except (TypeError, ValueError):
        return {}


def _owner(labels: dict) -> str:
    return str(labels.get("owner") or labels.get("Owner") or "")


def _environment(labels: dict) -> str:
    return str(labels.get("environment") or labels.get("Environment") or labels.get("env") or "")


def _region(zone: Any) -> str:
    if not zone:
        return "unknown"
    name = str(zone).rsplit("/", 1)[-1]
    return re.sub(r"-[a-z]$", "", name) or name


def build_document(
    project_id: str,
    instances: Any = None,
    sql_instances: Any = None,
    buckets: Any = None,
) -> dict:
    """Return an Atlas components document from Google Cloud resources."""
    components = []

    for item in instances or []:
        labels = _labels(field(item, "labels"))
        zone = field(item, "zone")
        name = str(field(item, "name", "instance"))
        components.append(
            component(
                identifier=f"gcp-compute-{project_id}-{name}",
                name=f"GCE {name}",
                category="processing",
                region=_region(zone),
                owner=_owner(labels),
                zones=[str(zone).rsplit("/", 1)[-1]] if zone else [],
                notes=f"Imported from Compute Engine {name}. Review criticality and backup evidence.",
                provider="gcp",
                environments=[_environment(labels)] if _environment(labels) else None,
            )
        )

    for item in sql_instances or []:
        name = str(field(item, "name", "database"))
        components.append(
            component(
                identifier=f"gcp-sql-{project_id}-{name}",
                name=f"Cloud SQL {name}",
                category="storage",
                region=str(field(item, "region") or "unknown"),
                owner="unassigned",
                notes=(
                    f"Imported from Cloud SQL {name}. Confirm HA, replication and restore evidence "
                    "manually."
                ),
                provider="gcp",
            )
        )

    for item in buckets or []:
        name = str(field(item, "name", "bucket"))
        labels = _labels(field(item, "labels"))
        components.append(
            component(
                identifier=f"gcp-storage-{project_id}-{name}",
                name=f"Cloud Storage {name}",
                category="storage",
                region=str(field(item, "location") or "unknown"),
                owner=_owner(labels),
                notes=f"Imported from Cloud Storage {name}. Add replication and backup details manually.",
                provider="gcp",
                environments=[_environment(labels)] if _environment(labels) else None,
            )
        )

    return {"version": 1, "components": components}
