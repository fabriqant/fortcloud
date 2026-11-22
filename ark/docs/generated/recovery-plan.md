# FortCloud Ark — Recovery Plan

> Generated on 2026-11-21 by `fortcloud-ark plan`. Do not edit by hand.

Ordered by asset criticality, then by tightest RTO. Fix the model, not this file.

## idp-db — Identity database

- **Owner:** sec-team
- **Criticality:** P0
- **Services:** `identity-auth`
- **Targets:** RTO 15m / RPO 0
- **Status:** PROVEN

No gap detected. Keep the backup and restore cadence.

## vault-secrets — Secrets vault

- **Owner:** sec-team
- **Criticality:** P0
- **Services:** `identity-auth`
- **Targets:** RTO 15m / RPO 0
- **Status:** AT RISK

**Gaps:**

- last successful backup is 3 days old (max 2).
- no ransomware or deletion restore scenario for a P0 asset.
- restore rst-vault is 129 days old (max 90).

**Steps:**

1. Fix: Last successful backup is 3 days old (max 2). Owner: sec-team.
2. Fix: No ransomware or deletion restore scenario for a P0 asset. Owner: sec-team.
3. Fix: Restore rst-vault is 129 days old (max 90). Owner: sec-team.
4. Re-run `fortcloud-ark check --strict` and attach `restore-status.json` to the pull request.

## pg-core — Primary transactional database

- **Owner:** data-platform
- **Criticality:** P0
- **Services:** `order-to-cash`
- **Targets:** RTO 30m / RPO 5m
- **Status:** PROVEN

No gap detected. Keep the backup and restore cadence.

## obj-lake — Object data lake

- **Owner:** data-platform
- **Criticality:** P0
- **Services:** `analytics-ingestion`
- **Targets:** RTO 4h / RPO 1h
- **Status:** PROVEN

No gap detected. Keep the backup and restore cadence.

## kafka-events — Event queue

- **Owner:** data-platform
- **Criticality:** P1
- **Services:** `analytics-ingestion`
- **Targets:** RTO 4h / RPO 1h
- **Status:** PROVEN

No gap detected. Keep the backup and restore cadence.

## config-repo — GitOps configuration repository

- **Owner:** platform
- **Criticality:** P1
- **Services:** `platform-config`
- **Targets:** RTO 8h / RPO 1d
- **Status:** AT RISK

**Gaps:**

- restore rst-config result is 'partial'.

**Steps:**

1. Fix: Restore rst-config result is 'partial'. Owner: platform.
2. Re-run `fortcloud-ark check --strict` and attach `restore-status.json` to the pull request.

## logs-archive — Audit log archive

- **Owner:** platform
- **Criticality:** P2
- **Services:** `platform-config`
- **Targets:** RTO 8h / RPO 1d
- **Status:** AT RISK

**Gaps:**

- no restore test.

**Steps:**

1. Fix: No restore test. Owner: platform.
2. Re-run `fortcloud-ark check --strict` and attach `restore-status.json` to the pull request.

## report-exports — Reporting exports

- **Owner:** analytics-team
- **Criticality:** P2
- **Services:** `platform-config`
- **Targets:** RTO 8h / RPO 1d
- **Status:** AT RISK

**Gaps:**

- last successful backup is 6 days old (max 2).
- no restore test.

**Steps:**

1. Fix: Last successful backup is 6 days old (max 2). Owner: analytics-team.
2. Fix: No restore test. Owner: analytics-team.
3. Re-run `fortcloud-ark check --strict` and attach `restore-status.json` to the pull request.

## Definition of done

- Every P0 asset has an immutable, encrypted, cross-region backup.
- Backup schedule is compatible with the tightest service RPO.
- Every P0 asset has a recent restore test with a deletion or ransomware scenario.
- Measured RTO and RPO are below the service targets.
- Every restore result is `passed` and has an evidence link.
- `fortcloud-ark check --strict` exits with code 0.
