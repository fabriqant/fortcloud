# Change control guide

## Design the pipeline as a control

A pipeline is not just a list of jobs. It declares who can deploy, what must pass and how to come back:

```yaml
- id: pipe-checkout-prod
  environment: prod
  trigger: tag
  deployer: ci-deploy
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

## Review

For a restricted environment, review is mandatory and at least 2 approvers are expected. One approver is a warning; no review is an error. Put the approvers in `review.approvers` so the number is reviewable in the model rather than implicit in a platform setting.

## Tests

Unit and integration tests are mandatory on a restricted environment. A security test is expected everywhere — missing it is a warning. Add `contract`, `e2e` or `load` stages when the change warrants them.

## Deployer identity

`deployer` references a principal from `access.yaml`. Custodian errors if that principal does not exist or is not scoped to the target environment. This ties deployment automation to the least-privilege model: the runner cannot deploy to production unless a grant and an environment scope say so.

## Rollback

Rollback is not a paragraph in a runbook. It must be:

- `enabled: true` — otherwise an error on a restricted environment;
- `target` — what to return to;
- `verified` — the date of the last successful rollback drill;
- `automate: true` — manual rollback on a restricted environment is a warning.

A verification older than 90 days is a warning. Rehearse rollback on the same cadence as restore drills in Ark.

## Audit the change

Every deployment needs a `deploy` operation in `audit.yaml`, plus `pipeline_change` whenever the pipeline itself changes. Point both at an immutable sink and keep fresh evidence. This is what turns "we have a pipeline" into "we can prove the change was reviewed, tested and reversible".

## Fixing findings

| Message | Fix |
|---|---|
| `review is not required for a restricted environment` | set `review.required: true` |
| `1 approver(s)` | add a second approver |
| `missing mandatory test(s): integration` | add the stage and make it blocking |
| `deployer 'ci-old' is not scoped to 'prod'` | use the dedicated production identity |
| `rollback is not enabled` | define a rollback target and enable it |
| `rollback verification is 324 days old` | rehearse rollback and update `verified` |
| `rollback is not automated` | automate the rollback job |
