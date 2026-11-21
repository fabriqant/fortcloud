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
| `op-deploy` — Production deployments | deploy | `prod` | yes | `sink-siem` | 2026-11-19 | OK |
| `op-grant-change` — Granting and revoking privileges | grant_change | `prod` | yes | `sink-siem` | 2026-11-18 | OK |
| `op-infra-change` — Infrastructure changes in staging | infra_change | `staging` | yes | `sink-archive` | 2026-11-16 | OK |
| `op-pipeline-change` — Pipeline changes | pipeline_change | `prod` | yes | `sink-archive` | 2026-11-17 | OK |
| `op-secret-access` — Reading production secrets | secret_access | `prod` | yes | `sink-siem` | 2026-11-18 | OK |
