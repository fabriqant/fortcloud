# Concepts

Crucible models a drill programme with four connected files. A scenario is only credible when its environment, its crew, its communication and its verification all check out.

## 1. Controlled environment first

An environment counts as **controlled** only when all three conditions hold:

- `isolation` is `full` or `partial` (not `shared`);
- `data` is `synthetic` or `masked` (not `production`);
- `approved` is `true`.

Before a `restore`, `failover` or `recovery` drill may run in production, a **passed exercise of the same kind** must exist in a controlled environment. Crucible compares the `kind`, not the scenario id, so a rehearsal in the sandbox counts for the production scenario of the same type.

The point is not bureaucracy: a failed rehearsal in a sandbox costs nothing, while the first attempt in production is an incident.

## 2. Scenario and roles

A scenario declares:

- `kind` — `restore`, `failover` or `recovery`;
- `environment`, `system`, `scheduled`, `status`;
- `target_rto`, `target_rpo`, `duration`;
- `blast_radius` — `contained`, `limited` or `broad`;
- `channel` and `owner`;
- `assignments` — person + role.

Four roles are mandatory: **coordinator** (runs the clock and the script), **operator** (performs the action), **communicator** (sends the messages), **verifier** (declares the service and data state). All must exist in the participant roster. The verifier cannot be implicit — a green result with no named verifier is not accepted.

## 3. Communication

An exercise without communication looks like a real incident. The plan declares channels (`slack`, `bridge`, `email`, `pager`), their audience and owner, and stakeholders with a `notify` list drawn from `start`, `update`, `end`.

At least one stakeholder must be notified at each of the three moments. Status updates go out at most every 15 minutes. External channels need an `approval`. The `plan` also names the escalation path and the go/no-go authority.

## 4. Verification

A drill is marked `passed` only when the model contains:

- a **service** check with `result: passed` — for example a 5xx rate, a success rate or data freshness;
- a **data** check with `result: passed` — for example a row count, a checksum or an export comparison;
- an **evidence** link on each check;
- an approved sign-off from the verifier, dated on or after the scheduled exercise.

Crucible also refuses to mark a `failed` drill green: a failed exercise stays flagged until the finding is fixed and a retest is recorded.

## How they connect

```text
environment (controlled) ──> scenario ──> four roles ──> communicator ──> stakeholders
                                  │
                                  └──> service + data checks ──> verifier sign-off
```

The scenario plan shows the schedule, the roles matrix shows the crew, the communication plan shows the script, and the verification report shows the result. Together they are the evidence an auditor or an incident reviewer wants.
