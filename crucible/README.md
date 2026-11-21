# Fortcloud Crucible

### Rehearse the outage before it happens.

> **A recovery plan that has never been rehearsed is a document, not a capability.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fortcloud Crucible turns a hand-maintained YAML model of failure drills into a **scenario plan**, a **who-does-what matrix**, a **communication plan**, a **service/data verification report** and a **machine-readable CI status**. It answers the questions an incident review always asks:

| Requirement | Where it is modelled | What Crucible checks |
|---|---|---|
| **Organise restore, failover and recovery tests in a controlled environment first** | `environments.yaml`, `scenarios.yaml` | An environment is controlled only if isolated, non-production and approved; a production exercise of a kind requires a passed rehearsal of the same kind in a controlled environment |
| **Document who does what** | `scenarios.yaml` → `assignments` | Every drill names a coordinator, an operator, a communicator and a verifier, all drawn from the participant roster |
| **Document how to communicate** | `communication.yaml` | Declared channels and stakeholders, notification at start/update/end, cadence under 15 minutes, approval for external channels |
| **Verify the service and the data are back to a correct state** | `verification.yaml` | Passed service check, passed data check, evidence link and an approved verifier sign-off after the scheduled date |
| **Keep the plan credible over time** | all four files | No stale planned drills, no silently failed exercise, no longer-than-4h drill window |

[← Back to the Fortcloud-io family README](../README.md) · [Previous tool: Fortcloud Custodian](../custodian/README.md)

