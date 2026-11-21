# Timeout budget guide

## Start from the SLO

Take the p99 latency the service promises. That is `latency_budget`. Do not derive it from the sum of the current timeouts — that would bless an existing problem.

## List the chain

Write one `steps` entry per outbound call, in the order they happen. A step needs both a `dependency` and the `policy` that guards it. Ballast rejects a policy attached to the wrong dependency.

## Size each timeout

Work backwards from the budget:

1. Reserve headroom for processing, serialisation and queueing (typically 20–30%).
2. Allocate the rest to steps, giving the most critical dependency the largest share.
3. Keep every step below 70% of the budget.
4. Remember that retries multiply the timeout: `timeout × (retries + 1)`.

Example: a 3s budget with three steps could use 150ms + 1 attempt for auth, 200ms + 2 for inventory and 500ms + 0 for payment — 1.5s worst case, 50% usage.

## Choose retry settings

| Situation | Setting |
|---|---|
| Read, idempotent, fast | 1–2 retries, jitter, multiplier 2 |
| Write, idempotent (upsert with key) | 0–1 retries, jitter |
| Write, non-idempotent | `retries: 0`, `fallback: queue` |
| Known slow dependency | shorten timeout, use `fallback: cached` |

Never retry a payment or an event that has no idempotency key.

## Protect the caller

- Set a `circuit_breaker` on every P0 dependency.
- Keep `failure_threshold` at 10 or below and `reset_timeout` at 30s or below.
- Give each dependency its own `bulkhead`.
- Give optional dependencies a `fallback`.

## Verify

```bash
fortcloud-ballast budget --out ./docs/generated
fortcloud-ballast check --strict --out ./artifacts
```

Compare the generated worst-case figures with measured p99 latencies from tracing. A budget that is never approached in production is usually a sign the timeouts are too loose to protect anything.
