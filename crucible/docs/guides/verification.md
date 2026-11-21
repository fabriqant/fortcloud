# Verification guide

## Two checks, one signature

Marking a scenario `passed` is a claim. Crucible accepts the claim only if the model holds:

1. a **service** check with `result: passed`;
2. a **data** check with `result: passed`;
3. an approved sign-off from the verifier;
4. a link to evidence for each check.

```yaml
checks:
  - id: chk-restore-service
    scenario: ex-restore-sandbox
    kind: service
    metric: http_5xx_rate
    expected: "0"
    result: passed
    evidence: https://ci.example.com/crucible/restore-service-25
    owner: dave
  - id: chk-restore-data
    scenario: ex-restore-sandbox
    kind: data
    metric: order_count_after_restore
    expected: equal
    result: passed
    evidence: https://ci.example.com/crucible/restore-data-25
    owner: erin
signoffs:
  - scenario: ex-restore-sandbox
    person: dave
    role: verifier
    date: "2026-11-26"
    decision: approved
```

## What to check

| Kind | Example metrics |
|---|---|
| `service` | HTTP 5xx rate, success rate, p99 latency, queue depth, freshness of the dashboard |
| `data` | row count comparison, checksum, export diff, last-write timestamp, referential integrity |

`expected` is a short human-readable statement (`0`, `equal`, `match`, `5m`). The actual measurement lives in the evidence link. Don't put a number in `expected` and a different one in the evidence — reviewers compare them.

## Sign-off discipline

The sign-off must name the verifier assigned to the scenario, use `role: verifier`, be `approved`, and carry a date **on or after** `scheduled`. A signature from the day before is a warning because it cannot describe an exercise that had not happened yet.

## Failed drills stay failed

A check with `result: failed` is an error. A scenario with `status: failed` is a warning until a retest is recorded. Do not flip the status to `passed` to make CI green: add a new scenario with a new date, link the finding, and verify again.

## Verdicts in the report

`verification-report.md` ends with one line per exercise:

- **VERIFIED** — `status: passed`, both check kinds passed, no gaps;
- **PENDING** — anything else.

The same verdict is reflected in `crucible-status.json` under `scenarios[].verification_status`.

## Fixing findings

| Message | Fix |
|---|---|
| `no passed 'service' verification` | add a service check and attach its evidence |
| `no passed 'data' verification` | add a data check and attach its evidence |
| `no approved verifier sign-off` | record an approved sign-off from the assigned verifier |
| `no evidence link` | point the check at the saved measurement |
| `signed 1 day(s) before the scheduled exercise` | sign after the drill |
| `verification failed on 'http_5xx_rate'` | fix the cause, retest, then update the result |
