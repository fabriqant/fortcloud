# FortCloud Ark

### Restore is a feature, not a hope

> **A backup you have never restored is a rumour.**

[![CI](https://github.com/fabriqant/fortcloud/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

FortCloud Ark turns a hand-maintained YAML model of your data assets, backup policies and restore tests into a **backup coverage matrix**, a **restore evidence report**, a **recovery plan** and a **machine-readable CI status**. It catches the gaps that only show up during an incident: an untested restore, a backup schedule that cannot meet the RPO, a missing immutable copy, or a drill from four months ago.

[← Back to the FortCloud family README](../README.md) · [Previous tool: FortCloud Failover](../failover/README.md) · [Next tool: FortCloud Ballast](../ballast/README.md) — keep workloads steady when parts fail.

> **Where the code lives:** this tool is the `ark/` folder of the [`fabriqant/fortcloud`](https://github.com/fabriqant/fortcloud) repository. It has its own model and does not depend on Atlas or Failover at runtime. The GitHub Actions workflow stays at the repository root.

## Why

Atlas maps the risk, Failover proves the switchover, Ark proves the **data comes back**. The three questions are different:

| Tool | Question |
|---|---|
| Atlas | Which dependencies can fail, and what is the blast radius? |
| Failover | Can we switch to the standby within the RTO? |
| **Ark** | Can we restore the data within the RTO and RPO, with evidence? |

A backup is only real when a dated test has measured the restore. Ark makes that evidence a first-class, versioned artifact instead of a slide in a governance deck.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud.git
cd fortcloud/ark
python -m pip install -e .

fortcloud-ark check
```

Result in `docs/generated/`:

- `backup-coverage.md` — per-asset coverage and status,
- `restore-evidence.md` — measured RTO/RPO versus targets, with evidence links,
- `recovery-plan.md` — ordered remediation steps with owners,
- `restore-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique and references point to real assets, backups and services | Error |
| A P0 asset has a backup policy | Error |
| A P0 backup is immutable | Error |
| Sensitive assets are encrypted at rest, on source and backup | Error |
| Backup schedule is compatible with the tightest service RPO | Error |
| A P0 asset has a restore test | Error |
| Measured RTO/RPO are below the service targets | Error |
| P0 retention below 30 days, or no cross-region copy | Warning |
| Last successful backup older than 2 days | Warning |
| Restore test older than 90 days, or no deletion/ransomware scenario for P0 | Warning |
| Restore result is not `passed`, or has no evidence link | Warning |

Durations use `0` (continuous/CDC) or `<number><s|m|h|d>`, and can be combined: `1h30m`, `2m12s`. Quote zero values in YAML: `rpo: "0"`.

## Model layout

Ark uses its **own four files** — it does not read Atlas's or Failover's models:

```text
model/
├── assets.yaml     # data assets: category, criticality, classification, encryption
├── backups.yaml    # policies: type, schedule, retention, immutability, freshness
├── restores.yaml   # dated evidence: scenario, measured RTO/RPO, result, link
└── services.yaml   # business services: criticality, RTO, RPO, assets
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What an entry looks like

`assets.yaml`:

```yaml
version: 1
assets:
  - id: pg-core
    name: Primary transactional database
    category: database
    criticality: P0
    classification: confidential
    owner: data-platform
    provider: cloud eu-west-1
    region: eu-west-1
    encryption_at_rest: true
```

`backups.yaml`:

```yaml
version: 1
backups:
  - id: bk-pg
    asset: pg-core
    type: cdc
    schedule: 5m
    retention_days: 35
    immutable: true
    cross_region: true
    encrypted: true
    last_successful: "2026-11-20"
```

`restores.yaml`:

```yaml
version: 1
restores:
  - id: rst-pg
    backup: bk-pg
    scenario: point_in_time
    last: "2026-11-08"
    measured_rto: 26m
    measured_rpo: 4m
    result: passed
    evidence: https://ci.example.com/restores/rst-pg-42
    owner: data-platform
```

`services.yaml`:

```yaml
version: 1
services:
  - id: order-to-cash
    name: Order to cash
    criticality: P0
    owner: commerce-team
    rto: 30m
    rpo: 5m
    assets: [pg-core]
```

## Generated output (excerpt)

From `docs/generated/backup-coverage.md` on the bundled example:

| Asset | Backup | Last backup | Last restore | Status |
|---|---|---|---|---|
| `pg-core` | `bk-pg` | 1 d | 13 d (passed) | PROVEN |
| `obj-lake` | `bk-lake` | 2 d | 27 d (passed) | PROVEN |
| `vault-secrets` | `bk-vault` | **3 d (stale)** | **129 d (stale)** | AT RISK |

And from `restore-evidence.md`:

| Restore | Asset | Scenario | Meas. RTO | Target RTO | Meas. RPO | Target RPO | Result |
|---|---|---|---|---|---|---|---|
| `rst-pg` | `pg-core` | point in time | 26m | 30m | 4m | 5m | passed |
| `rst-vault` | `vault-secrets` | region loss | 12m | 15m | 0 | 0 | passed |

The bundled example intentionally contains 7 warnings. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-ark validate   [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-ark coverage   [--model DIR] [--out DIR]
fortcloud-ark evidence   [--model DIR] [--out DIR]
fortcloud-ark plan       [--model DIR] [--out DIR]
fortcloud-ark check      [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: ark`, `cache-dependency-path: ark/requirements.txt` and an artifact named `fortcloud-ark-evidence` containing `ark/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Repository layout

```text
fortcloud/
├── .github/workflows/ci.yml
├── README.md                  # family overview
├── atlas/                     # dependency and risk map
├── failover/                  # failover plans and coverage
└── ark/                       # this tool
    ├── README.md
    ├── pyproject.toml         # package fortcloud-ark, CLI fortcloud-ark
    ├── schema/                # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_ark/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                 # 19 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — evidence, RPO, immutability](docs/concepts.md)
- [Restore testing guide](docs/guides/restore-testing.md)
- [ADR 0001 — evidence over snapshots](docs/adrs/0001-evidence-over-snapshots.md)
- [Restore report template](docs/templates/restore.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_ark/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **FortCloud** tool family: *Keep the cloud standing.*
