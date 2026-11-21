# Restore testing guide

## Before

- Confirm the backup is recent and its last job succeeded.
- Confirm immutability and cross-region replication for P0 assets.
- Pick the scenario that matches the threat: `point_in_time`, `full_loss`, `region_loss`, `deletion`, `ransomware`.
- Prepare an isolated target: restoring over production is not a test.
- Have the [restore report template](../templates/restore.md) open for notes.

## During

1. Choose a restore point and note the timestamp.
2. Restore into the isolated target; start the clock.
3. Verify integrity (checksums, row counts, application-level smoke tests).
4. Stop the clock and record `measured_rto`.
5. Compare the restored data with the source at the restore point and record `measured_rpo`.
6. Verify encryption and access control on the restored copy.
7. Delete the test copy according to your data retention policy.

## After

Add or update an entry in `restores.yaml`:

```yaml
- id: rst-pg-2026-11
  backup: bk-pg
  scenario: ransomware
  last: "2026-11-21"
  measured_rto: 28m
  measured_rpo: 5m
  result: passed
  evidence: https://ci.example.com/restores/rst-pg-58
  owner: data-platform
```

Rules:

- `result` must be `passed` to avoid a warning.
- `last` must be within 90 days of the check date.
- `measured_rto` and `measured_rpo` are compared with the tightest service targets.
- `evidence` must be a link or path to the recorded run.

Then regenerate:

```bash
fortcloud-ark check --strict --out ./docs/generated
```

## Cadence

| Asset criticality | Restore test cadence | Required scenarios |
|---|---|---|
| P0 | every 90 days | one routine + one `ransomware` or `deletion` |
| P1 | every 180 days | one routine |
| P2 | at least yearly | one routine |
