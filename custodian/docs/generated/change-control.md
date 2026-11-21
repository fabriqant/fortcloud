# Fortcloud Custodian — Change Control

> Generated on 2026-11-21 by `fortcloud-custodian changes`. Do not edit by hand.

A restricted environment requires a peer review, unit and integration
tests, an identified deployer and a verified, automated rollback.

| Pipeline | Env | Trigger | Deployer | Review | Approvers | Tests | Rollback | Mode | Status |
|---|---|---|---|---|---|---|---|---|---|
| `pipe-checkout-prod` — Déploiement commande en production | `prod` | tag | `ci-deploy` | yes | 2 | unit, integration, security, e2e | yes | auto | OK |
| `pipe-checkout-staging` — Déploiement commande en préproduction | `staging` | pull_request | `ci-staging` | yes | 1 | unit, integration, security | yes | auto | OK |
| `pipe-legacy-prod` — Déploiement historique en production | `prod` | manual | `ci-legacy` | yes | 2 | unit, integration, security | yes | manual | AT RISK |
| `pipe-reporting-prod` — Déploiement analytique en production | `prod` | manual | `ci-deploy` | yes | 1 | unit, integration, security | yes | auto | AT RISK |

## `pipe-legacy-prod`

- **Owner:** platform-team
- **Environment:** `prod`
- **Gap:** rollback is not automated for a restricted environment.

## `pipe-reporting-prod`

- **Owner:** analytics-team
- **Environment:** `prod`
- **Gap:** 1 approver(s) for a restricted environment (minimum 2).
- **Gap:** rollback verification is 324 days old (max 90).

Every remediation means editing the model and re-running `fortcloud-custodian check`.
