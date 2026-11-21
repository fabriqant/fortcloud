# ADR 0001 — Rehearse before production

- **Status:** Accepted
- **Date:** 2026-11-21
- **Scope:** Fortcloud Crucible v0.1.0

## Context

Recovery plans are usually written in a document, approved, and then discovered to be wrong during a real incident. The two most common failures are: the first attempt happens in production, and the result is recorded as "successful" without anyone checking the data or signing off. A drill can also cause an incident of its own if the organisation mistakes it for a real outage.

## Decision

Crucible encodes four rules in its model:

1. **Controlled first.** An exercise environment must be isolated, non-production and approved. A production drill of a given `kind` requires a passed rehearsal of that kind in a controlled environment.
2. **Named roles.** Every drill assigns a coordinator, operator, communicator and verifier from a participant roster.
3. **Planned communication.** Declared channels and stakeholders, notified at start, update and end, with a maximum 15-minute update cadence.
4. **Verified result.** A passed drill needs a passed service check, a passed data check, evidence links and an approved verifier sign-off dated after the exercise.

The model is a statement of intent validated in CI, not a live connector to a chaos engine.

## Alternatives considered

1. **Trust the runbook.** No validation, and the first real incident becomes the test.
2. **Run every drill in production.** Maximally realistic, but a failed restore or failover is an outage; unacceptable as a first attempt.
3. **Only track the RTO number.** A number without a role roster, communication plan and data verification is not evidence that recovery worked.

## Consequences

- Every production drill has a documented, passed predecessor — the rehearsal evidence is in the same repository.
- Incident responders know their roles before the drill; the communication plan doubles as the incident template.
- `check --strict` can gate a release on a credible drill programme.
- v0.1.0 does not measure RTO/RPO automatically; measured timings belong in the evidence links and the exercise record. Automatic measurement from drill timestamps is a roadmap item.
