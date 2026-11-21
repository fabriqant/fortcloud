# SLO design guide

## 1. Start from the user, not the metric

Write what a user can observe: "the checkout API answers successfully", "the order database is no more than five minutes behind". Then pick the signal that measures it. Avoid composite metrics that hide a failure behind an average.

## 2. Choose a target you can afford

Compute the budget before committing to the target:

| Target | 30-day budget |
|---|---|
| 99.9% | 43m12s |
| 99.95% | 21m36s |
| 99.99% | 4m19s |
| 99.995% | 2m10s |

A budget shorter than the time it takes to wake someone up is not operable. If the alert cannot fire and a human cannot act inside the budget, lower the target or automate the response.

## 3. Set the alert at half the budget

For percentile targets, the alert threshold should spend no more than 50% of the budget:

```text
alert_threshold = 100 − (100 − target) / 2
```

For 99.9%, that is 99.95%. For 99.99%, it is 99.995%. Vitals warns when the alert fires after more than half the budget is gone.

For duration targets, leave at least 20% of the target between the alert and the target: a 300ms target gets a 240ms alert; a 5m freshness target gets a 4m alert.

## 4. Sample fast enough

The interval must be at most a tenth of the budget. With 43m12s that is about 4m; with 4m19s it is about 26s. For freshness, use at most half the target. An interval that is too coarse is flagged as a warning because it silently destroys the alert's usefulness.

## 5. Use a window of at least seven days

A one-hour SLO is a health check, not an SLO. Vitals warns below `7d`. Use `30d` for service objectives and a shorter window only for explicitly rolling operational views.

## 6. Cover data quality on P0 services

Add a `freshness`, `completeness` or `validity` objective beside availability. A stale or corrupt answer is still a failed user experience.

## 7. Verify on a cadence

Store one `checks.yaml` entry per objective with:

- `last` — the ISO date of the verification;
- `result` — `passed`, `partial` or `failed`;
- `evidence` — a link to the CI run, dashboard export or test report;
- `runbook` — the response procedure.

Refresh at least every 90 days. A failed P0 check is a release blocker.

## 8. Gate in CI

```bash
fortcloud-vitals check --strict --out ./artifacts
```

Fix the model, never the generated artifacts. When the gate passes, the dashboard and status file are reviewable evidence of the controls you actually run.
