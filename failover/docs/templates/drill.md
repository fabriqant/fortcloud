# Failover drill — <strategy id>

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Scenario | primary-loss / region-loss / dns-failover / manual |
| Strategy | `<strategy id>` |
| Primary | `<component id>` |
| Standby | `<component id>` |
| Owner | `<team>` |
| Evidence link | `<CI run, ticket or recording>` |

## Target

- RTO: `<from services.yaml>`
- RPO: `<from services.yaml>`
- Detection budget: `<detection_time>`
- Promotion budget: `<promotion_time>`

## Steps

- [ ] Announce the drill and confirm the change window.
- [ ] Verify the primary health probe and alerts.
- [ ] Verify standby capacity ≥ primary capacity.
- [ ] Verify replication mode against the RPO.
- [ ] Inject the failure and record the detection time.
- [ ] Promote the standby and record the promotion time.
- [ ] Smoke-test every covered service.
- [ ] Verify data loss against the RPO.
- [ ] Check DNS TTL behaviour.
- [ ] Fail back and confirm the model still validates.

## Measured result

| Measure | Target | Measured | Pass |
|---|---|---|---|
| Detection | `<detection_time>` | | |
| Promotion | `<promotion_time>` | | |
| Total | `<rto>` | | |
| Data loss | `<rpo>` | | |

## Outcome

- [ ] passed
- [ ] partial
- [ ] failed

Notes:

<what worked, what did not, follow-up actions with owners and dates>
