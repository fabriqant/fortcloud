# FortCloud Ballast — Documentation

FortCloud Ballast checks whether a request chain can still meet the latency promised by its service when dependencies are slow or failing. It is standalone: it reads its own four YAML files and writes four artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — timeout budgets, retry amplification, breakers, bulkheads.
3. [Timeout budget guide](guides/timeouts.md) — how to design and verify a call chain.
4. [ADR 0001](adrs/0001-timeout-budget.md) — why the budget is a first-class check.
5. [Policy template](templates/policy.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `timeout-budget.md` | Does each flow fit within its service's latency budget? |
| `policy-matrix.md` | Which guardrails are configured for each outbound dependency? |
| `resilience-plan.md` | What must be fixed, in which order, and by whom? |
| `ballast-status.json` | What is the machine-readable status for CI? |

All four live in `docs/generated/` and are rebuilt by `fortcloud-ballast check`. Never edit them by hand.

## Command reference

```bash
fortcloud-ballast validate [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-ballast budget   [--model DIR] [--out DIR]
fortcloud-ballast policies [--model DIR] [--out DIR]
fortcloud-ballast plan     [--model DIR] [--out DIR]
fortcloud-ballast check    [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
