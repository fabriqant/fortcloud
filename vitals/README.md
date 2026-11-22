# FortCloud Vitals

### Health and data quality, one signal

> **An SLO without an error budget is a wish with a dashboard.**

[![CI](https://github.com/fabriqant/fortcloud/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

FortCloud Vitals turns a hand-maintained YAML model of your services, signals, SLOs and verification checks into an **SLO dashboard**, a **signal catalog**, a **quality plan** and a **machine-readable CI status**. It finds the gaps that make monitoring theatre: an alert that fires after the budget is already spent, a signal sampled too coarsely to see the breach, a P0 service with no data-quality objective, or an SLO nobody has verified.

[← Back to the FortCloud-io family README](../README.md) · [Previous tool: FortCloud Ballast](../ballast/README.md) · [Next tool: FortCloud Custodian](../custodian/README.md) — guard access, prove every change.

> **Where the code lives:** this tool is the `vitals/` folder of the [`fabriqant/fortcloud`](https://github.com/fabriqant/fortcloud) repository. It has its own model and does not depend on Atlas, Failover, Ark or Ballast at runtime. The GitHub Actions workflow stays at the repository root.

## Why

Ballast keeps the request path standing; Vitals checks that you can actually *see* whether it stands. "We have dashboards" is not evidence:

- a 99.9% target over 30 days allows **43m12s** of failure — an alert at 99.95% fires at exactly half of that, which is good; at 99.91% it fires after 90% is already gone;
- a 15-minute sampling interval cannot observe an error budget of a few minutes;
- a freshness target with an alert only one minute below it leaves no time to react;
- a P0 service with availability alone can be healthy while its data is stale or invalid;
- a check with no date, no evidence link and no runbook is not a control.

Vitals makes those trade-offs explicit and reviewable in a pull request.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud.git
cd fortcloud/vitals
python -m pip install -e .

fortcloud-vitals check
```

Result in `docs/generated/`:

- `slo-dashboard.md` — objectives, error budgets, alert headroom and status,
- `signal-catalog.md` — signal sources, intervals and the objectives they back,
- `quality-plan.md` — ordered remediation steps with owners,
- `vitals-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique and every objective references a real service and signal | Error |
| Signal kind matches the objective kind | Error |
| The alert is tighter than the target (percent higher, duration lower) | Error |
| P0 service without an availability objective | Error |
| P0 service without a data-quality objective (freshness, completeness, validity) | Error |
| Failed check on a P0 service | Error |
| P0 check without a runbook | Error |
| Alert fires after more than 50% of the error budget is spent | Warning |
| Latency/freshness alert margin below 20% of the target | Warning |
| Signal interval too coarse to observe the budget | Warning |
| Window shorter than 7 days | Warning |
| Check older than 90 days | Warning |
| Check result other than `passed` on a non-P0 service | Warning |
| Check without evidence or without a runbook | Warning |
| Objective without a verification check | Warning |
| Signal not used by any objective | Warning |

Durations are `0` or `<number><ms|s|m|h|d>`, combinable (`150ms`, `1m30s`, `43m12s`). They are stored internally in milliseconds and `format_duration()` output is reusable as model input.

## Model layout

Vitals uses its **own four files**:

```text
model/
├── services.yaml    # criticality and owner
├── signals.yaml     # source, kind, sampling interval, query
├── objectives.yaml  # target, alert threshold, window, owner
└── checks.yaml      # dated verification, result, evidence, runbook
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What an entry looks like

`services.yaml`:

```yaml
version: 1
services:
  - id: checkout
    name: Order API
    criticality: P0
    owner: commerce-team
```

`signals.yaml`:

```yaml
version: 1
signals:
  - id: sig-checkout-availability
    name: Order API availability
    kind: availability
    source: prometheus
    query: sum(rate(http_requests_total{job="checkout",code!~"5.."}[5m])) / sum(rate(http_requests_total{job="checkout"}[5m]))
    interval: 30s
    unit: percent
    owner: commerce-team
```

`objectives.yaml`:

```yaml
version: 1
objectives:
  - id: slo-checkout-avail
    service: checkout
    signal: sig-checkout-availability
    kind: availability
    target: 99.9
    alert_threshold: 99.95
    window: 30d
    owner: commerce-team
```

`checks.yaml`:

```yaml
version: 1
checks:
  - id: chk-checkout-avail
    objective: slo-checkout-avail
    last: "2026-11-18"
    result: passed
    evidence: https://ci.example.com/vitals/checkout-availability-118
    owner: commerce-team
    runbook: ../templates/check.md
```

For `latency` and `freshness` objectives, `target` and `alert_threshold` are durations (`300ms` / `240ms`); for `availability`, `completeness` and `validity` they are percentages.

## Generated output (excerpt)

From `docs/generated/slo-dashboard.md` on the bundled example:

| Objective | Service | Crit. | Target | Window | Budget | Alert at | Headroom | Status |
|---|---|---|---|---|---|---|---|---|
| `slo-auth-avail` | `identity-auth` | P0 | 99.99% | 30d | 4m19s | 99.995% | 50% used at alert | OK |
| `slo-auth-completeness` | `identity-auth` | P0 | 99.5% | 30d | 3h36m | 99.6% | 80% used at alert | AT RISK |
| `slo-checkout-avail` | `checkout` | P0 | 99.9% | 30d | 43m12s | 99.95% | 50% used at alert | OK |
| `slo-checkout-latency` | `checkout` | P0 | 300ms | 30d | margin 60ms | 240ms | 20% margin | OK |

The bundled example intentionally contains 7 warnings so you can see the checks in action. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-vitals validate   [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-vitals dashboard  [--model DIR] [--out DIR]
fortcloud-vitals signals    [--model DIR] [--out DIR]
fortcloud-vitals plan       [--model DIR] [--out DIR]
fortcloud-vitals check      [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: vitals`, `cache-dependency-path: vitals/requirements.txt` and an artifact named `fortcloud-vitals-dashboard` containing `vitals/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Repository layout

```text
fortcloud/
├── .github/workflows/ci.yml
├── README.md                   # family overview
├── atlas/                      # dependency and risk map
├── failover/                   # failover plans and coverage
├── ark/                        # backup coverage and restore evidence
├── ballast/                    # timeout budgets and resilience policies
└── vitals/                     # this tool
    ├── README.md
    ├── pyproject.toml          # package fortcloud-vitals, CLI fortcloud-vitals
    ├── schema/                 # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_vitals/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                  # 19 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — SLOs, error budgets, signals, data quality](docs/concepts.md)
- [SLO design guide](docs/guides/slos.md)
- [ADR 0001 — the error budget as a first-class check](docs/adrs/0001-error-budget.md)
- [Check template](docs/templates/check.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_vitals/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **FortCloud** tool family: *Keep the cloud standing.*
