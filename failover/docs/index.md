# Fortcloud Failover — Documentation

Fortcloud Failover checks whether a declared failover design can actually meet the availability targets of the services it protects. It is standalone: it reads its own four YAML files and writes four artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — false redundancy, RTO budget, replication and drill evidence.
3. [Drill guide](guides/drills.md) — how to run and record a failover drill.
4. [ADR 0001](adrs/0001-standalone-model.md) — why Failover has an independent model.
5. [Drill template](templates/drill.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `failover-matrix.md` | Which strategies cover which P0 components, and which are at risk? |
| `failover-plan.md` | What exactly must be fixed, in which order, and by whom? |
| `drill-scenarios.md` | What do we run to prove the switch works? |
| `failover-status.json` | What is the machine-readable status for CI? |

All four live in `docs/generated/` and are rebuilt by `fortcloud-failover check`. Never edit them by hand.

## Command reference

```bash
fortcloud-failover validate [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-failover matrix   [--model DIR] [--out DIR]
fortcloud-failover plan     [--model DIR] [--out DIR]
fortcloud-failover drills   [--model DIR] [--out DIR]
fortcloud-failover check    [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
