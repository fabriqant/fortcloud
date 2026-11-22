"""Shared helpers for local, read-only inventory connectors.

Connectors never authenticate to the console. They run next to the user's cloud
CLI configuration and only return a *proposal* that the Import tab reviews.
"""

from __future__ import annotations

import re
from typing import Any


def as_dict(value: Any) -> dict:
    """Normalise SDK models, mappings and simple objects to a plain dict."""
    if isinstance(value, dict):
        return value
    as_dict_method = getattr(value, "as_dict", None)
    if callable(as_dict_method):
        return as_dict_method()
    if hasattr(value, "__dict__"):
        return vars(value)
    return {}


def slug(value: Any) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")[:60]
    return result or "resource"


def field(value: Any, key: str, default: Any = "") -> Any:
    data = as_dict(value)
    if key in data:
        return data[key]
    return getattr(value, key, default) if value is not None else default


def tag(tags: Any, key: str, default: str = "") -> str:
    if isinstance(tags, dict):
        for name, value in tags.items():
            if str(name).lower() == key.lower():
                return str(value or default)
        return default
    for entry in tags or []:
        data = as_dict(entry)
        name = data.get("Key", data.get("key"))
        if str(name).lower() == key.lower():
            return str(data.get("Value", data.get("value")) or default)
    return default


def component(
    identifier: str,
    name: str,
    category: str,
    region: str,
    owner: str,
    zones: list[str] | None = None,
    instances: int = 1,
    replication: str = "none",
    notes: str = "",
    provider: str = "aws",
    environments: list[str] | None = None,
) -> dict:
    """Build one Atlas component with explicit, reviewable defaults."""
    result = {
        "id": slug(identifier),
        "name": str(name)[:120] or identifier,
        "category": category,
        "criticality": "P1",
        "owner": owner or "unassigned",
        "provider": provider,
        "regions": [region] if region else [],
        "zones": [zone for zone in (zones or []) if zone],
        "redundancy": {
            "instances": max(1, instances),
            "active_passive": instances > 1,
            "replication": replication,
        },
        "backup": {"enabled": False, "immutable": False, "retention_days": 0},
    }
    if environments:
        result["environments"] = list(environments)
    if notes:
        result["notes"] = notes
    return result
