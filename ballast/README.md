# Fortcloud Ballast

### Keep workloads steady when parts fail

> **A retry without a budget is an outage with a delay.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fortcloud Ballast turns a hand-maintained YAML model of your outbound dependencies and resilience policies into a **timeout budget report**, a **policy matrix**, a **remediation plan** and a **machine-readable CI status**. It catches the failures that only appear under load: a retry storm, a call chain that cannot fit in the latency budget, a missing circuit breaker, or one slow dependency starving every other call.

[← Back to the Fortcloud-io family README](../README.md) · [Previous tool: Fortcloud Ark](../ark/README.md) · [Next tool: Fortcloud Vitals](../vitals/README.md) — health and data quality, one signal.

> **Where the code lives:** this tool is the `ballast/` folder of the [`fabriqant/fortcloud-io`](https://github.com/fabriqant/fortcloud-io) repository. It has its own model and does not depend on Atlas, Failover or Ark at runtime. The GitHub Actions workflow stays at the repository root.

## Why

Atlas maps the risk, Failover proves the switchover, Ark proves the data comes back, Ballast keeps the **request path** standing when a dependency misbehaves. A resilience setting is not "more is better":

- 4 retries on a slow API turn one call into five, multiplying load exactly when the system is unhealthy;
- retries without jitter synchronise every client into a thundering herd;
- a circuit breaker that opens after 20 failures, or resets after 5 minutes, is not protecting anything;
- summing the worst-case timeouts of a call chain often exceeds the latency budget the service promised;
- retrying a non-idempotent payment can charge twice.

Ballast makes those trade-offs explicit and reviewable in a pull request.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/ballast
python -m pip install -e .

fortcloud-ballast check
```

Result in `docs/generated/`:

- `timeout-budget.md` — worst-case call chain versus latency budget, per flow,
- `policy-matrix.md` — timeout, retries, breaker, bulkhead and fallback per dependency,
- `resilience-plan.md` — ordered remediation steps with owners,
- `ballast-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique and every reference points to a real service, dependency or policy | Error |
| A policy attached to a step targets the dependency used by that step | Error |
| Worst-case chain `Σ timeout × attempts + backoff` exceeds the service latency budget | Error |
| Retries on a non-idempotent write | Error |
| P0 dependency without a circuit breaker | Error |
| Retries without jitter | Warning |
| More than 3 retries | Warning |
| Backoff multiplier below 2 | Warning |
| No bulkhead isolation | Warning |
| Optional dependency with `fallback: none` | Warning |
| A single step consuming more than 70% of the latency budget | Warning |
| Circuit breaker opening after more than 10 failures, or resetting after more than 30s | Warning |

Durations use `0` or `<number><ms|s|m|h|d>`, and can be combined: `150ms`, `1m30s`, `2m12s`. They are stored internally in milliseconds and `format_duration()` output is reusable as model input.

## Model layout

Ballast uses its **own four files**:

```text
model/
├── services.yaml      # latency budget, criticality, owner
├── dependencies.yaml  # outbound calls: type, operation, idempotency
├── policies.yaml      # timeout, retries, backoff, breaker, bulkhead, fallback
└── flows.yaml         # ordered steps: dependency + policy
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What an entry looks like

`services.yaml`:

```yaml
version: 1
services:
  - id: checkout
    name: API de commande
    criticality: P0
    owner: commerce-team
    latency_budget: 3s
```

`dependencies.yaml`:

```yaml
version: 1
dependencies:
  - id: dep-payment
    name: Passerelle de paiement
    type: http_api
    criticality: P0
    operation: write
    idempotent: false
    owner: payments-team
```

`policies.yaml`:

```yaml
version: 1
policies:
  - id: pol-payment
    dependency: dep-payment
    timeout: 500ms
    retries: 0
    backoff: 100ms
    backoff_multiplier: 2
    jitter: false
    circuit_breaker: true
    failure_threshold: 5
    reset_timeout: 10s
    bulkhead: payment-pool
    fallback: queue
```

`flows.yaml`:

```yaml
version: 1
flows:
  - id: flow-checkout
    name: Passage de commande
    service: checkout
    steps:
      - dependency: dep-auth
        policy: pol-auth
      - dependency: dep-inventory
        policy: pol-inventory
      - dependency: dep-payment
        policy: pol-payment
```

## Generated output (excerpt)

From `docs/generated/timeout-budget.md` on the bundled example:

| Flow | Service | Budget | Worst case | Headroom | Usage | Status |
|---|---|---|---|---|---|---|
| `flow-checkout` | `checkout` | 3s | 1s500ms | 1s500ms | 50% | OK |
| `flow-login` | `identity-auth` | 1s | 325ms | 675ms | 32% | OK |
| `flow-browse` | `catalog-browse` | 2s | 1s730ms | 270ms | 86% | AT RISK |

And from `policy-matrix.md`:

| Policy | Dependency | Timeout | Retries | Worst case | Breaker | Bulkhead | Status |
|---|---|---|---|---|---|---|---|
| `pol-catalog` | `dep-catalog` | 300ms | 3 | 1s480ms | yes | catalog-pool | OK |
| `pol-pricing` | `dep-pricing` | 200ms | 4 | 1s200ms | yes | pricing-pool | AT RISK |
| `pol-search` | `dep-search` | 250ms | 0 | 250ms | no | none | AT RISK |

The bundled example intentionally contains 7 warnings so you can see the checks in action. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-ballast validate   [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-ballast budget     [--model DIR] [--out DIR]
fortcloud-ballast policies   [--model DIR] [--out DIR]
fortcloud-ballast plan       [--model DIR] [--out DIR]
fortcloud-ballast check      [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: ballast`, `cache-dependency-path: ballast/requirements.txt` and an artifact named `fortcloud-ballast-policies` containing `ballast/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Repository layout

```text
fortcloud-io/
├── .github/workflows/ci.yml
├── README.md                   # family overview
├── atlas/                      # dependency and risk map
├── failover/                   # failover plans and coverage
├── ark/                        # backup coverage and restore evidence
└── ballast/                    # this tool
    ├── README.md
    ├── pyproject.toml          # package fortcloud-ballast, CLI fortcloud-ballast
    ├── schema/                 # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_ballast/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                  # 19 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — budget, retries, breakers, bulkheads](docs/concepts.md)
- [Timeout budget guide](docs/guides/timeouts.md)
- [ADR 0001 — the timeout budget as a first-class check](docs/adrs/0001-timeout-budget.md)
- [Policy template](docs/templates/policy.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_ballast/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **Fortcloud** tool family: *Keep the cloud standing.*