> **Where the code lives:** this tool is the `crucible/` folder of the [`fabriqant/fortcloud-io`](https://github.com/fabriqant/fortcloud-io) repository. It has its own model and does not depend on Atlas, Failover, Ark, Ballast, Vitals or Custodian at runtime. The GitHub Actions workflow stays at the repository root.

## Why

A declared RTO is a hypothesis. It becomes a fact only when someone has actually switched over, restored the data, told the right people and checked that the service and the records came back. Crucible makes that rehearsal a reviewable artefact:

- the **controlled-first rule** stops a team from experimenting in production;
- the **four roles** remove the "who was driving?" ambiguity during a drill;
- the **communication plan** makes an announced exercise indistinguishable from a real incident in the best way — everybody knows the script;
- the **verification report** refuses to mark a drill green without a service check, a data check, evidence and a signature.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/crucible
python -m pip install -e .

fortcloud-crucible check
```

Result in `docs/generated/`:

- `scenario-plan.md` — every drill, its kind, environment, status and targets;
- `roles-matrix.md` — the four roles per drill plus the participant roster;
- `communication-plan.md` — channels, stakeholders and the notification plan;
- `verification-report.md` — service/data checks, sign-offs and exercise verdicts;
- `crucible-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

### Controlled environment first

| Rule | Severity |
|---|---|
| An exercise references a declared environment | Error |
| A scenario in `prod` has a passed rehearsal of the same kind in an isolated, non-production, approved environment | Error |
| An environment used for exercises is approved | Warning |

### Who does what

| Rule | Severity |
|---|---|
| A drill assigns a coordinator, operator, communicator and verifier | Error |
| Every assigned person exists in the participant roster | Error |
| Scenario identifiers are unique | Error |

### Communication

| Rule | Severity |
|---|---|
| A drill names a declared communication channel | Error |
| Every stakeholder names a declared channel | Error |
| Someone is notified at start, update and end | Warning |
| Status updates are sent at most every 15 minutes | Warning |
| An external channel has an approval | Warning |
| A planned/running drill is not left on the calendar for weeks | Warning |

### Verification and sign-off

| Rule | Severity |
|---|---|
| A passed drill has a passed **service** check and a passed **data** check | Error |
| A passed drill has an approved sign-off from the verifier | Error |
| A check references a declared scenario | Error |
| A failed verification result | Error |
| Every check carries an evidence link | Warning |
| A sign-off is dated on or after the scheduled exercise | Warning |
| A failed drill is flagged for retest | Warning |
| A drill window longer than 4 hours | Warning |

## Model layout

Crucible uses its **own four files**:

```text
model/
├── environments.yaml   # isolated, non-production, approved drill environments
├── scenarios.yaml      # participants + restore/failover/recovery drills and roles
├── communication.yaml  # channels, stakeholders and the notification plan
└── verification.yaml   # service/data checks, evidence and sign-offs
```

Point the CLI at your own directory with `--model /path/to/your/model`. Durations follow the same convention as Ballast and Vitals: `0` or `<number><ms|s|m|h|d>`, combinable (`1h30m`), quoted when zero. The example in `examples/hybrid-multicloud/` is complete and working — replace it, never edit generated files.

### What an entry looks like

`scenarios.yaml`:

```yaml
version: 1
participants:
  - id: dave
    name: David Chen
    team: sre
scenarios:
  - id: ex-restore-sandbox
    name: Checkout API restore
    kind: restore
    environment: sandbox
    system: checkout
    scheduled: "2026-11-25"
    status: passed
    target_rto: 30m
    target_rpo: 5m
    duration: 2h
    blast_radius: contained
    channel: war-room
    owner: platform-team
    assignments:
      - { person: alice, role: coordinator }
      - { person: bob, role: operator }
      - { person: carol, role: communicator }
      - { person: dave, role: verifier }
```

`verification.yaml`:

```yaml
version: 1
checks:
  - id: chk-restore-service
    scenario: ex-restore-sandbox
    kind: service
    metric: http_5xx_rate
    expected: "0"
    result: passed
    evidence: https://ci.example.com/crucible/restore-service-25
    owner: dave
  - id: chk-restore-data
    scenario: ex-restore-sandbox
    kind: data
    metric: order_count_after_restore
    expected: equal
    result: passed
    evidence: https://ci.example.com/crucible/restore-data-25
    owner: erin
signoffs:
  - scenario: ex-restore-sandbox
    person: dave
    role: verifier
    date: "2026-11-26"
    decision: approved
```

## Generated output (excerpt)

From `scenario-plan.md`:

| Scenario | Kind | Env | Controlled | Scheduled | Status | RTO | Status |
|---|---|---|---|---|---|---|---|
| `ex-restore-sandbox` | Restore | `sandbox` | yes | 2026-11-25 | Passed | 30m | OK |
| `ex-restore-prod` | Restore | `prod` | no | 2026-11-20 | Failed | 30m | AT RISK |

And from `verification-report.md`:

- `ex-failover-staging` — Passed: **VERIFIED**
- `ex-failover-prod` — Planned: **PENDING**

The bundled example intentionally contains 6 warnings so you can see the checks in action. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-crucible validate      [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-crucible scenarios     [--model DIR] [--out DIR]
fortcloud-crucible roles         [--model DIR] [--out DIR]
fortcloud-crucible communication [--model DIR] [--out DIR]
fortcloud-crucible verification   [--model DIR] [--out DIR]
fortcloud-crucible check         [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: crucible`, `cache-dependency-path: crucible/requirements.txt` and an artifact named `fortcloud-crucible-drills` containing `crucible/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Repository layout

```text
fortcloud-io/
├── .github/workflows/ci.yml
├── README.md                   # family overview
├── atlas/                      # dependency and risk map
├── failover/                   # failover plans and coverage
├── ark/                        # backup coverage and restore evidence
├── ballast/                    # timeout budgets and resilience policies
├── vitals/                     # SLOs, signals and data quality
├── custodian/                  # least privilege, secrets, changes, audit
└── crucible/                   # this tool
    ├── README.md
    ├── pyproject.toml          # package fortcloud-crucible, CLI fortcloud-crucible
    ├── schema/                 # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_crucible/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                  # 20 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts](docs/concepts.md)
- [Controlled-first guide](docs/guides/controlled-first.md)
- [Communication guide](docs/guides/communication.md)
- [Verification guide](docs/guides/verification.md)
- [ADR 0001 — rehearse before production](docs/adrs/0001-controlled-first.md)
- [Exercise record template](docs/templates/exercise.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_crucible/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **Fortcloud** tool family: *Keep the cloud standing.*
