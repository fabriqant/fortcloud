# Fortcloud Atlas — Service levels and error budgets

## Criticality classes

| Class | Definition | Typical availability target | RTO target | RPO target |
|---|---|---|---|---|
| **P0** | Critical flow: financial loss, regulated data or immediate business stop | 99.95% – 99.99% | 15–30 min | 0 – 5 min |
| **P1** | Important flow: degradation tolerated, activity continues in degraded mode | 99.5% | 1–4 h | 1 h |
| **P2** | Support: internal tooling, deployment, non-vital reporting | 99% | 8 h | 24 h |

These are starting points. The value retained per flow lives in `flows.yaml` and must be validated by the business owner.

## Error budget

```
error budget (minutes/month) = (1 - availability_target) × 60 × 24 × 30
```

Examples: 99.95% → 21.6 min/month; 99.9% → 43.2 min/month; 99.5% → 216 min/month.

Governance rules:

1. While the error budget is positive, the team deploys normally.
2. At 50% consumed, freeze non-essential changes on that flow and review incidents.
3. At 100% consumed, freeze deployments until the budget recovers or the owner explicitly waives it.
4. Outages of external services count against the budget — that is why a contractual SLA and a fallback are necessary.

## Measurement

- **SLI**: proportion of successful requests, time to first byte, data freshness, processing success rate.
- **Stack**: Prometheus/Thanos for metrics, Loki for logs, Tempo/Jaeger for traces, Grafana for dashboards, Sloth or Pyrra for SLO generation.
- **Multi-cloud observability**: aggregate metrics in one control plane, otherwise the error budget is computed from a partial view.

## Link with RTO and RPO

The error budget measures **normal operation**. RTO/RPO measure **recovery after a disaster**. Both must be consistent: a 99.99% flow with an 8-hour RTO is contradictory. A 30-minute outage already consumes the entire monthly budget of a 99.95% flow — that is expected and must be documented in the post-mortem.

## Hybrid / multi-cloud requirements

- Do not add availability figures of independent components without accounting for shared dependencies (DNS, IdP, network hub).
- Require evidence for every objective: the date of the last restore test in `flows.yaml`.
- Revise targets after each game day: an unreachable RTO is a fictional target.
