"""Build an Atlas component proposal from read-only Azure Resource Manager data.

The collector accepts any object exposing ``resources.list()`` (the Azure
ResourceManagementClient, or a test fake). It never writes secrets and never
modifies a model directly: the console Import tab reviews the proposal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..common import as_dict, component, tag

WEB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMPORT_FILE = WEB_ROOT / "workspaces" / "atlas" / "imports" / "components.yaml"

_KINDS = (
    ("microsoft.compute/virtualmachines", "processing", "Azure VM"),
    ("microsoft.containerservice/managedclusters", "orchestration", "Azure Kubernetes Service"),
    ("microsoft.sql/servers/databases", "storage", "Azure SQL database"),
    ("microsoft.dbforpostgresql/servers", "storage", "Azure Database for PostgreSQL"),
    ("microsoft.dbformysql/servers", "storage", "Azure Database for MySQL"),
    ("microsoft.storage/storageaccounts", "storage", "Azure Storage account"),
)


def _kind(resource_type: str) -> tuple[str, str] | None:
    lowered = resource_type.lower()
    for prefix, category, label in _KINDS:
        if lowered == prefix or lowered.startswith(prefix + "/"):
            return category, label
    return None


def _zones(resource: dict) -> list[str]:
    return [str(zone) for zone in (resource.get("zones") or []) if zone]


def build_document(resource_client: Any, subscription_id: str = "") -> dict:
    """Return an Atlas components document from an Azure resource client."""
    components = []
    resources = resource_client.resources.list()
    for item in resources:
        data = as_dict(item)
        mapped = _kind(str(data.get("type", "")))
        if not mapped:
            continue
        category, label = mapped
        name = str(data.get("name", "resource"))
        resource_id = str(data.get("id") or name)
        tags = data.get("tags")
        environment = tag(tags, "environment") or tag(tags, "Environment")
        environment_tag = tag(tags, "env")
        components.append(
            component(
                identifier=f"azure-{data.get('type', 'resource')}-{resource_id}",
                name=f"{label} {name}",
                category=category,
                region=str(data.get("location") or "unknown"),
                owner=tag(tags, "owner") or tag(tags, "Owner"),
                zones=_zones(data),
                notes=(
                    f"Imported from Azure {data.get('type', 'resource')} {name}. "
                    "Review criticality, redundancy and backup evidence."
                ),
                provider="azure",
                environments=[environment or environment_tag] if (environment or environment_tag) else None,
            )
        )
    return {"version": 1, "components": components}
