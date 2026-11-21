# Fortcloud Vitals — Quality Plan

> Generated on 2026-11-21 by `fortcloud-vitals plan`. Do not edit by hand.

Ordered by service criticality. Fix the model, not this file.

## objective:slo-auth-completeness

- **Owner:** sec-team
- **Service:** `identity-auth` (P0)
- **Signal:** `sig-auth-completeness` (SQL query)

1. Fix: Alert fires after 80% of the error budget is spent (max 50%).
2. Fix: Last check is 129 days old (max 90).
3. Fix: Result is 'partial'.
4. Re-run `fortcloud-vitals check --strict`.

## objective:slo-catalog-avail

- **Owner:** catalog-team
- **Service:** `catalog-browse` (P1)
- **Signal:** `sig-catalog-availability` (CloudWatch)

1. Fix: Signal interval 15m is too coarse (max 4m19s).
2. Fix: No runbook.
3. Re-run `fortcloud-vitals check --strict`.

## objective:slo-reporting-validity

- **Owner:** analytics-team
- **Service:** `reporting` (P2)
- **Signal:** `sig-reporting-validity` (SQL query)

1. Fix: Signal interval 1h is too coarse (max 20m10s).
2. Fix: Result is 'failed'.
3. Re-run `fortcloud-vitals check --strict`.

## Definition of done

- Every P0 service has an availability objective and a data-quality objective.
- Every signal backs at least one objective.
- Each alert fires before the target is breached and before 50% of the error budget is spent.
- Latency and freshness alerts leave at least 20% margin below the target.
- Signal intervals are frequent enough to observe the budget.
- Every objective has a recent check with `result: passed`, evidence and a runbook.
- `fortcloud-vitals check --strict` exits with code 0.
