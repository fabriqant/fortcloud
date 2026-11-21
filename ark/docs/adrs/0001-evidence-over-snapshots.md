# ADR 0001 — Evidence over snapshots

- Status: Accepted
- Date: 2026-11-21

## Context

A backup inventory can be perfectly accurate and still tell us nothing about whether a restore works. Snapshots of "backup success" are produced by the systems that create the backups, which have an obvious incentive to report success. Restore duration and data loss are only known by actually restoring.

## Decision

Ark treats the restore test as the primary evidence. A P0 asset without a recent, successful, measured restore test is not "covered", regardless of its backup configuration. Backup configuration rules (immutability, encryption, cross-region, freshness, schedule) are supporting checks.

## Consequences

- Users must maintain a `restores.yaml` file with measured values and evidence links.
- Some assets will be reported AT RISK even though their backup dashboards are green. That is intentional.
- Restore tests must be automated or at least recorded in CI so the evidence link is durable.
- The tool stays offline: it validates declared evidence rather than running restores itself.

## Alternatives rejected

- **Trusting backup job status** as sufficient proof: it measures the write path, not the read path.
- **Running restores directly from Ark**: would require cloud credentials, network access and a runtime dependency on each provider — incompatible with the standalone design.
