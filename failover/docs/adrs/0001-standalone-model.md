# ADR 0001 — An independent model for Failover

- Status: Accepted
- Date: 2026-11-21

## Context

Atlas already models components, dependencies, flows and risks. Failover needs overlapping but different facts: which instance is the standby, in which direction the switchover goes, how long detection and promotion take, and whether a drill has evidence.

Options considered:

1. Reuse the Atlas YAML model and extend it.
2. Have Failover consume a JSON report exported by Atlas.
3. Give Failover its own four YAML files.

## Decision

Option 3. Failover owns `topology.yaml`, `services.yaml`, `strategies.yaml` and `drills.yaml`. It does not import `fortcloud_atlas` and does not require Atlas to be installed.

## Consequences

- Each tool can be adopted, installed and versioned alone.
- There is some deliberate duplication of loader code (~50 lines).
- Users who adopt both tools maintain two models. This is accepted: the tools answer different questions and the fields are not interchangeable.
- If a third tool needs the same loader, extracting a shared `fortcloud_common` package can be revisited.

## Alternatives rejected

- **Extending the Atlas model** would force Atlas users to carry failover fields they do not use and would couple the two release cycles.
- **Consuming an Atlas JSON export** adds a build-order dependency and a brittle contract between two CLIs.
