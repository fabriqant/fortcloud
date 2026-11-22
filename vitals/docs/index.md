# FortCloud Vitals — Documentation

FortCloud Vitals checks whether service health and data-quality signals are backed by credible SLOs, early alerts and dated verification. It is standalone: it reads its own four YAML files and writes four artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — SLOs, error budgets, signals and data quality.
3. [SLO design guide](guides/slos.md) — how to choose targets, alerts and sampling intervals.
4. [ADR 0001](adrs/0001-error-budget.md) — why the error budget is a first-class check.
5. [Check template](templates/check.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `slo-dashboard.md` | What do we promise, what budget does it allow, and is the alert early enough? |
| `signal-catalog.md` | Which signals exist, how often are they sampled, and what do they back? |
| `quality-plan.md` | What must be fixed, in which order, and by whom? |
| `vitals-status.json` | What is the machine-readable status for CI? |

All four live in `docs/generated/` and are rebuilt by `fortcloud-vitals check`. Never edit them by hand.

## Command reference

```bash
fortcloud-vitals validate  [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-vitals dashboard [--model DIR] [--out DIR]
fortcloud-vitals signals   [--model DIR] [--out DIR]
fortcloud-vitals plan      [--model DIR] [--out DIR]
fortcloud-vitals check     [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
