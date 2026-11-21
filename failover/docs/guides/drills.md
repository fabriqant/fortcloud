# Drill guide

A drill is a controlled rehearsal of a failure. The goal is not heroics; it is a measured, repeatable result attached to the model.

## Before

- Announce the window and confirm the service owner is available.
- Check the health probe on the primary and confirm alerts are firing.
- Confirm the standby capacity is at least the primary capacity.
- Confirm the replication mode is compatible with the service RPO.
- Have the [drill template](../templates/drill.md) open for notes.

## During

1. Stop or isolate the primary (staging first, production only with an approved change window).
2. Record the **detection time** — when the alert fired versus when the failure was injected.
3. Promote the standby and record the **promotion time**.
4. Run a smoke test for every service listed on the strategy.
5. Verify data loss against the declared RPO (for `async`, check the replication lag).
6. Check that the DNS TTL did not keep clients on the dead endpoint.
7. Fail back, then confirm the model still passes `fortcloud-failover check`.

## After

Add or update an entry in `drills.yaml`:

```yaml
- id: drill-pg-2026-11
  strategy: fo-pg
  scenario: region-loss
  last: "2026-11-21"
  duration: 24m10s
  result: passed
  evidence: https://ci.example.com/drills/fo-pg-47
  owner: data-platform
```

Rules:

- `result` must be `passed` to avoid a warning.
- `last` must be within 90 days of the check date.
- `evidence` must be a link or a path to the recorded run.

Then regenerate:

```bash
fortcloud-failover check --strict --out ./docs/generated
```

## Scenarios

| Scenario | What it proves |
|---|---|
| `primary-loss` | the standby can take over after a process or instance failure |
| `region-loss` | redundancy is real across regions |
| `network-partition` | the health probe and quorum rules behave correctly |
| `idp-outage` | services can survive the identity provider failing |
| `dns-failover` | clients stop reaching the dead endpoint within the RTO |
| `manual` | the runbook is executable by a human under time pressure |
