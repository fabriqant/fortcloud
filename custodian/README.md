# FortCloud Custodian

### Guard access. Prove every change.

> **A control that cannot be shown in a pull request is a control that does not exist.**

[![CI](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriqant/fortcloud-io/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

FortCloud Custodian turns a hand-maintained YAML model of identities, secrets, deployment pipelines and audit controls into an **access matrix**, a **secret inventory**, a **change-control report**, an **audit trail** and a **machine-readable CI status**. It answers four questions:

| Requirement | Where it is enforced | What Custodian checks |
|---|---|---|
| **Apply least privilege** | `access.yaml` → `grants` | Explicit permissions, no wildcards, permission count, expiry, approved elevated roles |
| **Separate environments** | `access.yaml` → `environments`, `principals`, `grants` | One identity per environment, grants inside the principal scope, no cross-environment resources, isolated secrets |
| **Protect secrets** | `secrets.yaml` | References only (never values), rotation policy and age, environment isolation, declared consumers |
| **Log sensitive operations** | `audit.yaml` | Every sensitive operation logged into a declared, immutable, durable sink with fresh evidence |
| **Automate deployments with review, tests and rollback** | `changes.yaml` | Required review, enough approvers, unit + integration + security tests, scoped deployer, verified automated rollback |

[← Back to the FortCloud-io family README](../README.md) · [Previous tool: FortCloud Vitals](../vitals/README.md) · [Next tool: FortCloud Crucible](../crucible/README.md) — rehearse the outage before it happens.

> **Where the code lives:** this tool is the `custodian/` folder of the [`fabriqant/fortcloud-io`](https://github.com/fabriqant/fortcloud-io) repository. It has its own model and does not depend on Atlas, Failover, Ark, Ballast or Vitals at runtime. The GitHub Actions workflow stays at the repository root.

## Why

Vitals shows whether you can see a breach; Custodian shows whether access and changes were controlled in the first place. Common failures are boring and expensive:

- a CI identity that holds `*:*` forever and can reach both staging and production;
- a production secret copied into a staging config, or rotated only every 180 days;
- a deployment with one reviewer, no security test and a rollback nobody has tried since January;
- an audit bucket with 30-day retention and write access — an incident report that cannot be trusted.

Custodian makes these trade-offs explicit and reviewable before the next access review or post-mortem.

## 30-second quickstart

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/custodian
python -m pip install -e .

fortcloud-custodian check
```

Result in `docs/generated/`:

- `access-matrix.md` — every grant, its scope, expiry and least-privilege status,
- `secret-inventory.md` — references, stores, rotation and isolation,
- `change-control.md` — review, tests and rollback per pipeline,
- `audit-trail.md` — log sinks and sensitive operations with evidence,
- `custodian-status.json` — the same facts, machine-readable for CI.

Requirements: Python 3.9+ plus `PyYAML` and `jsonschema`, installed automatically.

## What it checks

### Access and least privilege

| Rule | Severity |
|---|---|
| YAML files conform to the JSON Schemas in `schema/` | Error |
| Identifiers are unique and every reference points to a real principal, environment or sink | Error |
| A grant's environment is inside the principal's allowed scope | Error |
| A resource explicitly targets a different declared environment | Error |
| A wildcard permission (`*`, `*:*`, `read:*`) | Error |
| An expired grant, or an elevated role without expiry | Error |
| More than 8 permissions on a single grant | Warning |
| A CI identity spanning several environments | Warning |
| An elevated role that is not time-bound | Error |
| A grant on a restricted environment without approval | Warning |
| Access without an expiry date | Warning |
| An expiry further than 365 days away | Warning |

### Secrets

| Rule | Severity |
|---|---|
| A `value` key in the model — the schema only allows a `reference` | Error |
| A secret shared with a restricted environment | Error |
| A restricted secret past its rotation policy | Error |
| A consumer that does not exist, or has no access to the secret's environments | Error |
| An invalid rotation date | Error |
| A secret shared between two non-restricted environments | Warning |
| Rotation overdue on a non-restricted environment | Warning |
| A rotation policy above 90 days | Warning |
| A Kubernetes Secret in a restricted environment | Warning |

### Changes and deployments

| Rule | Severity |
|---|---|
| A restricted environment without mandatory review | Error |
| A restricted environment missing unit or integration tests | Error |
| A deployer that is unknown or not scoped to the target environment | Error |
| A restricted environment without rollback | Error |
| Fewer than 2 approvers on a restricted environment | Warning |
| No security test in a pipeline | Warning |
| Rollback never verified, or verification older than 90 days | Warning |
| Manual rollback on a restricted environment | Warning |

### Audit trail

| Rule | Severity |
|---|---|
| A sensitive operation that is not logged | Error |
| A logged operation with no declared sink | Error |
| An audit control with `result: failed` | Error |
| A sink with less than 365 days of retention | Warning |
| A mutable log sink | Warning |
| An operation without evidence, or evidence older than 90 days | Warning |
| No logged operation for `grant_change`, `secret_access`, `deploy` or `pipeline_change` | Warning |

## Model layout

Custodian uses its **own four files**, one per responsibility:

```text
model/
├── access.yaml   # environments, principals, grants (least privilege + separation)
├── secrets.yaml  # secret references, rotation, consumers
├── changes.yaml  # deployment pipelines, review, tests, rollback
└── audit.yaml    # log sinks and sensitive operations
```

Point the CLI at your own directory with `--model /path/to/your/model`. The example in `examples/hybrid-multicloud/` is a complete, working sample — replace it, don't edit the generated files.

### What an entry looks like

`access.yaml`:

```yaml
version: 1
environments:
  - id: prod
    name: Production
    classification: restricted
    owner: platform-team
principals:
  - id: ci-deploy
    name: Deployment runner
    type: ci
    owner: platform-team
    environments: [prod]
grants:
  - id: grant-ci-prod-deploy
    principal: ci-deploy
    role: deployer
    environment: prod
    permissions: [deploy:create, deploy:rollback, secrets:read]
    resources: [proj/prod/checkout/*]
    expires: "2027-06-30"
    approval: change-board
```

`secrets.yaml`:

```yaml
version: 1
secrets:
  - id: sec-checkout-db
    name: Checkout database password
    store: vault
    reference: vault://prod/checkout/db
    environments: [prod]
    owner: platform-team
    last_rotated: "2026-10-01"
    rotation_days: 90
    used_by: [ci-deploy]
```

`changes.yaml`:

```yaml
version: 1
pipelines:
  - id: pipe-checkout-prod
    name: Checkout deployment in production
    environment: prod
    trigger: tag
    deployer: ci-deploy
    owner: commerce-team
    review:
      required: true
      approvers: 2
    tests: [unit, integration, security]
    rollback:
      enabled: true
      target: previous-release
      verified: "2026-11-15"
      automate: true
```

`audit.yaml`:

```yaml
version: 1
sinks:
  - id: sink-siem
    name: Centralized SIEM
    type: siem
    destination: https://siem.example.com/events
    retention_days: 365
    immutable: true
    owner: sec-team
operations:
  - id: op-deploy
    name: Production deployments
    kind: deploy
    environment: prod
    logged: true
    sink: sink-siem
    evidence: https://ci.example.com/custodian/deploy-119
    last_evidence: "2026-11-19"
    result: passed
    owner: platform-team
```

## Generated output (excerpt)

From `docs/generated/access-matrix.md` on the bundled example:

| Grant | Principal | Environment | Role | # Perms | Status |
|---|---|---|---|---|---|
| `grant-alice-admin` | `alice` | `dev` | admin | 4 | OK — time-bound and approved |
| `grant-ci-prod-deploy` | `ci-deploy` | `prod` | deployer | 4 | OK |
| `grant-alice-overprivileged` | `alice` | `staging` | developer | 9 | AT RISK |

And from `change-control.md`:

| Pipeline | Env | Review | Approvers | Rollback | Status |
|---|---|---|---|---|---|
| `pipe-checkout-prod` | `prod` | yes | 2 | auto, verified 2026-11-15 | OK |
| `pipe-reporting-prod` | `prod` | yes | 1 | auto, verified 2026-01-01 | AT RISK |
| `pipe-legacy-prod` | `prod` | yes | 2 | manual | AT RISK |

The bundled example intentionally contains 7 warnings so you can see the checks in action. Once your own model is clean, run `check --strict` in CI.

## CLI

```bash
fortcloud-custodian validate  [--model DIR] [--schema-dir DIR] [--strict]
fortcloud-custodian access    [--model DIR] [--out DIR]
fortcloud-custodian secrets   [--model DIR] [--out DIR]
fortcloud-custodian changes   [--model DIR] [--out DIR]
fortcloud-custodian audit     [--model DIR] [--out DIR]
fortcloud-custodian check     [--model DIR] [--out DIR] [--strict]
```

`--strict` turns warnings into errors. Exit code is `0` on success, `1` on validation failure, `2` on CLI usage error.

## Continuous integration

The root workflow has a dedicated job with `working-directory: custodian`, `cache-dependency-path: custodian/requirements.txt` and an artifact named `fortcloud-custodian-access` containing `custodian/artifacts`. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

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
└── custodian/                  # this tool
    ├── README.md
    ├── pyproject.toml          # package fortcloud-custodian, CLI fortcloud-custodian
    ├── schema/                 # 4 JSON Schemas — the model contracts
    ├── src/fortcloud_custodian/
    ├── examples/hybrid-multicloud/model/
    ├── docs/
    ├── tests/                  # 20 unit tests
    └── LICENSE
```

## Documentation

- [Overview](docs/index.md)
- [Quickstart](docs/quickstart.md)
- [Concepts — access, environments, secrets, changes, audit](docs/concepts.md)
- [Least privilege guide](docs/guides/least-privilege.md)
- [Secrets guide](docs/guides/secrets.md)
- [Change control guide](docs/guides/changes.md)
- [ADR 0001 — controls as versioned model](docs/adrs/0001-controls-as-model.md)
- [Change record template](docs/templates/change.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `schema/` or to the rules in `src/fortcloud_custodian/validate.py` require a test. Run the suite from this folder:

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Part of the **FortCloud** tool family: *Keep the cloud standing.*
