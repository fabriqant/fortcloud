# Fortcloud-io

### Cloud resilience tooling for hybrid and multi-cloud infrastructure

> **Keep the cloud standing.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)

Fortcloud is a family of small, independent engineering tools that make infrastructure risk explicit, testable and reviewable in a pull request. This repository hosts the family. It contains all seven tools — **Atlas**, **Failover**, **Ark**, **Ballast**, **Vitals**, **Custodian** and **Crucible** — each in its own folder with its own package, CLI, model, tests and documentation.

The common thread is simple: **no backend, no agent, no platform to adopt** — just versioned files, a CLI and CI checks.

## The seven tools

| # | Need | Tool | Folder | Status | Tagline |
|---|---|---|---|---|---|
| 1 | Map dependencies and risks | **Fortcloud Atlas** | [`atlas/`](atlas/README.md) | **Available — v0.1.0** | *Map every dependency. See every risk.* |
| 2 | Eliminate single points of failure | **Fortcloud Failover** | [`failover/`](failover/README.md) | **Available — v0.1.0** | *Design out the single point of failure.* |
| 3 | Protect data and prove restoration | **Fortcloud Ark** | [`ark/`](ark/README.md) | **Available — v0.1.0** | *Restore is a feature, not a hope.* |
| 4 | Keep request paths stable under failure | **Fortcloud Ballast** | [`ballast/`](ballast/README.md) | **Available — v0.1.0** | *Keep workloads steady when parts fail.* |
| 5 | Service and data quality monitoring | **Fortcloud Vitals** | [`vitals/`](vitals/README.md) | **Available — v0.1.0** | *Health and data quality, one signal.* |
| 6 | Secure access and changes | **Fortcloud Custodian** | [`custodian/`](custodian/README.md) | **Available — v0.1.0** | *Guard access. Prove every change.* |
| 7 | Exercise failure scenarios | **Fortcloud Crucible** | [`crucible/`](crucible/README.md) | **Available — v0.1.0** | *Rehearse the outage before it happens.* |

All seven tools are also available through one optional **web console** prototype: [`web/`](web/README.md) — a local FastAPI + React interface with guided forms, a YAML editor, dashboards, staged import review and generated artifacts. It consumes the tools; it does not change them. An optional local read-only AWS connector can propose an Atlas inventory, but no credentials reach the console.

Each tool can be adopted alone. All seven are separate packages with **independent models** and separate CLIs. They answer different questions:

| Tool | Question |
|---|---|
| Atlas | Where is the risk, and what is the blast radius? |
| Failover | Can we switch to the standby within the RTO? |
| Ark | Can we restore the data within the RTO/RPO, with evidence? |
| Ballast | Can the request chain still meet its latency budget when a dependency fails? |
| Vitals | Can we see a breach early enough, with credible SLOs and data quality? |
| Custodian | Is access least-privileged, are secrets safe, and can every change be reviewed, reversed and audited? |
| Crucible | Have we actually rehearsed restore, failover and recovery, with roles, communication and verified results? |

## Repository layout

```text
fortcloud-io/
├── .github/
│   └── workflows/ci.yml        # one workflow, one job per tool, one for the web console
├── README.md                   # this file — family overview
├── web/                        # optional local web console (FastAPI + React) and connectors
├── atlas/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-atlas, CLI: fortcloud-atlas
│   ├── schema/
│   ├── src/fortcloud_atlas/
│   ├── examples/
│   ├── docs/
│   └── tests/
├── failover/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-failover, CLI: fortcloud-failover
│   ├── schema/
│   ├── src/fortcloud_failover/
│   ├── examples/
│   ├── docs/
│   └── tests/
├── ark/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-ark, CLI: fortcloud-ark
│   ├── schema/
│   ├── src/fortcloud_ark/
│   ├── examples/
│   ├── docs/
│   └── tests/
├── ballast/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-ballast, CLI: fortcloud-ballast
│   ├── schema/
│   ├── src/fortcloud_ballast/
│   ├── examples/
│   ├── docs/
│   └── tests/
├── vitals/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-vitals, CLI: fortcloud-vitals
│   ├── schema/
│   ├── src/fortcloud_vitals/
│   ├── examples/
│   ├── docs/
│   └── tests/
├── custodian/
│   ├── README.md
│   ├── pyproject.toml          # package: fortcloud-custodian, CLI: fortcloud-custodian
│   ├── schema/
│   ├── src/fortcloud_custodian/
│   ├── examples/
│   ├── docs/
│   └── tests/
└── crucible/
    ├── README.md
    ├── pyproject.toml          # package: fortcloud-crucible, CLI: fortcloud-crucible
    ├── schema/
    ├── src/fortcloud_crucible/
    ├── examples/
    ├── docs/
    └── tests/
```

