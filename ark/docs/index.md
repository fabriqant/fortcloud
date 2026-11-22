# FortCloud Ark — Documentation

FortCloud Ark checks whether declared backups can actually restore the data within the availability targets of the services that depend on it. It is standalone: it reads its own four YAML files and writes four artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — evidence, RPO, immutability, ransomware scenarios.
3. [Restore testing guide](guides/restore-testing.md) — how to run and record a restore test.
4. [ADR 0001](adrs/0001-evidence-over-snapshots.md) — why evidence beats backup snapshots.
5. [Restore report template](templates/restore.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `backup-coverage.md` | Which assets have an immutable, fresh, cross-region backup? |
| `restore-evidence.md` | Were measured RTO/RPO within target, and where is the proof? |
| `recovery-plan.md` | What must be fixed, in which order, and by whom? |
| `restore-status.json` | What is the machine-readable status for CI? |

All four live in `docs/generated/` and are rebuilt by `fortcloud-ark check`. Never edit them by hand.

## Command reference

```bash
fortcloud-ark validate [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-ark coverage [--model DIR] [--out DIR]
fortcloud-ark evidence [--model DIR] [--out DIR]
fortcloud-ark plan     [--model DIR] [--out DIR]
fortcloud-ark check    [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
