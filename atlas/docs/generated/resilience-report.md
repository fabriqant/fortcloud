# Fortcloud Atlas — Resilience Report

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
| `dns-global` — DNS global / résolution | Réseau | P0 | net-team | 4 | R-002 | Mettre en place un second fournisseur DNS anycast et tester une bascule complète. |
| `idp-oidc` — Fournisseur d'identité OIDC | Identités | P0 | sec-team | 2 | R-001 | Fédérer un IdP de secours et tester le basculement. |
| `network-hub` — Hub réseau inter-sites (on-prem) | Réseau | P0 | net-team | 3 | R-003 | Dupliquer le hub et activer BGP redondant. |
| `payments-api` — API de paiement externe | Service externe | P0 | payments-team | 1 | R-007 | Négocier un SLA contractuel et un second processeur de paiement. |
| `argocd` — Orchestrateur GitOps (Argo CD) | Orchestrateur | P1 | platform | 0 | R-006 | Passer à 2 replicas et restaurer depuis Git en moins de 8h. |

### P0 components in a single region

| Component | Regions | Provider | Owner |
|---|---|---|---|
| `dns-global` | global | fournisseur DNS unique | net-team |
| `idp-oidc` | eu-west-3 | SaaS unique | sec-team |
| `k8s-control` | eu-west-1 | cloud (EKS eu-west-1) | platform |
| `kafka-bus` | eu-west-3 | cloud (MSK eu-west-3) | data-platform |
| `network-hub` | on-prem-dc1 | on-prem DC1 | net-team |
| `payments-api` | eu-west-3 | tiers (SaaS) | payments-team |

## RTO / RPO matrix

RTO = maximum time to restore service. RPO = maximum acceptable data loss.

| Flow | Criticality | Availability | RTO | RPO | Owner | Last restore test |
|---|---|---|---|---|---|---|
| `identity-auth` — Authentification des utilisateurs | P0 | 99.99% | 15m | 0 | sec-team | 18 d |
| `order-to-cash` — Commande jusqu'à encaissement | P0 | 99.95% | 30m | 5m | commerce-team | 39 d |
| `analytics-ingestion` — Ingestion analytique | P1 | 99.50% | 4h | 1h | data-platform | **98 d (stale)** |
| `deploy-pipeline` — Chaîne de déploiement | P2 | 99.00% | 8h | 24h | platform | **142 d (stale)** |

### Recovery strategies

- **analytics-ingestion**: Replay des événements Kafka + réconciliation depuis pg-core ; perte acceptable limitée au lac.
- **deploy-pipeline**: Re-apply des manifests depuis le dépôt Git ; aucune perte de données métier.
- **identity-auth**: Sessions en cache local + IdP de secours en cours de déploiement ; RPO 0 car l'identité est sans état critique côté plateforme.
- **order-to-cash**: Multi-AZ + réplication asynchrone vers DC secondaire + backups immuables + circuit breaker sur l'API de paiement.

## Risk register

Sorted by descending score (likelihood × impact).

| ID | Risk | Components | Score | Severity | Status | Owner | Due |
|---|---|---|---|---|---|---|---|
| R-007 | API de paiement externe indisponible | `payments-api` | 16 | critique | in_progress | payments-team | 2026-11-30 |
| R-001 | Fournisseur d'identité unique | `idp-oidc` | 15 | critique | in_progress | sec-team | 2026-12-15 |
| R-002 | DNS unique fournisseur | `dns-global` | 15 | critique | in_progress | net-team | 2026-12-20 |
| R-004 | Bus d'événements mono-région | `kafka-bus` | 12 | élevé | in_progress | data-platform | 2026-12-10 |
| R-003 | Hub réseau inter-sites unique | `network-hub` | 10 | élevé | open | net-team | 2026-12-31 |
| R-005 | Plan de contrôle Kubernetes mono-région | `k8s-control` | 10 | élevé | open | platform | 2027-01-15 |
| R-008 | Restauration analytique non validée | `obj-lake` | 9 | élevé | open | data-platform | 2026-12-05 |
| R-006 | Orchestrateur GitOps en instance unique | `argocd` | 6 | modéré | in_progress | platform | 2026-11-30 |

### Critical action plans

- **R-007 — API de paiement externe indisponible** (16): Négocier un SLA contractuel et un second processeur de paiement. — payments-team, due 2026-11-30.
- **R-001 — Fournisseur d'identité unique** (15): Fédérer un IdP de secours et tester le basculement. — sec-team, due 2026-12-15.
- **R-002 — DNS unique fournisseur** (15): Mettre en place un second fournisseur DNS anycast et tester une bascule complète. — net-team, due 2026-12-20.

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
