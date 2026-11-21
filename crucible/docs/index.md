# Fortcloud Crucible — Documentation

Fortcloud Crucible checks that failure drills are rehearsed in a controlled environment first, that everyone knows their role, that communication is planned, and that the service and the data are verified before an exercise is called a success. It is standalone: it reads its own four YAML files and writes five artifacts.

## Start here

1. [Quickstart](quickstart.md) — install, run, understand the output.
2. [Concepts](concepts.md) — controlled environments, roles, communication and verification.
3. [Controlled-first guide](guides/controlled-first.md) — plan restore, failover and recovery drills safely.
4. [Communication guide](guides/communication.md) — who is told, when, and on which channel.
5. [Verification guide](guides/verification.md) — prove that the service and the data came back.
6. [ADR 0001](adrs/0001-controlled-first.md) — why the first drill is never in production.
7. [Exercise record template](templates/exercise.md) — copy it into your runbook.

## Generated artifacts

| File | Question it answers |
|---|---|
| `scenario-plan.md` | Which drills are planned, where and with which targets? |
| `roles-matrix.md` | Who coordinates, operates, communicates and verifies each drill? |
| `communication-plan.md` | Which channels are used and who is notified at start, update and end? |
| `verification-report.md` | Did the service and the data come back, with evidence and a signature? |
| `crucible-status.json` | What is the machine-readable status for CI? |

All five live in `docs/generated/` and are rebuilt by `fortcloud-crucible check`. Never edit them by hand.

## Command reference

```bash
fortcloud-crucible validate      [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-crucible scenarios     [--model DIR] [--out DIR]
fortcloud-crucible roles         [--model DIR] [--out DIR]
fortcloud-crucible communication [--model DIR] [--out DIR]
fortcloud-crucible verification   [--model DIR] [--out DIR]
fortcloud-crucible check         [--model DIR] [--out DIR] [--strict]
```

Exit codes: `0` success, `1` validation failure, `2` CLI usage error.
