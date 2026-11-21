# Fortcloud Atlas — Runbook template

> Copy this template to `docs/runbooks/<flow-id>.md` in your own repository. A tested runbook beats a perfect one.

## Flow identity

| Field | Value |
|---|---|
| Flow | `<flow-id>` |
| Owner | `<team / person>` |
| Criticality | `P0 / P1 / P2` |
| Availability target | `<99.95%>` |
| RTO / RPO | `<minutes> / <minutes>` |
| Last restore test | `<YYYY-MM-DD>` |
| Components involved | `<model ids>` |

## Detection

- **Signals**: `<Prometheus alerts, logs, external status page>`.
- **Trigger threshold**: `<e.g. > 5% errors over 5 min>`.
- **Expected impact**: `<what users experience>`.

## Quick diagnosis

1. `<check the most upstream component in the flow>`.
2. `<check shared dependencies: DNS, IdP, secrets, network>`.
3. `<check whether a recent change caused it (GitOps, infrastructure)>`.

## Decision

| Situation | Action | Decision maker |
|---|---|---|
| `<e.g. database unavailable>` | `<fail over to the secondary DC>` | `<role>` |
| `<e.g. IdP down>` | `<enable local session cache / backup IdP>` | `<role>` |
| `<e.g. external API degraded>` | `<degraded mode: local queue>` | `<role>` |

## Recovery

1. `<step 1 — exact command>`.
2. `<step 2 — verification>`.
3. `<business validation: how do we know the flow is back?>`.

## After the incident

- [ ] Actual recovery duration: `<...>` — compare with the RTO of `<...>`.
- [ ] Actual data loss: `<...>` — compare with the RPO of `<...>`.
- [ ] Update `model/risks.yaml` if a new failure mode appeared.
- [ ] Post-mortem and corrective action: `<link>`.
