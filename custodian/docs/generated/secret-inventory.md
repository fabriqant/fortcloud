# Fortcloud Custodian — Secret Inventory

> Generated on 2026-11-21 by `fortcloud-custodian secrets`. Do not edit by hand.

Only **references** belong in this model. A secret shared between
environments, especially with production, breaks isolation.

| Secret | Store | Reference | Environments | Last rotated | Age | Policy | Users | Status |
|---|---|---|---|---|---|---|---|---|
| `sec-checkout-api` — Checkout gateway API key | Vault | `vault://prod/checkout/api` | `prod` | 2026-09-15 | 67d | 90d | 1 | OK |
| `sec-checkout-db` — Checkout database password | Vault | `vault://prod/checkout/db` | `prod` | 2026-10-01 | 51d | 90d | 2 | OK |
| `sec-ci-token` — CI deployment token | Vault | `vault://prod/ci/deploy-token` | `prod` | 2026-10-15 | 37d | 180d | 1 | AT RISK |
| `sec-legacy-token` — Legacy staging token | Kubernetes Secret | `${LEGACY_TOKEN_REF}` | `staging` | 2026-09-01 | 81d | 90d | 1 | OK |
| `sec-reporting-export-key` — Analytics export key | GCP Secret Manager | `gcp-secret-manager://staging/reporting/export-key` | `staging` | 2026-03-01 | 265d | 90d | 1 | AT RISK |
| `sec-staging-db` — Staging database password | AWS Secrets Manager | `aws-secrets-manager://staging/reporting/db` | `staging` | 2026-11-01 | 20d | 90d | 1 | OK |

## `sec-ci-token`

- **Owner:** platform-team
- **Reference:** `vault://prod/ci/deploy-token`
- **Gap:** rotation policy of 180 days exceeds 90 days.

## `sec-reporting-export-key`

- **Owner:** analytics-team
- **Reference:** `gcp-secret-manager://staging/reporting/export-key`
- **Gap:** last rotated 265 days ago (policy: 90 days).
