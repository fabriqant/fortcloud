"""Local reference-value catalog used by the guided forms.

The catalog holds reusable metadata such as owners, regions and providers. It is
separate from the model files: tools still own their YAML, while the console
offers suggestions that users may accept or override.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "catalog.sqlite3"

CATEGORIES = ("owners", "teams", "regions", "zones", "providers", "environments", "services")

DEFAULTS: dict[str, tuple[str, ...]] = {
    "owners": (
        "platform",
        "sec-team",
        "net-team",
        "payments-team",
        "commerce-team",
        "data-platform",
        "catalog-team",
        "analytics-team",
        "inventory-team",
        "pricing-team",
        "search-team",
    ),
    "teams": (
        "sec-team",
        "net-team",
        "payments-team",
        "commerce-team",
        "data-platform",
        "catalog-team",
        "analytics-team",
        "platform",
        "comms-team",
    ),
    "regions": (
        "global",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-central-1",
        "europe-west1",
        "us-east-1",
        "on-prem DC1",
    ),
    "zones": (
        "az1",
        "az2",
        "az3",
        "eu-west-3a",
        "eu-west-3b",
        "eu-west-3c",
        "on-prem DC1",
        "global",
    ),
    "providers": (
        "aws",
        "gcp",
        "azure",
        "on-prem DC1",
        "single SaaS",
        "single DNS provider",
        "SaaS",
        "hybrid Kubernetes",
        "third party (SaaS)",
        "multi-cloud (S3 + GCS)",
        "Git SaaS",
    ),
    "environments": ("prod", "staging", "sandbox", "dev", "dr", "on-prem"),
    "services": (
        "checkout",
        "identity-auth",
        "catalog-browse",
        "checkout-reporting",
        "reporting",
        "dns",
        "event-bus",
        "data-lake",
        "observability",
    ),
}


def _connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def ensure_catalog() -> None:
    """Create the local database and seed it with the default values once."""
    with _connection() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS reference_values ("
            "category TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY (category, value))"
        )
        for category, values in DEFAULTS.items():
            connection.executemany(
                "INSERT OR IGNORE INTO reference_values (category, value) VALUES (?, ?)",
                [(category, value) for value in values],
            )


def _check_category(category: str) -> None:
    if category not in CATEGORIES:
        raise ValueError(f"Unknown catalog category: {category}")


def _clean(value: str) -> str:
    result = value.strip()
    if not result or len(result) > 120:
        raise ValueError("A catalog value must contain between 1 and 120 characters")
    return result


def list_values() -> dict[str, list[str]]:
    """Return all categories, including the default values and user edits."""
    ensure_catalog()
    catalog = {category: [] for category in CATEGORIES}
    with _connection() as connection:
        rows = connection.execute(
            "SELECT category, value FROM reference_values ORDER BY category, value"
        ).fetchall()
    for category, value in rows:
        if category in catalog:
            catalog[category].append(value)
    return catalog


def add_value(category: str, value: str) -> bool:
    """Add a value. Return False when it already exists."""
    _check_category(category)
    cleaned = _clean(value)
    ensure_catalog()
    with _connection() as connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO reference_values (category, value) VALUES (?, ?)",
            (category, cleaned),
        )
    return cursor.rowcount == 1


def rename_value(category: str, value: str, new_value: str) -> bool:
    """Rename a value. Return False when the old value does not exist."""
    _check_category(category)
    old = _clean(value)
    new = _clean(new_value)
    if old == new:
        return True
    ensure_catalog()
    with _connection() as connection:
        cursor = connection.execute(
            "UPDATE OR IGNORE reference_values SET value = ? WHERE category = ? AND value = ?",
            (new, category, old),
        )
        if cursor.rowcount:
            connection.execute(
                "DELETE FROM reference_values WHERE category = ? AND value = ?",
                (category, old),
            )
    return cursor.rowcount == 1


def remove_value(category: str, value: str) -> bool:
    """Remove a value. Return False when it does not exist."""
    _check_category(category)
    cleaned = _clean(value)
    ensure_catalog()
    with _connection() as connection:
        cursor = connection.execute(
            "DELETE FROM reference_values WHERE category = ? AND value = ?",
            (category, cleaned),
        )
    return cursor.rowcount == 1
