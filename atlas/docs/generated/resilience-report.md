# FortCloud Atlas — Resilience Report

> Generated on 2026-11-20 by `fortcloud-atlas report`. Do not edit by hand.

## Summary

- **12** components (P0: 8, P1: 4, P2: 0)
- **4** business flows
- **20** dependencies
- **5** single points of failure (single instance)
- **6** P0 components in a single region
- **3** critical risks (score >= 15)

## Single points of failure

These components have a single instance. Losing one directly impacts every
flow that depends on it — or blocks deployments for support components.

| Component | Category | Criticality | Owner | Dependents | Risks | Action |
|---|---|---|---|---|---|---|
| `dns-global` — Global DNS / name resolution | Network | P0 | net-team | 4 | R-002 | Deploy a second anycast DNS provider and test a full failover. |
| `idp-oidc` — OIDC identity provider | Identity | P0 | sec-team | 2 | R-001 | Federate a backup IdP and test the failover. |
| `network-hub` — Inter-site network hub (on-prem) | Network | P0 | net-team | 3 | R-003 | Duplicate the hub and enable redundant BGP. |
| `payments-api` — External payments API | External service | P0 | payments-team | 1 | R-007 | Negotiate a contractual SLA and a second payment processor. |
| `argocd` — GitOps orchestrator (Argo CD) | Orchestration | P1 | platform | 0 | R-006 | Run 2 replicas and restore from Git in under 8 hours. |

### P0 components in a single region

| Component | Regions | Provider | Owner |
|---|---|---|---|
| `dns-global` | global | single DNS provider | net-team |
| `idp-oidc` | eu-west-3 | single SaaS | sec-team |
| `k8s-control` | eu-west-1 | cloud (EKS eu-west-1) | platform |
| `kafka-bus` | eu-west-3 | cloud (MSK eu-west-3) | data-platform |
| `network-hub` | on-prem-dc1 | on-prem DC1 | net-team |
| `payments-api` | eu-west-3 | third party (SaaS) | payments-team |

## RTO / RPO matrix

RTO = maximum time to restore service. RPO = maximum acceptable data loss.

| Flow | Criticality | Availability | RTO | RPO | Owner | Last restore test |
|---|---|---|---|---|---|---|
| `identity-auth` — User authentication | P0 | 99.99% | 15m | 0 | sec-team | 18 d |
| `order-to-cash` — Order to cash | P0 | 99.95% | 30m | 5m | commerce-team | 39 d |
| `analytics-ingestion` — Analytics ingestion | P1 | 99.50% | 4h | 1h | data-platform | **98 d (stale)** |
| `deploy-pipeline` — Deployment pipeline | P2 | 99.00% | 8h | 24h | platform | **142 d (stale)** |

### Recovery strategies

- **analytics-ingestion**: Kafka event replay + reconciliation from pg-core; acceptable loss limited to the lake.
- **deploy-pipeline**: Re-apply manifests from the Git repository; no business data loss.
- **identity-auth**: Local session cache + backup IdP being deployed; RPO 0 because identity has no critical state on the platform side.
- **order-to-cash**: Multi-AZ + asynchronous replication to the secondary DC + immutable backups + circuit breaker on the payment API.

## Risk register

Sorted by descending score (likelihood × impact).

| ID | Risk | Components | Score | Severity | Status | Owner | Due |
|---|---|---|---|---|---|---|---|
| R-007 | External payments API unavailable | `payments-api` | 16 | critical | in_progress | payments-team | 2026-11-30 |
| R-001 | Single identity provider | `idp-oidc` | 15 | critical | in_progress | sec-team | 2026-12-15 |
| R-002 | Single DNS provider | `dns-global` | 15 | critical | in_progress | net-team | 2026-12-20 |
| R-004 | Single-region event bus | `kafka-bus` | 12 | high | in_progress | data-platform | 2026-12-10 |
| R-003 | Single inter-site network hub | `network-hub` | 10 | high | open | net-team | 2026-12-31 |
| R-005 | Single-region Kubernetes control plane | `k8s-control` | 10 | high | open | platform | 2027-01-15 |
| R-008 | Analytics restore not validated | `obj-lake` | 9 | high | open | data-platform | 2026-12-05 |
| R-006 | Single-instance GitOps orchestrator | `argocd` | 6 | moderate | in_progress | platform | 2026-11-30 |

### Critical action plans

- **R-007 — External payments API unavailable** (16): Negotiate a contractual SLA and a second payment processor. — payments-team, due 2026-11-30.
- **R-001 — Single identity provider** (15): Federate a backup IdP and test the failover. — sec-team, due 2026-12-15.
- **R-002 — Single DNS provider** (15): Deploy a second anycast DNS provider and test a full failover. — net-team, due 2026-12-20.

## Restore tests to refresh

| Flow | Criticality | Age of last test |
|---|---|---|
| analytics-ingestion | P1 | 98 days |
| deploy-pipeline | P2 | 142 days |

Rule: a restore test must be refreshed at least every 90 days.

## Links

- [Dependency graph](dependency-graph.md)
- [Concepts](../concepts.md)
- [Quickstart](../quickstart.md)
