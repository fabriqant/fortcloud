# Fortcloud Atlas

### Dependency & Risk Map for hybrid and multi-cloud infrastructure

> **Map every dependency. See every risk.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fortcloud Atlas turns a hand-maintained YAML model of your infrastructure into a **validated dependency graph**, a **single-point-of-failure audit** and an **RTO/RPO matrix**. It is one tool in the Fortcloud family and works entirely on its own — no platform, no backend, no agent.

## Why

In hybrid and multi-cloud setups, the dangerous dependencies are rarely in the application diagram: DNS, the IdP, the secrets manager, the network hub, the CI/CD pipeline. Atlas makes them explicit, computes their blast radius and fails your CI when a P0 component has no owner and no mitigation.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd atlas
python -m pip install -e .

fortcloud-atlas check
```

> The Fortcloud Atlas tool lives in the `atlas/` folder of the `fortcloud-io` repository. The CI workflow stays at the repository root so GitHub Actions can discover it.

Result:

- `docs/generated/dependency-graph.md` — Mermaid graph of every `A depends on B` edge.
- `docs/generated/resilience-report.md` — SPOFs, single-region P0s, RTO/RPO matrix, FMEA risk register, stale restore tests.

Try it without installing anything:

```bash
python -m fortcloud_atlas check --model examples/hybrid-multicloud/model --out /tmp/atlas-demo
```

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

## CLI

```bash
fortcloud-atlas validate [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-atlas graph    [--model DIR] [--out DIR]
fortcloud-atlas report   [--model DIR] [--out DIR]
fortcloud-atlas check    [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors — handy once your model is clean. Exit code is `0` on success, `1` otherwise, so the commands drop straight into CI.

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — SPOF, FMEA, RTO/RPO](docs/concepts.md)
- [Service levels and error budgets](docs/guides/service-levels.md)
- [Reference views (C4)](docs/architecture/system-context.md)
- [Architecture decisions](docs/adrs/0001-yaml-as-source-of-truth.md)
- [Runbook template](docs/templates/runbook.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` and to the rules in `src/fortcloud_atlas/validate.py` require a test.

## License

MIT — see [LICENSE](LICENSE).

Part of the **Fortcloud** tool family: *Keep the cloud standing.*
