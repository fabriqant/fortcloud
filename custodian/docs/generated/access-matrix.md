# Fortcloud Custodian — Access Matrix

> Generated on 2026-11-21 by `fortcloud-custodian access`. Do not edit by hand.

Least privilege means explicit permissions, one environment per identity,
a reason for elevated roles and an expiry date on every grant.

| Grant | Principal | Type | Environment | Class. | Role | # Perms | Expires | Term | Status |
|---|---|---|---|---|---|---|---|---|---|
| `grant-alice-admin` | `alice` | Humain | `dev` | Interne | admin | 4 | 2026-12-31 | active | OK |
| `grant-alice-dev` | `alice` | Humain | `dev` | Interne | developer | 3 | 2027-06-30 | active | OK |
| `grant-alice-overprivileged` | `alice` | Humain | `staging` | Confidentiel | developer | 9 | 2027-06-30 | active | AT RISK |
| `grant-alice-prod-read` | `alice` | Humain | `prod` | Restreint | viewer | 2 | 2026-12-31 | active | OK |
| `grant-ci-legacy-dev` | `ci-legacy` | CI | `dev` | Interne | viewer | 1 | 2027-06-30 | active | OK |
| `grant-ci-prod-deploy` | `ci-deploy` | CI | `prod` | Restreint | deployer | 4 | 2027-06-30 | active | OK |
| `grant-ci-staging-deploy` | `ci-staging` | CI | `staging` | Confidentiel | deployer | 2 | 2027-06-30 | active | OK |
| `grant-svc-checkout` | `svc-checkout` | Service | `prod` | Restreint | runtime | 2 | 2027-06-30 | active | OK |
| `grant-svc-reporting` | `svc-reporting` | Service | `staging` | Confidentiel | runtime | 2 | 2027-06-30 | active | OK |

## Environments

| Environment | Classification | Owner | Principals | Grants | Secrets | Pipelines |
|---|---|---|---|---|---|---|
| `dev` — Développement | Interne | platform-team | 2 | 3 | 0 | 0 |
| `prod` — Production | Restreint | platform-team | 4 | 3 | 3 | 3 |
| `staging` — Préproduction | Confidentiel | platform-team | 3 | 3 | 3 | 1 |

## Elevated and broad grants

- `grant-alice-admin` — role `admin`, 4 permissions, expires 2026-12-31.
- `grant-alice-overprivileged` — role `developer`, 9 permissions, expires 2027-06-30.
  - **Gap:** 9 permissions exceed the maximum of 8.

## Links

- [Secret inventory](secret-inventory.md)
- [Change control](change-control.md)
- [Machine-readable status](custodian-status.json)
