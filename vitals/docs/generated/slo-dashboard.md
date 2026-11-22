# FortCloud Vitals — SLO Dashboard

> Generated on 2026-11-21 by `fortcloud-vitals dashboard`. Do not edit by hand.

**Error budget** is the amount of failure a percentile target allows over its
window (for example 99.9% over 30 days = 43m12s). The alert must fire before
that budget is spent.

## Objectives

| Objective | Service | Crit. | Signal | Kind | Target | Window | Budget | Alert at | Headroom | Interval | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slo-auth-avail` | `identity-auth` | P0 | `sig-auth-availability` | Availability | 99.99% | 30d | 4m19s | 99.995% | 50% used at alert | 15s | OK |
| `slo-auth-completeness` | `identity-auth` | P0 | `sig-auth-completeness` | Completeness | 99.5% | 30d | 3h36m | 99.6% | 80% used at alert | 5m | AT RISK |
| `slo-catalog-avail` | `catalog-browse` | P1 | `sig-catalog-availability` | Availability | 99.9% | 30d | 43m12s | 99.95% | 50% used at alert | 15m | AT RISK |
| `slo-checkout-avail` | `checkout` | P0 | `sig-checkout-availability` | Availability | 99.9% | 30d | 43m12s | 99.95% | 50% used at alert | 30s | OK |
| `slo-checkout-freshness` | `checkout` | P0 | `sig-checkout-freshness` | Freshness | 5m | 30d | margin 1m | 4m | 20% margin | 1m | OK |
| `slo-checkout-latency` | `checkout` | P0 | `sig-checkout-latency` | Latency | 300ms | 30d | margin 60ms | 240ms | 20% margin | 15s | OK |
| `slo-reporting-validity` | `reporting` | P2 | `sig-reporting-validity` | Validity | 99% | 14d | 3h21m36s | 99.5% | 50% used at alert | 1h | AT RISK |

## `slo-auth-avail` — Authentication

- **Owner:** sec-team
- **Kind:** Availability
- **Target / alert:** 99.99% / 99.995%
- **Window:** 30d
- **Error budget:** 4m19s — 50% used at alert
- **Signal:** `sig-auth-availability` every 15s (Datadog)
- **Last check:** 2026-11-18 — passed
- **Status:** OK


## `slo-auth-completeness` — Authentication

- **Owner:** sec-team
- **Kind:** Completeness
- **Target / alert:** 99.5% / 99.6%
- **Window:** 30d
- **Error budget:** 3h36m — 80% used at alert
- **Signal:** `sig-auth-completeness` every 5m (SQL query)
- **Last check:** 2026-07-15 — partial
- **Status:** AT RISK
- **Gap:** alert fires after 80% of the error budget is spent (max 50%).


## `slo-catalog-avail` — Catalog browsing

- **Owner:** catalog-team
- **Kind:** Availability
- **Target / alert:** 99.9% / 99.95%
- **Window:** 30d
- **Error budget:** 43m12s — 50% used at alert
- **Signal:** `sig-catalog-availability` every 15m (CloudWatch)
- **Last check:** 2026-11-18 — passed
- **Status:** AT RISK
- **Gap:** signal interval 15m is too coarse (max 4m19s).


## `slo-checkout-avail` — Order API

- **Owner:** commerce-team
- **Kind:** Availability
- **Target / alert:** 99.9% / 99.95%
- **Window:** 30d
- **Error budget:** 43m12s — 50% used at alert
- **Signal:** `sig-checkout-availability` every 30s (Prometheus)
- **Last check:** 2026-11-18 — passed
- **Status:** OK


## `slo-checkout-freshness` — Order API

- **Owner:** data-platform
- **Kind:** Freshness
- **Target / alert:** 5m / 4m
- **Window:** 30d
- **Error budget:** margin 1m — 20% margin
- **Signal:** `sig-checkout-freshness` every 1m (SQL query)
- **Last check:** 2026-10-10 — passed
- **Status:** OK


## `slo-checkout-latency` — Order API

- **Owner:** commerce-team
- **Kind:** Latency
- **Target / alert:** 300ms / 240ms
- **Window:** 30d
- **Error budget:** margin 60ms — 20% margin
- **Signal:** `sig-checkout-latency` every 15s (Prometheus)
- **Last check:** 2026-11-18 — passed
- **Status:** OK


## `slo-reporting-validity` — Analytics reporting

- **Owner:** analytics-team
- **Kind:** Validity
- **Target / alert:** 99% / 99.5%
- **Window:** 14d
- **Error budget:** 3h21m36s — 50% used at alert
- **Signal:** `sig-reporting-validity` every 1h (SQL query)
- **Last check:** 2026-11-18 — failed
- **Status:** AT RISK
- **Gap:** signal interval 1h is too coarse (max 20m10s).

## Links

- [Signal catalog](signal-catalog.md)
- [Quality plan](quality-plan.md)
- [Machine-readable status](vitals-status.json)
