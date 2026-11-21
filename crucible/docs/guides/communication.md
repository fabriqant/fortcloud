# Communication guide

## Announce, update, close

A drill that is not announced produces the same pages as a real outage. The model requires three notification moments:

- **start** — say it is an exercise, name the system and the window;
- **update** — periodic status, at most every 15 minutes;
- **end** — declare the exercise closed and state the outcome.

```yaml
stakeholders:
  - id: support
    name: Customer support
    channel: war-room
    notify: [start, update, end]
```

At least one stakeholder must cover each moment. A stakeholder missing `update` is acceptable only if another one covers it — but the cadence check still applies to the plan as a whole.

## Declared channels only

Every scenario names a `channel` that must exist in `communication.yaml`. Every stakeholder names a declared channel too. This prevents "we'll use a temporary channel" from becoming the place where evidence disappears.

Channel types: `slack`, `bridge`, `email`, `pager`. Audience: `internal`, `external`, `both`. A channel with `external` or `both` audience needs an `approval` — an approved comms owner is the difference between a drill and a customer-facing incident.

## Name the plan owner and escalation path

```yaml
plan:
  updates_every: 15m
  escalation: sec-team
  go_no_go: change-board
  owner: communications
```

The communicator in the scenario's `assignments` is the person who executes this plan. The `plan.owner` is the team that maintains it. The escalation path and go/no-go authority should match the incident process used in production.

## Practical template

1. **T-1 day:** go/no-go confirmed, stakeholders aware of the window.
2. **T0:** "EXERCISE START — restoring checkout in sandbox, no customer impact."
3. **Every 15m:** current step, RTO clock, blockers.
4. **End:** "EXERCISE END — service verified, data verified, findings recorded", link to the exercise record.

## Fixing findings

| Message | Fix |
|---|---|
| `communication channel 'ghost' not found` | declare the channel or correct the scenario id |
| `channel 'ghost' not found` | fix the stakeholder's channel reference |
| `no stakeholder is notified at 'update'` | add `update` to a stakeholder's `notify` list |
| `status updates every 30m exceed 15m` | lower `plan.updates_every` |
| `external channel without communication approval` | set `approval` to the comms owner |
