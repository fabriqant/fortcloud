# FortCloud Vitals — Signal Catalog

> Generated on 2026-11-21 by `fortcloud-vitals signals`. Do not edit by hand.

Every signal should back at least one objective. Orphan signals cost money
and produce alerts nobody owns.

| Signal | Kind | Source | Interval | Unit | Objectives | Last check | Status |
|---|---|---|---|---|---|---|---|
| `sig-auth-availability` — Identity service availability | Availability | Datadog | 15s | percent | 1 | 2026-11-18 | OK |
| `sig-auth-completeness` — Identity record completeness | Completeness | SQL query | 5m | percent | 1 | 2026-07-15 | OK |
| `sig-catalog-availability` — Catalog availability | Availability | CloudWatch | 15m | percent | 1 | 2026-11-18 | OK |
| `sig-checkout-availability` — Order API availability | Availability | Prometheus | 30s | percent | 1 | 2026-11-18 | OK |
| `sig-checkout-freshness` — Order database freshness | Freshness | SQL query | 1m | duration | 1 | 2026-10-10 | OK |
| `sig-checkout-latency` — Order API p99 latency | Latency | Prometheus | 15s | ms | 1 | 2026-11-18 | OK |
| `sig-reporting-validity` — Analytics export validity | Validity | SQL query | 1h | percent | 1 | 2026-11-18 | OK |

## `sig-catalog-availability`

- **Owner:** catalog-team
- **Objectives:** `slo-catalog-avail`
- **Note:** Sampled too coarsely for the declared error budget.
