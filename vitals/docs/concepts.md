# Concepts

## SLI, SLO and error budget

A **SLI** is a signal: a measurable view of service behaviour (`availability`, `latency`, `freshness`, `completeness`, `validity`). An **SLO** is the objective attached to that signal: a target, an alert threshold and a window. The **error budget** is what the target permits to fail over that window:

```text
budget = window × (100 − target) / 100
```

For a 99.9% availability objective over 30 days the budget is **43m12s**. For a 99.99% objective it is **4m19s**. A tighter target shrinks the budget dramatically, which is exactly why "four nines" needs a much faster alert.

## Alert headroom

The alert threshold must be **tighter than the target**:

- percent kinds (`availability`, `completeness`, `validity`): the alert value is **higher** than the target;
- duration kinds (`latency`, `freshness`): the alert value is **lower** than the target.

For percentile targets Vitals expresses how much of the budget is already spent when the alert fires. A threshold of 99.95% against 99.9% means 50% of the budget is spent — the alert fires with half the budget left. A threshold of 99.91% means 90% is gone. Vitals flags anything above 50%.

For duration targets there is no failure budget in the same sense, so Vitals checks the **margin** between alert and target and requires at least 20% of the target as reaction time.

## Sampling

An alert can only observe what the signal samples. Vitals requires the sampling interval to be at most a tenth of the error budget (and at most half of a freshness target). A 4m19s budget needs a signal at least every ~26s; a 15m interval cannot see the breach before the budget is gone.

## Health and data quality

Availability is not enough. A service can answer `200 OK` while its data is stale, incomplete or invalid. Every P0 service therefore needs:

1. an availability objective, and
2. at least one data-quality objective (`freshness`, `completeness` or `validity`).

This is a model rule, not a dashboard suggestion: Vitals fails validation when it is missing.

## Evidence over claims

An SLO that nobody verifies is a number in a document. Every objective should have a check with a date, a result, an evidence link and a runbook. On a P0 service a failed check or a missing runbook is an error; on lower-criticality services it is a warning. Checks older than 90 days are stale.

## Kinds and units

| Kind | Target / alert type | Typical unit |
|---|---|---|
| `availability` | percent | `percent` |
| `completeness` | percent | `percent` |
| `validity` | percent | `percent` |
| `latency` | duration | `ms` or `duration` |
| `freshness` | duration | `duration` |

A signal's `kind` must match every objective that uses it.
