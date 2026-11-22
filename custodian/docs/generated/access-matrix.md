# FortCloud Custodian — Access Matrix

> Generated on 2026-11-21 by `fortcloud-custodian access`. Do not edit by hand.

Least privilege means explicit permissions, one environment per identity,
a reason for elevated roles and an expiry date on every grant.

| Grant | Principal | Type | Environment | Class. | Role | # Perms | Expires | Term | Status |
|---|---|---|---|---|---|---|---|---|---|
| `grant-alice-admin` | `alice` | Human | `dev` | Internal | admin | 4 | 2026-12-31 | active | OK |
| `grant-alice-dev` | `alice` | Human | `dev` | Internal | developer | 3 | 2027-06-30 | active | OK |
| `grant-alice-overprivileged` | `alice` | Human | `staging` | Confidential | developer | 9 | 2027-06-30 | active | AT RISK |
| `grant-alice-prod-read` | `alice` | Human | `prod` | Restricted | viewer | 2 | 2026-12-31 | active | OK |
| `grant-ci-legacy-dev` | `ci-legacy` | CI | `dev` | Internal | viewer | 1 | 2027-06-30 | active | OK |
| `grant-ci-prod-deploy` | `ci-deploy` | CI | `prod` | Restricted | deployer | 4 | 2027-06-30 | active | OK |
| `grant-ci-staging-deploy` | `ci-staging` | CI | `staging` | Confidential | deployer | 2 | 2027-06-30 | active | OK |
| `grant-svc-checkout` | `svc-checkout` | Service | `prod` | Restricted | runtime | 2 | 2027-06-30 | active | OK |
| `grant-svc-reporting` | `svc-reporting` | Service | `staging` | Confidential | runtime | 2 | 2027-06-30 | active | OK |

## Environments

| Environment | Classification | Owner | Principals | Grants | Secrets | Pipelines |
|---|---|---|---|---|---|---|
| `dev` — Development | Internal | platform-team | 2 | 3 | 0 | 0 |
| `prod` — Production | Restricted | platform-team | 4 | 3 | 3 | 3 |
| `staging` — Staging | Confidential | platform-team | 3 | 3 | 3 | 1 |

## Elevated and broad grants

- `grant-alice-admin` — role `admin`, 4 permissions, expires 2026-12-31.
- `grant-alice-overprivileged` — role `developer`, 9 permissions, expires 2027-06-30.
  - **Gap:** 9 permissions exceed the maximum of 8.

## Links

- [Secret inventory](secret-inventory.md)
- [Change control](change-control.md)
- [Machine-readable status](custodian-status.json)
