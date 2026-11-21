# ADR 0001 — The error budget is a first-class check

- **Status:** Accepted
- **Date:** 2026-11-21
- **Scope:** Fortcloud Vitals v0.1.0

## Context

Teams frequently publish an SLO target and an alert threshold without ever computing how much failure the target allows. The two numbers are chosen independently, so alerts often fire long after the budget is exhausted. Sampling intervals are picked for cost reasons without checking whether they can observe the budget at all. The result is a dashboard that looks healthy until the incident is already over.

## Decision

Vitals computes the error budget from the target and window for every percentile objective, then validates the alert threshold against it:

```text
budget      = window × (100 − target) / 100
spent_at_alert = window × (100 − alert_threshold) / 100 / budget
```

An alert spending more than 50% of the budget is a warning. For duration targets, the margin between alert and target must be at least 20%. The sampling interval must be at most a tenth of the budget (or half of a freshness target). These are model checks, not advisory text.

The budget, headroom and interval appear in the generated dashboard and in `vitals-status.json` so a reviewer can see the same numbers in a pull request and in CI.

## Alternatives considered

1. **Document the budget in a wiki page.** It drifts away from the target as soon as someone edits the dashboard.
2. **Only check that the alert is tighter than the target.** Valid but far too permissive: 99.91% against 99.9% is "tighter" while leaving only 10% of the budget.
3. **Require burn-rate windows immediately.** Powerful, but needs live telemetry; Vitals v0.1.0 stays a static model tool and leaves burn-rate alerting to a future version.

## Consequences

- Alert thresholds must be chosen deliberately, with the budget visible in review.
- Tight targets may become "invalid" until sampling or alerting is improved — this is the intended pressure.
- Duration objectives use a margin rule because they do not express a failure allowance in the same way.
- A clean model produces a credible, reproducible SLO record; a dirty model fails `check --strict` in CI.
