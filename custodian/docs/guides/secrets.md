# Secrets guide

## Store references, never values

```yaml
- id: sec-checkout-db
  store: vault
  reference: vault://prod/checkout/db
```

The schema has `additionalProperties: false`, so adding `value: hunter2` produces a validation error before anything else runs. This file is safe to commit and review.

Supported stores: `vault`, `aws-secrets-manager`, `azure-key-vault`, `gcp-secret-manager`, `k8s-secret`. A Kubernetes Secret in a restricted environment is a warning — use a managed store with encryption and audit.

## One secret per environment

A secret listing several environments is a warning; if one of them is `restricted`, it is an error. Never copy a production credential into staging. Create a distinct secret with a distinct reference for each environment.

## Rotation policy

Set `rotation_days` to at most 90 and keep `last_rotated` current:

```yaml
last_rotated: "2026-10-01"
rotation_days: 90
```

Custodian computes the age against today. Overdue on a restricted environment is an error; elsewhere a warning. A policy above 90 days is always a warning, even if the secret was rotated yesterday.

## Declare every consumer

`used_by` lists principal ids from `access.yaml`. Custodian errors when a consumer does not exist or has no environment in common with the secret. This prevents a service account in staging from quietly depending on a production credential.

## Record the audit link

A `secret_access` operation in `audit.yaml` should cover the restricted environment and point to an immutable sink. The secret inventory and the audit trail are reviewed together — a rotated secret with no access log is not a controlled secret.

## Fixing findings

| Message | Fix |
|---|---|
| `Additional properties are not allowed ('value')` | remove the value; keep only `reference` |
| `secret shared across 2 environments` | split into one secret per environment |
| `last rotated 265 days ago` | rotate, update `last_rotated`, record evidence |
| `rotation policy of 180 days exceeds 90 days` | set `rotation_days: 90` or less |
| `consumer 'ci-old' not found` | remove the stale consumer or declare the principal |
| `Kubernetes Secret in a restricted environment` | migrate to a managed secret store |
