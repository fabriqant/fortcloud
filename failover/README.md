# Fortcloud Failover

### Design out the single point of failure

> **A redundancy claim is not a failover plan.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fortcloud Failover turns a hand-maintained YAML model of your failover topology into a **coverage matrix**, a **remediation plan**, a **drill checklist** and a **machine-readable CI status**. It catches false redundancy before an outage does: a standby in the same region, a capacity too small to absorb the load, a switchover slower than the RTO, or a drill that has gone stale.

[← Back to the Fortcloud-io family README](../README.md) · [Next tool: Fortcloud Ark](../ark/README.md) — restore is a feature, not a hope.

> **Where the code lives:** this tool is the `failover/` folder of the [`fabriqant/fortcloud-io`](https://github.com/fabriqant/fortcloud-io) repository. It has its **own model** and does not depend on Atlas at runtime. The GitHub Actions workflow stays at the repository root.

## Why

Atlas tells you *where* the single point of failure is. Failover tells you *what to do about it* and *how to prove it works*. The gap between the two is where most resilience claims die:

- two instances in the same region are not redundancy — they are two things to lose at once;
- a standby with half the capacity will fail during the promotion;
- a 26-minute switchover cannot satisfy a 30-minute RTO once detection is included;
- `async` replication cannot satisfy `RPO: 0`;
- a drill from four months ago is a memory, not evidence.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/failover
python -m pip install -e .

fortcloud-failover check
```

Result in `docs/generated/`:

- `failover-matrix.md` — coverage per strategy and per service,
- `failover-plan.md` — ordered remediation steps with owners,
- `drill-scenarios.md` — a seven-step checklist per strategy,
- `failover-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique and every reference points to a real component or strategy | Error |
| Primary and standby share the same `pair`, with the right roles | Error |
| Both instances are in the same region (false redundancy) | Error |
| `detection_time + promotion_time` exceeds the tightest RTO | Error |
| `async`/`none` replication with an `RPO: 0` service | Error |
| A P0 component in a service has no failover strategy | Error |
| Both instances use the same provider | Warning |
| Standby capacity is lower than primary capacity | Warning |
| DNS TTL exceeds the RTO | Warning |
| Switchover is manual for a P0 service | Warning |
| No drill, or a drill older than 90 days | Warning |
| Drill result is not `passed`, or has no evidence link | Warning |

Durations use `0` or `<number><s|m|h|d>`, and can be combined: `1h30m`, `2m12s`.

## Model layout

Failover uses its **own four files** — it does not read Atlas's model:

```text
model/
├── topology.yaml     # component inventory: role, pair, region, provider, capacity, health check
├── services.yaml     # business services: criticality, RTO, RPO, owner, components
├── strategies.yaml   # primary → standby, mode, replication, detection/promotion, DNS TTL
└── drills.yaml       # dated drill evidence: scenario, result, duration, evidence link
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What an entry looks like

`topology.yaml`:

```yaml
version: 1
topology:
  - id: pg-core
    name: Primary transactional database
    criticality: P0
    owner: data-platform
    provider: cloud eu-west-1
    region: eu-west-1
    zone: az1
    role: primary
    pair: pg
    capacity: 100
    health_check: https://pg.internal/health
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
    components: [pg-core, dns-global, idp-oidc]
```

`strategies.yaml`:

```yaml
version: 1
strategies:
  - id: fo-pg
    primary: pg-core
    standby: pg-core-dr
    mode: active_passive
    replication: async
    detection_time: 1m
    promotion_time: 25m
    dns_ttl: 45m
    automated: false
    runbook: ../../docs/templates/drill.md
    owner: data-platform
```

`drills.yaml`:

```yaml
version: 1
drills:
  - id: drill-pg
    strategy: fo-pg
    scenario: region-loss
    last: "2026-10-12"
    duration: 27m30s
    result: partial
    evidence: https://ci.example.com/drills/fo-pg-31
    owner: data-platform
```

## Generated output (excerpt)

From `docs/generated/failover-matrix.md` on the bundled example:

| Strategy | Primary → Standby | Switchover / RTO | Last drill | Status |
|---|---|---|---|---|
| `fo-dns` | `dns-global` → `dns-global-dr` | 6m / 15m | 24 d | COVERED |
| `fo-idp` | `idp-oidc` → `idp-oidc-dr` | 2m30s / 15m | 16 d | AT RISK |
| `fo-pg` | `pg-core` → `pg-core-dr` | 26m / 30m | 40 d | AT RISK |
| `fo-vault` | `vault-secrets` → `vault-secrets-dr` | 11m / 15m | **129 d (stale)** | AT RISK |

The bundled example intentionally contains 7 warnings so you can see the checks in action. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-failover validate   [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-failover matrix     [--model DIR] [--out DIR]
fortcloud-failover plan       [--model DIR] [--out DIR]
fortcloud-failover drills     [--model DIR] [--out DIR]
fortcloud-failover check      [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: failover`, `cache-dependency-path: failover/requirements.txt` and an artifact named `fortcloud-failover-plan` containing `failover/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Repository layout

```text
fortcloud-io/
├── .github/workflows/ci.yml
├── README.md                  # family overview
├── atlas/                     # dependency and risk map
└── failover/                  # this tool
    ├── README.md
    ├── pyproject.toml         # package fortcloud-failover, CLI fortcloud-failover
    ├── schema/                # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_failover/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                 # 20 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — false redundancy, RTO budget, drill evidence](docs/concepts.md)
- [Drill guide](docs/guides/drills.md)
- [ADR 0001 — an independent model](docs/adrs/0001-standalone-model.md)
- [Drill template](docs/templates/drill.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_failover/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **Fortcloud** tool family: *Keep the cloud standing.*
