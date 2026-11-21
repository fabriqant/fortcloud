# Fortcloud-io

### Cloud resilience tooling for hybrid and multi-cloud infrastructure

> **Keep the cloud standing.**

[![Atlas CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)

Fortcloud is a family of small, independent engineering tools that make infrastructure risk explicit, testable and reviewable in a pull request. This repository hosts the family. Today it contains **Atlas**; the other tools are planned and will live in their own folders with their own package, CLI, tests and documentation.

The common thread is simple: **no backend, no agent, no platform to adopt** — just versioned files, a CLI and CI checks.

## The seven tools

| # | Need | Tool | Folder | Status | Tagline |
|---|---|---|---|---|---|
| 1 | Map dependencies and risks | **Fortcloud Atlas** | [`atlas/`](atlas/README.md) | **Available — v0.1.0** | *Map every dependency. See every risk.* |
| 2 | Eliminate single points of failure | Fortcloud Failover | `failover/` | Planned | *Design out the single point of failure.* |
| 3 | Protect data and prove restoration | Fortcloud Ark | `ark/` | Planned | *Restore is a feature, not a hope.* |
| 4 | Fault-tolerant processing | Fortcloud Ballast | `ballast/` | Planned | *Keep workloads steady when parts fail.* |
| 5 | Service and data quality monitoring | Fortcloud Vitals | `vitals/` | Planned | *Health and data quality, one signal.* |
| 6 | Secure access and changes | Fortcloud Custodian | `custodian/` | Planned | *Guard access. Prove every change.* |
| 7 | Exercise failure scenarios | Fortcloud Crucible | `crucible/` | Planned | *Rehearse the outage before it happens.* |

Each tool can be adopted alone. Atlas does not require Failover, and Failover will not require Atlas at runtime — they may optionally consume the same YAML model, but they are separate packages.

## Repository layout

```text
fortcloud-io/
├── .github/
│   └── workflows/ci.yml        # CI for the tools present in this repo
├── README.md                   # this file — family overview
└── atlas/
    ├── README.md               # tool overview and quickstart
    ├── pyproject.toml          # package: fortcloud-atlas, CLI: fortcloud-atlas
    ├── schema/                 # JSON Schemas — the model contracts
    ├── src/fortcloud_atlas/    # implementation
    ├── examples/               # working hybrid/multi-cloud sample
    ├── docs/                   # concepts, guides, C4 views, ADRs, runbook template
    ├── tests/
    └── .github/                # (none) — workflows live at the repository root
```

> GitHub Actions only discovers workflows under `.github/workflows/` at the **repository root**. That is why the CI file is not inside `atlas/`. Its `working-directory` is set to `atlas/`.

## Start with Atlas

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/atlas
python -m pip install -e .

fortcloud-atlas check
```

This validates the example model and writes:

- `docs/generated/dependency-graph.md` — the Mermaid dependency graph,
- `docs/generated/resilience-report.md` — SPOFs, RTO/RPO matrix and FMEA risk register.

Read the [Atlas README](atlas/README.md) for the CLI, the model format and the full documentation index.

## Design principles

1. **The model is the source of truth.** Four small YAML files, reviewed in PRs, validated in CI.
2. **Generated files are disposable.** Diagrams and reports are rebuilt, never hand-edited.
3. **CI-friendly.** Every CLI command returns `0` or `1`; `--strict` escalates warnings.
4. **Hybrid / multi-cloud aware.** Redundancy is measured across instances, zones, regions and providers — a single IdP or DNS still counts as a SPOF.
5. **Standalone by default.** A tool must be installable and usable without the rest of the family.
6. **Evidence over claims.** An RTO is only credible if a dated restore test exists.

## Roadmap

- [x] **Atlas** — dependency mapping, SPOF audit, RTO/RPO matrix, FMEA register.
- [ ] **Failover** — turn the SPOF audit into remediation plans and failover checks.
- [ ] **Ark** — automated restore verification with evidence attached to each flow.
- [ ] **Ballast** — fault-tolerant processing policies (timeouts, retries, circuit breakers, bulkheads).
- [ ] **Vitals** — service health and data quality signals tied to SLOs.
- [ ] **Custodian** — least-privilege access and change verification for IaC and pipelines.
- [ ] **Crucible** — failure-scenario drills with measured RTO versus declared RTO.

## Contributing

See [`atlas/CONTRIBUTING.md`](atlas/CONTRIBUTING.md) for the development workflow. New tools should follow the same layout: a folder named after the tool, its own `pyproject.toml`, CLI, tests and docs, plus a CI job at the repository root.

## License

The tools are MIT licensed — see [`atlas/LICENSE`](atlas/LICENSE).
