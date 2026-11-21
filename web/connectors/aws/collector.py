"""Build an Atlas component proposal from a read-only AWS session.

The collector never writes secrets and never modifies a model directly. It returns
a document that the console shows as a proposal in the Import tab.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

WEB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMPORT_FILE = WEB_ROOT / "workspaces" / "atlas" / "imports" / "components.yaml"


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60]
    return result or "resource"


def _tag(tags: list[dict] | None, key: str, default: str = "") -> str:
    for tag in tags or []:
        if tag.get("Key") == key:
            return str(tag.get("Value") or default)
    return default


def _pages(client: Any, method: str, result_key: str, **kwargs: Any) -> list[dict]:
    paginator = client.get_paginator(method)
    items: list[dict] = []
    for page in paginator.paginate(**kwargs):
        items.extend(page.get(result_key, []))
    return items


def _component(
    identifier: str,
    name: str,
    category: str,
    region: str,
    owner: str,
    zones: list[str] | None = None,
    instances: int = 1,
    replication: str = "none",
    notes: str = "",
) -> dict:
    component = {
        "id": _slug(identifier),
        "name": name[:120] or identifier,
        "category": category,
        "criticality": "P1",
        "owner": owner or "unassigned",
        "provider": "aws",
        "regions": [region],
        "zones": [zone for zone in (zones or []) if zone],
        "redundancy": {
            "instances": max(1, instances),
            "active_passive": instances > 1,
            "replication": replication,
        },
        "backup": {"enabled": False, "immutable": False, "retention_days": 0},
    }
    if notes:
        component["notes"] = notes
    return component


def _ec2_components(client: Any, region: str) -> list[dict]:
    components = []
    reservations = _pages(client, "describe_instances", "Reservations")
    for reservation in reservations:
        for instance in reservation.get("Instances", []):
            instance_id = instance.get("InstanceId", "unknown")
            tags = instance.get("Tags")
            name = _tag(tags, "Name", instance_id)
            owner = _tag(tags, "owner", _tag(tags, "Owner"))
            zone = (instance.get("Placement") or {}).get("AvailabilityZone", "")
            components.append(
                _component(
                    identifier=f"ec2-{name}-{instance_id}",
                    name=f"EC2 {name}",
                    category="processing",
                    region=region,
                    owner=owner,
                    zones=[zone],
                    notes=f"Imported from EC2 {instance_id}. Review criticality and backup evidence.",
                )
            )
    return components


def _rds_components(client: Any, region: str) -> list[dict]:
    components = []
    for database in _pages(client, "describe_db_instances", "DBInstances"):
        identifier = database.get("DBInstanceIdentifier", "unknown")
        tags = database.get("TagList")
        components.append(
            _component(
                identifier=f"rds-{identifier}",
                name=f"RDS {identifier}",
                category="storage",
                region=region,
                owner=_tag(tags, "owner", _tag(tags, "Owner")),
                zones=[database.get("AvailabilityZone", "")],
                instances=2 if database.get("MultiAZ") else 1,
                replication="sync" if database.get("MultiAZ") else "none",
                notes=f"Imported from RDS {identifier}. Confirm the backup and restore evidence.",
            )
        )
    return components


def _s3_components(client: Any, region: str) -> list[dict]:
    components = []
    for bucket in _pages(client, "list_buckets", "Buckets"):
        name = bucket.get("Name", "unknown")
        components.append(
            _component(
                identifier=f"s3-{name}",
                name=f"S3 {name}",
                category="storage",
                region=region,
                owner="unassigned",
                notes=f"Imported from S3 {name}. Add replication and backup details manually.",
            )
        )
    return components


def build_document(session: Any, region: str) -> dict:
    """Return an Atlas components document from a read-only AWS session."""
    components = []
    components.extend(_ec2_components(session.client("ec2", region_name=region), region))
    components.extend(_rds_components(session.client("rds", region_name=region), region))
    components.extend(_s3_components(session.client("s3", region_name=region), region))
    return {"version": 1, "components": components}
