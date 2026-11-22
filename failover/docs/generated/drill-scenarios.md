# FortCloud Failover — Drill Scenarios

> Generated on 2026-11-21 by `fortcloud-failover drills`. Do not edit by hand.

Run these scenarios in staging (or in production with an approved change
window). Record the measured time and attach evidence to the pull request.

| Strategy | Primary | Standby | Mode | Last drill | Evidence |
|---|---|---|---|---|---|
| `fo-dns` | `dns-global` | `dns-global-dr` | Active/active | 24 d | https://ci.example.com/drills/fo-dns-17 |
| `fo-idp` | `idp-oidc` | `idp-oidc-dr` | Active/passive | 16 d | https://ci.example.com/drills/fo-idp-42 |
| `fo-pg` | `pg-core` | `pg-core-dr` | Active/passive | 40 d (partial) | https://ci.example.com/drills/fo-pg-31 |
| `fo-vault` | `vault-secrets` | `vault-secrets-dr` | Active/passive | **129 d (stale)** | https://ci.example.com/drills/fo-vault-08 |

## fo-dns — loss of `dns-global`

- **Target:** restore service in ≤ 15m (expected switchover 6m).
- **Replication:** stateless — verify the RPO before promoting `dns-global-dr`.
- **Runbook:** ../../docs/templates/drill.md

1. Announce the drill and confirm the change window with the service owner.
2. Check that the health probe on `dns-global` is green and alerting is active.
3. Simulate the failure of `dns-global` (stop the endpoint or isolate the region).
4. Measure detection time against 1m.
5. Promote `dns-global-dr` and measure the time against 5m.
6. Run a smoke test for every covered service and verify data loss against the RPO.
7. Fail back to `dns-global`, then record duration, result and evidence in `drills.yaml`.

Recorded drills:

- `drill-dns` — dns-failover on 2026-10-28 (24 d ago, result: passed) — https://ci.example.com/drills/fo-dns-17

## fo-idp — loss of `idp-oidc`

- **Target:** restore service in ≤ 15m (expected switchover 2m30s).
- **Replication:** stateless — verify the RPO before promoting `idp-oidc-dr`.
- **Runbook:** ../../docs/templates/drill.md

1. Announce the drill and confirm the change window with the service owner.
2. Check that the health probe on `idp-oidc` is green and alerting is active.
3. Simulate the failure of `idp-oidc` (stop the endpoint or isolate the region).
4. Measure detection time against 30s.
5. Promote `idp-oidc-dr` and measure the time against 2m.
6. Run a smoke test for every covered service and verify data loss against the RPO.
7. Fail back to `idp-oidc`, then record duration, result and evidence in `drills.yaml`.

Recorded drills:

- `drill-idp` — primary-loss on 2026-11-05 (16 d ago, result: passed) — https://ci.example.com/drills/fo-idp-42

## fo-pg — loss of `pg-core`

- **Target:** restore service in ≤ 30m (expected switchover 26m).
- **Replication:** async — verify the RPO before promoting `pg-core-dr`.
- **Runbook:** ../../docs/templates/drill.md

1. Announce the drill and confirm the change window with the service owner.
2. Check that the health probe on `pg-core` is green and alerting is active.
3. Simulate the failure of `pg-core` (stop the endpoint or isolate the region).
4. Measure detection time against 1m.
5. Promote `pg-core-dr` and measure the time against 25m.
6. Run a smoke test for every covered service and verify data loss against the RPO.
7. Fail back to `pg-core`, then record duration, result and evidence in `drills.yaml`.

Recorded drills:

- `drill-pg` — region-loss on 2026-10-12 (40 d ago, result: partial) — https://ci.example.com/drills/fo-pg-31

## fo-vault — loss of `vault-secrets`

- **Target:** restore service in ≤ 15m (expected switchover 11m).
- **Replication:** sync — verify the RPO before promoting `vault-secrets-dr`.
- **Runbook:** ../../docs/templates/drill.md

1. Announce the drill and confirm the change window with the service owner.
2. Check that the health probe on `vault-secrets` is green and alerting is active.
3. Simulate the failure of `vault-secrets` (stop the endpoint or isolate the region).
4. Measure detection time against 1m.
5. Promote `vault-secrets-dr` and measure the time against 10m.
6. Run a smoke test for every covered service and verify data loss against the RPO.
7. Fail back to `vault-secrets`, then record duration, result and evidence in `drills.yaml`.

Recorded drills:

- `drill-vault` — region-loss on 2026-07-15 (129 d ago, result: passed) — https://ci.example.com/drills/fo-vault-08
