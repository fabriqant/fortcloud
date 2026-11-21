# ADR 0001 — Controls as a versioned model

- **Status:** Accepted
- **Date:** 2026-11-21
- **Scope:** Fortcloud Custodian v0.1.0

## Context

Access policy, secrets, deployment pipelines and audit configuration usually live in four different systems: an IAM console, a secret manager, a CI platform and a log platform. No single pull request can show whether a change to one of them breaks the controls of another. The result is predictable: a CI runner with production access in two environments, a secret rotated every 180 days, a deployment with no tested rollback, and an audit bucket nobody has checked.

## Decision

Custodian keeps a **declarative model** of these controls in four YAML files, validated by JSON Schemas and semantic rules:

- access: environments, principals and grants;
- secrets: references, rotation and consumers;
- changes: review, tests and rollback;
- audit: sinks and sensitive operations.

Cross-file references are checked: a deployer must exist as a principal and be scoped to the target environment; a secret consumer must exist and share an environment; every logged operation must name a declared sink. The model is intentionally a **statement of intent**, not a live connector.

## Alternatives considered

1. **Query the live APIs.** More accurate at a point in time, but needs credentials, network access and per-provider plugins — incompatible with "no backend, no agent".
2. **Keep controls in a wiki.** Easy to write, impossible to validate, and guaranteed to drift.
3. **One file for everything.** Simpler to load, but hides the separation of duties between the teams that own access, secrets, delivery and audit.

## Consequences

- Every control change is a reviewed commit, with the generated reports as evidence.
- The model can be stricter than the live platform; the diff is exactly the remediation work.
- No live telemetry is collected in v0.1.0 — import of real IAM policies and audit logs is a roadmap item.
- `check --strict` can gate a release on least privilege, environment isolation, protected secrets, controlled changes and a trustworthy audit trail.
