# ADR 0001 — YAML as the source of truth

- **Status**: Accepted
- **Date**: 2026-11-20
- **Deciders**: Fortcloud contributors

## Context

Infrastructure diagrams drift as soon as they are drawn by hand. Engineers need a model they can review in a pull request, validate in CI and regenerate views from.

## Decision

The model lives in four YAML files (`components.yaml`, `dependencies.yaml`, `flows.yaml`, `risks.yaml`) under a user-provided directory. All diagrams and reports are generated from those files. No database, no API, no agent.

## Consequences

- Positive: small diff, easy review, works offline, no vendor lock-in.
- Positive: JSON Schemas give immediate feedback in editors and CI.
- Negative: the model can be stale if nobody updates it — mitigated by CI validation and by stale-restore-test warnings.
- Negative: very large estates need splitting into several model directories and an aggregation step.
