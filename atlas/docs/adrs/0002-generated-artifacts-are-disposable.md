# ADR 0002 — Generated artifacts are disposable

- **Status**: Accepted
- **Date**: 2026-11-20
- **Deciders**: FortCloud contributors

## Context

The dependency graph and the resilience report are useful in pull requests and documentation sites. If contributors edit them directly, the next generation overwrites their changes and trust in the tool collapses.

## Decision

Generated Markdown files are written to `docs/generated/` by default and marked "do not edit by hand". They are rebuilt on every `check` run and published as a CI artifact.

## Consequences

- Positive: one source of truth, no merge conflicts on generated files.
- Positive: the report can be attached to a release or a change proposal by CI.
- Negative: readers must follow the link to the generated file rather than a hand-curated page; stable hand-written overview pages live under `docs/` instead.
