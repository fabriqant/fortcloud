# FortCloud Custodian — Documentation

FortCloud Custodian checks that access is least-privileged, environments are separated, secrets are referenced safely, deployments are reviewed and tested with a rollback, and sensitive operations are logged with evidence. It is standalone: it reads its own four YAML files and writes five artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — the five control families and how they connect.
3. [Least privilege guide](guides/least-privilege.md) — design grants and environment boundaries.
4. [Secrets guide](guides/secrets.md) — references, rotation and isolation.
5. [Change control guide](guides/changes.md) — review, tests and rollback.
6. [ADR 0001](adrs/0001-controls-as-model.md) — why controls are versioned files.
7. [Change record template](templates/change.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `access-matrix.md` | Who has which permission, in which environment, until when? |
| `secret-inventory.md` | Which secrets exist, where they live and when they were rotated? |
| `change-control.md` | Which deployments have review, tests and a verified rollback? |
| `audit-trail.md` | Which sensitive operations are logged, where and with what evidence? |
| `custodian-status.json` | What is the machine-readable status for CI? |

All five live in `docs/generated/` and are rebuilt by `fortcloud-custodian check`. Never edit them by hand.

## Command reference

```bash
fortcloud-custodian validate  [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-custodian access    [--model DIR] [--out DIR]
fortcloud-custodian secrets   [--model DIR] [--out DIR]
fortcloud-custodian changes   [--model DIR] [--out DIR]
fortcloud-custodian audit     [--model DIR] [--out DIR]
fortcloud-custodian check     [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
