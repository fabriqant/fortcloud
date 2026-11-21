# Exercise record — template

Copy this file for every drill. Link it from the check evidence in `verification.yaml`.

## Exercise

- **Scenario:** `ex-...`
- **Kind:** restore / failover / recovery
- **Environment:** sandbox / staging / prod
- **System:** ...
- **Scheduled:** YYYY-MM-DD
- **Controlled rehearsal:** `ex-...-sandbox` (date, result)
- **Owner:** team
- **Go / no-go:** name + decision

## Who did what

- [ ] Coordinator: ...
- [ ] Operator: ...
- [ ] Communicator: ...
- [ ] Verifier: ...

## Communication

- [ ] Start announced at ... on `channel`
- [ ] Updates every 15m: link or channel excerpt
- [ ] End announced at ... with outcome
- [ ] Escalation path used if needed: ...

## Timings

| Milestone | Time | Note |
|---|---|---|
| Drill start | HH:MM | |
| Fault applied / restore started | HH:MM | |
| Service recovered | HH:MM | measured RTO |
| Data current up to | HH:MM | measured RPO |
| Drill end | HH:MM | |
| Declared RTO / RPO | 30m / 5m | from `scenarios.yaml` |

## Verification

| Kind | Metric | Expected | Observed | Result | Evidence |
|---|---|---|---|---|---|
| service | | | | passed / failed | link |
| data | | | | passed / failed | link |

## Outcome

- [ ] Service returned to a correct state
- [ ] Data returned to a correct state
- [ ] Verifier sign-off recorded after the exercise
- [ ] Findings opened with owner and due date

```bash
fortcloud-crucible check --strict --out ./artifacts
```

- [ ] Exit code 0
- [ ] `scenario-plan.md`, `roles-matrix.md`, `communication-plan.md`, `verification-report.md` attached
