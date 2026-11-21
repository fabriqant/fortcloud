# Resilience policy review — <policy id>

| Field | Value |
|---|---|
| Policy | `<policy id>` |
| Dependency | `<dependency id>` |
| Type | database / cache / http_api / grpc / queue / search |
| Criticality | P0 / P1 / P2 |
| Operation | read / write |
| Idempotent | yes / no |
| Owner | `<team>` |

## Budget

| Measure | Value |
|---|---|
| Service latency budget | `<from services.yaml>` |
| Timeout | `<timeout>` |
| Retries | `<number>` |
| Backoff | `<backoff> × <multiplier>` |
| Jitter | yes / no |
| Worst case | `<computed by fortcloud-ballast budget>` |
| Share of budget | `<percentage>` |

## Guardrails

- [ ] Circuit breaker enabled (required for P0)
- [ ] Failure threshold ≤ 10
- [ ] Reset timeout ≤ 30s
- [ ] Dedicated bulkhead
- [ ] Fallback declared for optional dependencies
- [ ] No retries on non-idempotent writes
- [ ] Worst case below the service latency budget
- [ ] No single step above 70% of the budget

## Notes

<why these values were chosen, measured p99 latency, incidents that motivated the change>

## Decision

- [ ] Accepted
- [ ] Changes requested

Reviewer: `<name>` — Date: `YYYY-MM-DD`
