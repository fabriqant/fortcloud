# Fortcloud Ark — Backup Coverage

> Generated on 2026-11-21 by `fortcloud-ark coverage`. Do not edit by hand.

## Summary

- **8** data assets
- **8** backup policies
- **7** restore tests
- **4** business services
- **3/4** P0 assets fully proven
- **4** assets at risk

**PROVEN** means the asset has a backup policy and at least one recent,
successful restore test compatible with the service targets. See the
[recovery plan](recovery-plan.md) for the gaps.

## Assets

| Asset | Crit. | Backup | Type / Schedule | Retention | Immutable | Cross-region | Last backup | Last restore | RTO / RPO | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `idp-db` — Identity database | P0 | `bk-idp` | cdc / 0 | 30 d | yes | yes | 1 d | 19 d (passed) | 15m / 0 | PROVEN |
| `obj-lake` — Object data lake | P0 | `bk-lake` | incremental / 1h | 90 d | yes | yes | 2 d | 27 d (passed) | 4h / 1h | PROVEN |
| `pg-core` — Primary transactional database | P0 | `bk-pg` | cdc / 5m | 35 d | yes | yes | 1 d | 13 d (passed) | 30m / 5m | PROVEN |
| `vault-secrets` — Secrets vault | P0 | `bk-vault` | cdc / 0 | 30 d | yes | yes | **3 d (stale)** | **129 d (stale)** (passed) | 15m / 0 | AT RISK |
| `config-repo` — GitOps configuration repository | P1 | `bk-config` | snapshot / 24h | 30 d | yes | no | 1 d | 32 d (partial) | 8h / 1d | AT RISK |
| `kafka-events` — Event queue | P1 | `bk-kafka` | incremental / 1h | 7 d | **no** | no | 1 d | 22 d (passed) | 4h / 1h | PROVEN |
| `logs-archive` — Audit log archive | P2 | `bk-logs` | snapshot / 24h | 365 d | yes | no | 1 d | **none** | 8h / 1d | AT RISK |
| `report-exports` — Reporting exports | P2 | `bk-exports` | snapshot / 24h | 7 d | **no** | no | **6 d (stale)** | **none** | 8h / 1d | AT RISK |

## Links

- [Restore evidence](restore-evidence.md)
- [Recovery plan](recovery-plan.md)
- [Machine-readable status](restore-status.json)
