# Fortcloud Crucible — Verification Report

> Generated on 2026-11-21 by `fortcloud-crucible verification`. Do not edit by hand.

A completed exercise is only credible when both the service and the
data were checked, with evidence and an approved verifier sign-off.

## Checks

| Check | Scenario | Kind | Metric | Expected | Result | Status |
|---|---|---|---|---|---|---|
| `chk-failover-data` | `ex-failover-staging` | data | session_count | `equal` | passed | OK |
| `chk-failover-service` | `ex-failover-staging` | service | auth_success_rate | `100%` | passed | OK |
| `chk-recovery-data` | `ex-recovery-sandbox` | data | export_checksum | `match` | passed | AT RISK |
| `chk-recovery-service` | `ex-recovery-sandbox` | service | dashboard_freshness | `5m` | passed | OK |
| `chk-restore-data` | `ex-restore-sandbox` | data | order_count_after_restore | `equal` | passed | OK |
| `chk-restore-service` | `ex-restore-sandbox` | service | http_5xx_rate | `0` | passed | OK |

## Sign-offs

| Scenario | Verifier | Role | Date | Decision | Status |
|---|---|---|---|---|---|
| `ex-failover-staging` | `dave` | verifier | 2026-11-26 | approved | OK |
| `ex-recovery-sandbox` | `erin` | verifier | 2026-11-27 | approved | OK |
| `ex-restore-sandbox` | `dave` | verifier | 2026-11-24 | approved | AT RISK |

## Exercise verdicts

- `ex-failover-prod` — Planifié: PENDING.
- `ex-failover-staging` — Réussi: VERIFIED.
- `ex-recovery-prod` — Planifié: PENDING.
- `ex-recovery-sandbox` — Réussi: PENDING.
- `ex-restore-prod` — Échoué: PENDING.
- `ex-restore-sandbox` — Réussi: VERIFIED.
