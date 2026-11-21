# Fortcloud Atlas

### Dependency & Risk Map for hybrid and multi-cloud infrastructure

> **Map every dependency. See every risk.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fortcloud Atlas turns a hand-maintained YAML model of your infrastructure into a **validated dependency graph**, a **single-point-of-failure audit** and an **RTO/RPO matrix**. It is one tool in the Fortcloud family and works entirely on its own — no platform, no backend, no agent.

[← Back to the Fortcloud-io family README](../README.md) · [Next tool: Fortcloud Failover](../failover/README.md) — design out the single point of failure.

> **Where the code lives:** this tool is the `atlas/` folder of the [`fabriqant/fortcloud-io`](https://github.com/fabriqant/fortcloud-io) repository. The GitHub Actions workflow lives at the repository root (`.github/workflows/ci.yml`) and runs with `working-directory: atlas` so GitHub can discover it.

## Why

In hybrid and multi-cloud setups, the dangerous dependencies are rarely in the application diagram: DNS, the IdP, the secrets manager, the network hub, the CI/CD pipeline. Atlas makes them explicit, computes their blast radius and fails your CI when a P0 component has no owner and no mitigation.

Typical questions Atlas answers:

- Which single instance takes down four business flows if it disappears?
- Which P0 components still live in one region or with one provider?
- Is the advertised RTO backed by a restore test younger than 90 days?
- Which FMEA risks are critical, open and past their due date?

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/atlas
python -m pip install -e .

fortcloud-atlas check
```

Result:

- `docs/generated/dependency-graph.md` — Mermaid graph of every `A depends on B` edge.
- `docs/generated/resilience-report.md` — SPOFs, single-region P0s, RTO/RPO matrix, FMEA risk register, stale restore tests.

Try it without installing anything:

```bash
python -m fortcloud_atlas check --model examples/hybrid-multicloud/model --out /tmp/atlas-demo
```

Requirements: Python 3.9+ and two dependencies (`PyYAML`, `jsonschema`), installed automatically by `pip install -e .`.

## What it checks

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique; all references point to real components | Error |
| A P0 component with one instance has an active risk, owner and action | Error |
| A P0 storage component has an immutable backup and a dated restore test | Error |
| A P0 component runs in a single region | Warning |
| A restore test is older than 90 days | Warning |
| A critical risk (score ≥ 15) is still open | Warning |

Scoring is FMEA: `score = likelihood × impact`, from 1 to 5 each.

## Model layout

```text
model/
├── components.yaml     # inventory: storage, processing, orchestration, network, identity, external
├── dependencies.yaml   # directed edges: "from depends on to"
├── flows.yaml          # business flows + availability target + RTO/RPO + recovery strategy
└── risks.yaml          # FMEA register with owner, mitigations and corrective action
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What a model entry looks like

`components.yaml` — the inventory and its redundancy/backup facts:

```yaml
version: 1
components:
  - id: pg-core
    name: Base transactionnelle principale
    category: storage
    criticality: P0
    owner: data-platform
    provider: hybride (on-prem DC1 + cloud eu-west-3)
    environments: [prod, dr]
    regions: [eu-west-3, on-prem-dc1]
    zones: [az1, az2]
    redundancy:
      instances: 2
      active_passive: true
      replication: async
    backup:
      enabled: true
      immutable: true
      retention_days: 35
      last_restore_test: "2026-10-12"
```

`dependencies.yaml` — direction matters: `from` is the component that **depends on** `to`. Many inbound arrows to one node mean a large blast radius.

```yaml
version: 1
dependencies:
  - id: d-001
    from: k8s-control
    to: dns-global
    kind: dns
    required: true
    description: Internal and external name resolution for the cluster.
```

`flows.yaml` — the business promise, with an RTO/RPO that must be credible:

```yaml
version: 1
flows:
  - id: order-to-cash
    name: Order to cash
    criticality: P0
    owner: commerce-team
    availability_target: 99.95%
    rto: 30m
    rpo: 5m
    strategy: Multi-AZ + async replication + immutable backups + circuit breaker.
    components: [pg-core, kafka-bus, idp-oidc, payments-api, dns-global]
    external_dependencies: [payments-api]
    last_restore_test: "2026-10-12"
```

Accepted RTO/RPO format: `0` or `<number><s|m|h|d>`.

`risks.yaml` — one FMEA row per threat, with an owner and a dated corrective action.

## Generated output (excerpt)

From `docs/generated/resilience-report.md` on the bundled example:

| Flow | Criticality | Availability | RTO | RPO | Owner | Last restore test |
|---|---|---|---|---|---|---|
| `identity-auth` | P0 | 99.99% | 15m | 0 | sec-team | 18 d |
| `order-to-cash` | P0 | 99.95% | 30m | 5m | commerce-team | 39 d |
| `analytics-ingestion` | P1 | 99.50% | 4h | 1h | data-platform | **98 d (stale)** |
| `deploy-pipeline` | P2 | 99.00% | 8h | 24h | platform | **142 d (stale)** |

And the FMEA register, sorted by descending score:

| ID | Risk | Score | Severity | Status | Owner | Due |
|---|---|---|---|---|---|---|
| R-007 | External payments API unavailable | 16 | critical | in_progress | payments-team | 2026-11-30 |
| R-001 | Single identity provider | 15 | critical | in_progress | sec-team | 2026-12-15 |
| R-002 | Single DNS provider | 15 | critical | in_progress | net-team | 2026-12-20 |

The bundled example intentionally contains 11 warnings (stale restore tests, single-region P0s, open critical risks) so you can see the checks in action. Your own clean model should produce none.

## CLI

```bash
fortcloud-atlas validate [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-atlas graph    [--model DIR] [--out DIR]
fortcloud-atlas report   [--model DIR] [--out DIR]
fortcloud-atlas check    [--model DIR] [--out DIR] [--strict]
```

`--schema-dir` lets you point at a different set of JSON Schemas. `--strict` turns warnings into errors — handy once your model is clean. Exit code is `0` on success, `1` otherwise, so the commands drop straight into CI.

## Continuous integration

The workflow at the repository root runs the unit tests, validates the model and publishes the generated files as an artifact named `fortcloud-atlas-report`:

```yaml
defaults:
  run:
    working-directory: atlas

jobs:
  test-and-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: atlas/requirements.txt
      - run: python -m pip install -e .
      - run: python -m unittest discover -s tests -v
      - run: fortcloud-atlas check --out ./artifacts
      - uses: actions/upload-artifact@v4
        with:
          name: fortcloud-atlas-report
          path: atlas/artifacts
```

See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). Generated files are disposable: rebuild them, never hand-edit them.

