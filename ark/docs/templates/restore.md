# Restore test report — <restore id>

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Backup | `<backup id>` |
| Asset | `<asset id>` |
| Scenario | point_in_time / full_loss / region_loss / deletion / ransomware |
| Owner | `<team>` |
| Evidence link | `<CI run, ticket or recording>` |

## Targets

| Measure | Target | Measured | Pass |
|---|---|---|---|
| RTO | `<from services.yaml>` | | |
| RPO | `<from services.yaml>` | | |

## Steps

- [ ] Confirm the backup job succeeded and the copy is immutable.
- [ ] Confirm cross-region copy exists for P0.
- [ ] Prepare an isolated restore target.
- [ ] Choose and record the restore point.
- [ ] Restore and measure the duration.
- [ ] Verify integrity with checksums and application smoke tests.
- [ ] Compare restored data with the source at the restore point.
- [ ] Verify encryption and access control on the restored copy.
- [ ] Delete the test copy according to the retention policy.

## Outcome

- [ ] passed
- [ ] partial
- [ ] failed

Notes:

<what worked, what did not, follow-up actions with owners and dates>