> GitHub Actions only discovers workflows under `.github/workflows/` at the **repository root**. That is why CI lives there. Each job overrides `working-directory` to its tool folder and uses its own dependency cache path.

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

Read the [Atlas README](atlas/README.md) for the CLI, the model format and the full documentation index. If the terminology is new, start with [Atlas explained simply](atlas/docs/explained.md) — a plain-language walkthrough with a glossary.

## Continue with Failover

```bash
cd fortcloud-io/failover
python -m pip install -e .

fortcloud-failover check
```

This writes a failover coverage matrix, a remediation plan, a drill checklist and a machine-readable status. Read the [Failover README](failover/README.md).

## Continue with Ark

```bash
cd fortcloud-io/ark
python -m pip install -e .

fortcloud-ark check
```

This writes a backup coverage matrix, a restore evidence report, a recovery plan and a machine-readable status. Read the [Ark README](ark/README.md).

## Continue with Ballast

```bash
cd fortcloud-io/ballast
python -m pip install -e .

fortcloud-ballast check
```

This writes a timeout budget report, a resilience policy matrix, a remediation plan and a machine-readable status. Read the [Ballast README](ballast/README.md).

## Continue with Vitals

```bash
cd fortcloud-io/vitals
python -m pip install -e .

fortcloud-vitals check
```

This writes an SLO dashboard, a signal catalog, a quality plan and a machine-readable status. Read the [Vitals README](vitals/README.md).

## Continue with Custodian

```bash
cd fortcloud-io/custodian
python -m pip install -e .

fortcloud-custodian check
```

This writes an access matrix, a secret inventory, a change-control report, an audit trail and a machine-readable status. Read the [Custodian README](custodian/README.md).

## Finish with Crucible

```bash
cd fortcloud-io/crucible
python -m pip install -e .

fortcloud-crucible check
```

This writes a scenario plan, a roles matrix, a communication plan, a verification report and a machine-readable status. Read the [Crucible README](crucible/README.md).

## Web console (optional)

A local FastAPI + React console gives all seven tools one interface with guided forms, a YAML editor, dashboards and generated artifacts. It imports the tool packages in-process; it is not an eighth tool.

```bash
python -m pip install -r web/requirements.txt
cd web/ui && npm install && npm run build && cd ../..
python -m uvicorn api.main:app --app-dir web --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. See the [web console README](web/README.md) for the staged import workflow and the optional local read-only AWS connector.

## Design principles

1. **The model is the source of truth.** Four small YAML files per tool, reviewed in PRs, validated in CI.
2. **Generated files are disposable.** Diagrams, reports and plans are rebuilt, never hand-edited.
3. **CI-friendly.** Every CLI command returns `0` or `1`; `--strict` escalates warnings.
4. **Hybrid / multi-cloud aware.** Redundancy is measured across instances, zones, regions and providers — a single IdP or DNS still counts as a SPOF.
5. **Standalone by default.** A tool must be installable and usable without the rest of the family.
6. **Evidence over claims.** An RTO is only credible if a dated restore test — or a dated, successful failover drill — exists, with service and data verification and a named verifier.
7. **Rehearse before production.** A failed drill in an isolated environment is a lesson; the first attempt in production is an incident.

## Roadmap

- [x] **Atlas** — dependency mapping, SPOF audit, RTO/RPO matrix, FMEA register.
- [x] **Failover** — coverage matrix, remediation plan, drill checklist, CI status.
- [x] **Ark** — backup coverage, restore evidence, recovery plan, CI status.
- [x] **Ballast** — timeout budgets, policy matrix, resilience plan, CI status.
- [x] **Vitals** — SLO dashboard, signal catalog, error budgets, quality plan, CI status.
- [x] **Custodian** — least privilege, environment separation, secret protection, change control and audit trail.
- [x] **Crucible** — controlled-first restore/failover/recovery drills, roles, communication, verification and CI status.

## Contributing

See the `CONTRIBUTING.md` of each tool ([Atlas](atlas/CONTRIBUTING.md), [Failover](failover/CONTRIBUTING.md), [Ark](ark/CONTRIBUTING.md), [Ballast](ballast/CONTRIBUTING.md), [Vitals](vitals/CONTRIBUTING.md), [Custodian](custodian/CONTRIBUTING.md), [Crucible](crucible/CONTRIBUTING.md)) for the development workflow. New tools should follow the same layout: a folder named after the tool, its own `pyproject.toml`, model, CLI, tests and docs, plus a job at the repository root.

## License

The tools are MIT licensed — see [Atlas](atlas/LICENSE), [Failover](failover/LICENSE), [Ark](ark/LICENSE), [Ballast](ballast/LICENSE), [Vitals](vitals/LICENSE), [Custodian](custodian/LICENSE) and [Crucible](crucible/LICENSE).
