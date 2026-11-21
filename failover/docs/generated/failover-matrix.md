# Fortcloud Failover — Coverage Matrix

> Generated on 2026-11-21 by `fortcloud-failover matrix`. Do not edit by hand.

## Summary

- **10** components in the topology
- **3** business services
- **4** failover strategies
- **8/8** P0 components covered by a strategy
- **3** strategies at risk
- **4** recorded drills

A strategy is **COVERED** when no drift check fires. **AT RISK** means at
least one gap must be fixed; see the [remediation plan](failover-plan.md).

## Strategies

| Strategy | Primary → Standby | Mode | Regions | Replication | Switchover / RTO | Last drill | Status |
|---|---|---|---|---|---|---|---|
| `fo-dns` | `dns-global` → `dns-global-dr` | Active/active | global-a / global-b | stateless | 6m / 15m | 24 d | COVERED |
| `fo-idp` | `idp-oidc` → `idp-oidc-dr` | Active/passive | eu-west-1 / eu-west-3 | stateless | 2m30s / 15m | 16 d | AT RISK |
| `fo-pg` | `pg-core` → `pg-core-dr` | Active/passive | eu-west-1 / eu-west-3 | async | 26m / 30m | 40 d (partial) | AT RISK |
| `fo-vault` | `vault-secrets` → `vault-secrets-dr` | Active/passive | eu-west-1 / eu-west-3 | sync | 11m / 15m | **129 d (stale)** | AT RISK |

## Services and their protection

| Service | Criticality | RTO | RPO | Owner | P0 coverage |
|---|---|---|---|---|---|
| `identity-auth` — User authentication | P0 | 15m | 0 | sec-team | `idp-oidc` → fo-idp; `dns-global` → fo-dns; `vault-secrets` → fo-vault |
| `order-to-cash` — Order to cash | P0 | 30m | 5m | commerce-team | `pg-core` → fo-pg; `dns-global` → fo-dns; `idp-oidc` → fo-idp; `vault-secrets` → fo-vault |
| `analytics-ingestion` — Analytics ingestion | P1 | 4h | 1h | data-platform | no P0 component |

## Links

- [Remediation plan](failover-plan.md)
- [Drill scenarios](drill-scenarios.md)
- [Machine-readable status](failover-status.json)
