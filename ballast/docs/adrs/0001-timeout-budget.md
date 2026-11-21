# ADR 0001 — The timeout budget as a first-class check

- Status: Accepted
- Date: 2026-11-21

## Context

Resilience settings are usually reviewed one file at a time. A 500 ms timeout here, three retries there, a breaker with a default threshold — each looks reasonable in isolation. The failure mode only appears when they are composed along a request path: the worst-case chain exceeds the latency the service promised.

Options considered:

1. Leave timeouts to runtime frameworks and review them in code only.
2. Derive the budget from the sum of configured timeouts.
3. Declare the service latency budget independently and check every chain against it.

## Decision

Option 3. `services.yaml` owns the budget; `flows.yaml` declares the chain; Ballast computes the worst case — `Σ timeout × attempts + backoff` — and fails when it exceeds the budget. A single step above 70% of the budget is a warning even when the total fits.

## Consequences

- Teams must declare a latency budget per service, which forces an SLO conversation.
- Adding a retry or increasing a timeout can fail CI, which is intentional: both consume budget.
- The worst case is a deterministic upper bound, not a statistical prediction; it does not replace load testing or tracing.
- `format_duration()` produces values that can be pasted back into the model, keeping the loop short.

## Alternatives rejected

- **Runtime-only review** makes composition invisible and pushes the discovery to production.
- **Deriving the budget from configured timeouts** would validate the model against itself and could never detect over-generous timeouts.
