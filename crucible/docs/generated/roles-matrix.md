# Fortcloud Crucible — Roles Matrix

> Generated on 2026-11-21 by `fortcloud-crucible roles`. Do not edit by hand.

Every exercise names a coordinator, an operator, a communicator and a
verifier. The verifier signs off only after service and data checks pass.

| Scenario | Coordinator | Operator | Communicator | Verifier | Status |
|---|---|---|---|---|---|
| `ex-failover-prod` | `alice` | `bob` | `carol` | `dave` | AT RISK |
| `ex-failover-staging` | `alice` | `bob` | `carol` | `dave` | OK |
| `ex-recovery-prod` | `alice` | `bob` | `carol` | `erin` | OK |
| `ex-recovery-sandbox` | `alice` | `bob` | `carol` | `erin` | AT RISK |
| `ex-restore-prod` | `alice` | `bob` | `carol` | `dave` | AT RISK |
| `ex-restore-sandbox` | `alice` | `bob` | `carol` | `dave` | OK |

## Roster

| Participant | Name | Team | Contact |
|---|---|---|---|
| `alice` | Alice Martin | platform-team | alice@example.com |
| `bob` | Bernard Lefevre | platform-team | bob@example.com |
| `carol` | Carole Ndiaye | communications | carol@example.com |
| `dave` | David Chen | sre | dave@example.com |
| `erin` | Erin Novak | data-platform | erin@example.com |
