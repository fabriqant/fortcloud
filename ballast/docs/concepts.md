# Concepts

## The timeout budget

A service promises a maximum end-to-end latency. Every outbound call in the chain consumes part of that budget. Ballast computes the **worst case** of a step as:

```text
worst case = timeout × (retries + 1) + Σ backoff × multiplierⁱ
```

The sum over all steps of a flow must stay below the service's `latency_budget`. This is the classic timeout-cascade problem: five steps allowed 800 ms each can still take 4 seconds.

## Dominant step

A single step consuming more than 70% of the budget is flagged even when the chain fits. It leaves no room for variance and makes the whole service dependent on one dependency's tail latency.

## Retry amplification

Retries multiply load at exactly the moment a dependency is unhealthy. Four retries mean five calls. If that dependency also retries internally, amplification compounds. Ballast caps retries at three, requires exponential backoff (`multiplier >= 2`) and jitter, and forbids retries on non-idempotent writes.

## Circuit breaker

A breaker stops sending traffic to a failing dependency so it can recover and so callers fail fast. Ballast requires one for every P0 dependency, warns when it opens only after more than 10 failures, and warns when the reset timeout is longer than 30 seconds.

## Bulkhead

A bulkhead isolates each dependency in its own pool of workers or connections. Without it, one slow dependency can exhaust every thread and take down calls that never touched it. Ballast warns when `bulkhead` is empty.

## Fallback

An optional dependency should degrade gracefully. `cached`, `default`, `degraded` and `queue` are valid answers; `none` is a warning for anything below P0. A P0 dependency may legitimately have no fallback if failing the request is safer than serving wrong data.

## Standalone by design

Ballast does not read the models of Atlas, Failover or Ark and does not import their code. Each tool answers a different question and can be adopted alone.
