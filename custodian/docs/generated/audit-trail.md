# Fortcloud Custodian — Audit Trail

> Generated on 2026-11-21 by `fortcloud-custodian audit`. Do not edit by hand.

Sensitive operations must leave durable evidence. A log that can be
edited is not an audit trail.

## Log sinks

| Sink | Type | Destination | Retention | Immutable | Status |
|---|---|---|---|---|---|
| `sink-archive` | object-storage | `s3://audit-logs/custodian/` | 2555d | yes | OK |
| `sink-siem` | siem | `https://siem.example.com/events` | 365d | yes | OK |

## Sensitive operations

| Operation | Kind | Environment | Logged | Sink | Last evidence | Status |
|---|---|---|---|---|---|---|
| `op-deploy` — Déploiements en production | deploy | `prod` | yes | `sink-siem` | 2026-11-19 | OK |
| `op-grant-change` — Attribution et révocation de privilèges | grant_change | `prod` | yes | `sink-siem` | 2026-11-18 | OK |
| `op-infra-change` — Changements d'infrastructure en préproduction | infra_change | `staging` | yes | `sink-archive` | 2026-11-16 | OK |
| `op-pipeline-change` — Modification des pipelines | pipeline_change | `prod` | yes | `sink-archive` | 2026-11-17 | OK |
| `op-secret-access` — Lecture des secrets de production | secret_access | `prod` | yes | `sink-siem` | 2026-11-18 | OK |
