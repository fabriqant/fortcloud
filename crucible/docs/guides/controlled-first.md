# Controlled-first guide

## Plan the kinds, not just the dates

For each system, you need at least one rehearsal of every kind you might use in anger:

| Kind | Question | Typical controlled action |
|---|---|---|
| `restore` | Can we bring the data back from a backup? | Restore a snapshot into the sandbox and compare row counts |
| `failover` | Can we switch traffic to the standby? | Flip a masked-data staging service and measure the switch |
| `recovery` | Can we bring the whole service back after a major incident? | Run the full runbook in an isolated environment |

A production drill of a kind without a passed rehearsal is an **error** in Crucible. The model comparison uses `kind`, so `ex-restore-sandbox` covers `ex-restore-prod`.

## Make the environment genuinely controlled

```yaml
- id: sandbox
  isolation: full
  data: synthetic
  owner: platform-team
  approved: true
  approved_by: change-board
```

`partial` isolation with `masked` data is acceptable if the environment is approved. `shared` isolation or `production` data is not controlled — even if `approved: true`. This is deliberate: rehearsing against production data is a change in risk, not a rehearsal.

## Keep the window short

`duration` is the planned exercise window. Crucible warns above 4 hours. Split a long `recovery` drill into stages rather than holding a war room open all day.

## Record the target, then measure

`target_rto` and `target_rpo` are declared in the model and printed in the scenario plan. Crucible checks their syntax and renders them in milliseconds in `crucible-status.json`. The measured values belong in the verification evidence and the exercise record — see the [verification guide](verification.md).

## Respect the blast radius

`contained` means the drill cannot reach other systems, `limited` means a small, known surface, `broad` means real customer impact. Production exercises with `broad` blast radius should require an explicit incident commander and a go/no-go decision recorded in the exercise record template.

## Fixing findings

| Message | Fix |
|---|---|
| `no passed 'failover' exercise in a controlled environment` | add a failover drill in `sandbox` or `staging` and mark it passed once verified |
| `environment is not approved for exercises` | record the approval and set `approved: true` |
| `scheduled 37 days ago and still 'planned'` | run it, or update `scheduled` to the new date |
| `exercise window 6h exceeds 4h` | split the drill |
| `exercise failed — schedule a retest` | open the finding, fix it, add a new scenario with a new date |