## Repository layout

```text
fortcloud-io/
├── .github/workflows/ci.yml
├── README.md                  # family overview
└── atlas/                     # this tool
    ├── README.md
    ├── pyproject.toml         # package fortcloud-atlas, CLI fortcloud-atlas
    ├── requirements.txt
    ├── schema/                # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_atlas/   # cli, core, validate, render
    ├── examples/hybrid-multicloud/model/
    ├── docs/                  # concepts, guides, C4 views, ADRs, runbook template
    ├── tests/                 # 10 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Explained simply — how it works and glossary](docs/explained.md) — start here if the terminology is new
- [Quickstart](docs/quickstart.md)
- [Concepts — SPOF, FMEA, RTO/RPO](docs/concepts.md)
- [Service levels and error budgets](docs/guides/service-levels.md)
- [Technology guide](docs/guides/technology.md)
- [Reference views (C4) — system context](docs/architecture/system-context.md)
- [Reference views (C4) — container view](docs/architecture/container-view.md)
- [ADR 0001 — YAML as source of truth](docs/adrs/0001-yaml-as-source-of-truth.md)
- [ADR 0002 — Generated artifacts are disposable](docs/adrs/0002-generated-artifacts-are-disposable.md)
- [Runbook template](docs/templates/runbook.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` and to the rules in `src/fortcloud_atlas/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **Fortcloud** tool family: *Keep the cloud standing.*
