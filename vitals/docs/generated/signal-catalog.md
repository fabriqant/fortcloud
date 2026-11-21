# Fortcloud Vitals — Signal Catalog

> Generated on 2026-11-21 by `fortcloud-vitals signals`. Do not edit by hand.

Every signal should back at least one objective. Orphan signals cost money
and produce alerts nobody owns.

| Signal | Kind | Source | Interval | Unit | Objectives | Last check | Status |
|---|---|---|---|---|---|---|---|
| `sig-auth-availability` — Disponibilité du service d'identité | Disponibilité | Datadog | 15s | percent | 1 | 2026-11-18 | OK |
| `sig-auth-completeness` — Complétude des enregistrements d'identité | Complétude | Requête SQL | 5m | percent | 1 | 2026-07-15 | OK |
| `sig-catalog-availability` — Disponibilité du catalogue | Disponibilité | CloudWatch | 15m | percent | 1 | 2026-11-18 | OK |
| `sig-checkout-availability` — Disponibilité de l'API commande | Disponibilité | Prometheus | 30s | percent | 1 | 2026-11-18 | OK |
| `sig-checkout-freshness` — Fraîcheur de la base commande | Fraîcheur | Requête SQL | 1m | duration | 1 | 2026-10-10 | OK |
| `sig-checkout-latency` — Latence p99 de l'API commande | Latence | Prometheus | 15s | ms | 1 | 2026-11-18 | OK |
| `sig-reporting-validity` — Validité des exports analytiques | Validité | Requête SQL | 1h | percent | 1 | 2026-11-18 | OK |

## `sig-catalog-availability`

- **Owner:** catalog-team
- **Objectives:** `slo-catalog-avail`
- **Note:** Sampled too coarsely for the declared error budget.
