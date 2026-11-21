# Fortcloud Crucible — Scenario Plan

> Generated on 2026-11-21 by `fortcloud-crucible scenarios`. Do not edit by hand.

Failure drills always start in a controlled environment: isolated,
non-production data and approved. Production needs a passed rehearsal
of the same kind first.

| Scenario | Kind | System | Env | Controlled | Scheduled | Status | RTO | RPO | Window | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `ex-failover-prod` — Bascule du service d'identité en production | Bascule | `identity-auth` | `prod` | no | 2026-10-15 | Planifié | 15m | 0 | 1h | AT RISK |
| `ex-failover-staging` — Bascule du service d'identité | Bascule | `identity-auth` | `staging` | yes | 2026-11-26 | Réussi | 15m | 0 | 1h | OK |
| `ex-recovery-prod` — Reprise du reporting en production | Reprise après incident | `reporting` | `prod` | no | 2026-11-30 | Planifié | 1h | 15m | 2h | OK |
| `ex-recovery-sandbox` — Reprise du reporting analytique | Reprise après incident | `reporting` | `sandbox` | yes | 2026-11-27 | Réussi | 1h | 15m | 6h | AT RISK |
| `ex-restore-prod` — Restauration de l'API commande en production | Restauration | `checkout` | `prod` | no | 2026-11-20 | Échoué | 30m | 5m | 2h | AT RISK |
| `ex-restore-sandbox` — Restauration de l'API commande | Restauration | `checkout` | `sandbox` | yes | 2026-11-25 | Réussi | 30m | 5m | 2h | OK |

## `ex-failover-prod`

- **Owner:** sec-team
- **Environment:** `prod`
- **Gap:** scheduled 37 days ago and still 'planned'.

## `ex-recovery-sandbox`

- **Owner:** analytics-team
- **Environment:** `sandbox`
- **Gap:** exercise window 6h exceeds 4h.

## `ex-restore-prod`

- **Owner:** platform-team
- **Environment:** `prod`
- **Gap:** exercise failed — schedule a retest and record the finding.

## Links

- [Who does what](roles-matrix.md)
- [Communication](communication-plan.md)
- [Verification](verification-report.md)
- [Machine-readable status](crucible-status.json)
