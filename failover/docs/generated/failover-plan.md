# Fortcloud Failover — Remediation Plan

> Generated on 2026-11-21 by `fortcloud-failover plan`. Do not edit by hand.

Ordered by service criticality, then by tightest RTO. Each gap below comes
from a deterministic rule in `validate.py`; fix the model, not this file.

## fo-dns — `dns-global` → `dns-global-dr`

- **Owner:** net-team
- **Services:** `identity-auth`, `order-to-cash`
- **Mode:** Actif/actif
- **Replication:** stateless
- **Status:** COVERED

No gap detected. Keep the drill cadence and review the runbook after
every topology change.

## fo-idp — `idp-oidc` → `idp-oidc-dr`

- **Owner:** sec-team
- **Services:** `identity-auth`, `order-to-cash`
- **Mode:** Actif/passif
- **Replication:** stateless
- **Status:** AT RISK

**Gaps:**

- both instances use the same provider 'SaaS unique'.

**Steps:**

1. Fix: Both instances use the same provider 'SaaS unique'. Owner: sec-team.
2. Re-run `fortcloud-failover check --strict` and attach `failover-status.json` to the pull request.

## fo-vault — `vault-secrets` → `vault-secrets-dr`

- **Owner:** sec-team
- **Services:** `identity-auth`, `order-to-cash`
- **Mode:** Actif/passif
- **Replication:** sync
- **Status:** AT RISK

**Gaps:**

- both instances use the same provider 'SaaS'.
- drill drill-vault is 129 days old (max 90).

**Steps:**

1. Fix: Both instances use the same provider 'SaaS'. Owner: sec-team.
2. Fix: Drill drill-vault is 129 days old (max 90). Owner: sec-team.
3. Re-run `fortcloud-failover check --strict` and attach `failover-status.json` to the pull request.

## fo-pg — `pg-core` → `pg-core-dr`

- **Owner:** data-platform
- **Services:** `order-to-cash`
- **Mode:** Actif/passif
- **Replication:** async
- **Status:** AT RISK

**Gaps:**

- standby capacity 50 is lower than primary capacity 100.
- DNS TTL 45m exceeds RTO 30m.
- switchover is manual for a P0 service.
- drill drill-pg result is 'partial'.

**Steps:**

1. Fix: Standby capacity 50 is lower than primary capacity 100. Owner: data-platform.
2. Fix: DNS TTL 45m exceeds RTO 30m. Owner: data-platform.
3. Fix: Switchover is manual for a P0 service. Owner: data-platform.
4. Fix: Drill drill-pg result is 'partial'. Owner: data-platform.
5. Re-run `fortcloud-failover check --strict` and attach `failover-status.json` to the pull request.

## Definition of done

- Every P0 component in a service has a strategy with a standby in another region.
- `detection_time + promotion_time` is below the tightest RTO.
- Replication is compatible with the declared RPO.
- A drill younger than 90 days has `result: passed` and an evidence link.
- `fortcloud-failover check --strict` exits with code 0.
