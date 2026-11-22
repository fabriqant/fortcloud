"""Local reference-value catalog used by the guided forms.

The catalog holds reusable metadata such as owners, regions and providers. It is
separate from the model files: tools still own their YAML, while the console
offers suggestions that users may accept or override.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "catalog.sqlite3"

CATEGORIES = (
    "owners",
    "teams",
    "people",
    "services",
    "components",
    "pairs",
    "providers",
    "regions",
    "zones",
    "environments",
    "roles",
    "audiences",
    "strategies",
    "scenarios",
    "channels",
    "stakeholders",
    "assets",
    "backups",
    "restores",
    "dependencies",
    "flows",
    "risks",
    "checks",
    "objectives",
    "signals",
    "sinks",
    "metrics",
    "operations",
    "pipelines",
    "secrets",
    "principals",
    "permissions",
    "runbooks",
    "drills",
    "participants",
    "signoffs",
    "assignments",
    "actions",
)

DEFAULTS: dict[str, tuple[str, ...]] = {
    "owners": (
        "platform",
        "platform-team",
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
        "communications",
        "dave",
        "erin",
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
        "platform-team",
        "comms-team",
        "communications",
        "sre",
    ),
    "people": ("Alice Martin", "Bernard Lefevre", "Carole Ndiaye", "David Chen", "Erin Novak"),
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
    "components": (
        "dns",
        "dns-global",
        "dns-global-dr",
        "idp",
        "idp-oidc",
        "idp-oidc-dr",
        "pg",
        "pg-core",
        "pg-core-dr",
        "vault",
        "vault-secrets",
        "vault-secrets-dr",
        "checkout",
        "catalog-browse",
        "network-hub",
    ),
    "pairs": ("dns", "idp", "pg", "vault", "checkout", "identity-auth"),
    "providers": (
        "aws",
        "gcp",
        "azure",
        "on-prem DC1",
        "single SaaS",
        "single DNS provider",
        "SaaS",
        "DNS provider A",
        "DNS provider B",
        "Git SaaS",
        "Git mirror",
        "hybrid Kubernetes",
        "multi-cloud (S3 + GCS)",
        "multi-cloud replication",
        "cloud-native PITR",
        "cold object storage",
        "third party (SaaS)",
    ),
    "regions": (
        "global",
        "global-a",
        "global-b",
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
        "anycast",
        "eu-west-3a",
        "eu-west-3b",
        "eu-west-3c",
        "on-prem DC1",
        "global",
    ),
    "environments": ("prod", "staging", "sandbox", "dev", "dr", "on-prem"),
    "roles": (
        "primary",
        "standby",
        "standalone",
        "owner",
        "approver",
        "communicator",
        "coordinator",
        "observer",
        "operator",
        "verifier",
        "admin",
        "deployer",
        "developer",
        "runtime",
        "viewer",
    ),
    "audiences": ("internal", "external"),
    "strategies": (
        "fo-dns",
        "fo-idp",
        "fo-pg",
        "fo-vault",
        "multi-AZ with async replication",
        "backup IdP federation",
        "event replay with reconciliation",
    ),
    "scenarios": (
        "primary-loss",
        "region-loss",
        "network-partition",
        "idp-outage",
        "dns-failover",
        "manual",
        "deletion",
        "point_in_time",
        "ransomware",
        "ex-failover-staging",
        "ex-recovery-sandbox",
        "ex-restore-sandbox",
    ),
    "channels": ("exec-bridge", "war-room", "slack", "email", "pager", "siem"),
    "stakeholders": (
        "sec-team",
        "net-team",
        "payments-team",
        "comms-team",
        "platform",
        "customer-support",
    ),
    "assets": (
        "pg-core",
        "idp-db",
        "kafka-events",
        "obj-lake",
        "logs-archive",
        "config-repo",
        "vault-secrets",
        "report-exports",
    ),
    "backups": ("bk-config", "bk-idp", "bk-kafka", "bk-lake", "bk-pg", "bk-vault"),
    "restores": ("restore-pg-core", "restore-vault", "restore-lake", "restore-checkout-prod"),
    "dependencies": (
        "dep-audit",
        "dep-auth",
        "dep-catalog",
        "dep-inventory",
        "dep-payment",
        "dep-pricing",
        "dep-search",
    ),
    "flows": ("checkout-payment", "identity-sso", "catalog-search", "analytics-export"),
    "risks": tuple(f"R-{index:03d}" for index in range(1, 9)),
    "checks": (
        "chk-auth-avail",
        "chk-auth-completeness",
        "chk-catalog-avail",
        "chk-checkout-avail",
        "chk-checkout-freshness",
        "chk-failover-service",
        "chk-recovery-data",
        "chk-restore-service",
    ),
    "objectives": (
        "slo-auth-avail",
        "slo-auth-completeness",
        "slo-catalog-avail",
        "slo-checkout-avail",
        "slo-checkout-freshness",
        "slo-reporting-validity",
    ),
    "signals": (
        "sig-auth-availability",
        "sig-auth-completeness",
        "sig-catalog-availability",
        "sig-checkout-availability",
        "sig-checkout-freshness",
        "sig-reporting-validity",
    ),
    "sinks": ("sink-archive", "sink-siem"),
    "metrics": (
        "auth_success_rate",
        "dashboard_freshness",
        "export_checksum",
        "http_5xx_rate",
        "order_count_after_restore",
        "session_count",
    ),
    "operations": ("read", "write"),
    "pipelines": ("ci-deploy", "ci-staging", "ci-legacy"),
    "secrets": ("sec-checkout-api-key", "sec-analytics-export", "sec-ci-deploy-token"),
    "principals": ("alice", "ci-deploy", "ci-legacy", "ci-staging", "svc-checkout", "svc-reporting"),
    "permissions": ("read", "write", "admin", "deploy", "approve"),
    "runbooks": (
        "docs/templates/drill.md",
        "docs/templates/check.md",
        "docs/runbooks/failover.md",
    ),
    "drills": ("fo-drill-q1", "restore-drill-q2", "region-loss-drill"),
    "participants": ("alice", "bob", "carol", "dave", "erin"),
    "signoffs": ("alice", "bob", "carol"),
    "assignments": ("sec-team", "net-team", "platform", "payments-team"),
    "actions": (
        "Deploy a second anycast DNS provider",
        "Duplicate the hub and enable redundant BGP",
        "Federate a backup IdP",
        "Automate quarterly restore tests",
        "Replicate to a secondary region",
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
