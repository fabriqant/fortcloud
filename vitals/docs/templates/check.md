# SLO verification record — template

Copy this file for each objective and keep it next to your runbooks. The `checks.yaml` entry should point to the stored record.

```yaml
- id: chk-<objective-id>
  objective: <objective-id>
  last: "YYYY-MM-DD"
  result: passed          # passed | partial | failed
  evidence: https://ci.example.com/vitals/<objective-id>-<run>
  owner: <team>
  runbook: ../templates/check.md
  notes: What was measured and why the result is credible.
```

## What to record

1. **Window measured** — the same window declared in `objectives.yaml`.
2. **Observed SLI** — the measured value, including the query or dashboard link.
3. **Budget consumed** — actual failures versus the computed budget.
4. **Alert behaviour** — did the alert fire before the budget was spent?
5. **Data-quality result** — for P0 services, confirm freshness, completeness or validity.
6. **Actions** — what was fixed, who owns it and the due date if the result is not `passed`.

## Review checklist

- [ ] The check date is within 90 days.
- [ ] `result: passed`, or an incident is open for a P0 failure.
- [ ] `evidence` is reachable and reproducible.
- [ ] `runbook` describes the response, not just the symptom.
- [ ] `fortcloud-vitals check --strict` exits with code 0.
