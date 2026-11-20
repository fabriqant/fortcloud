# Fortcloud Atlas — Technology context (hybrid / multi-cloud)

Principle: **start simple**, then add tools when the pain is measured. A Git repository with Mermaid and Prometheus beats an expensive platform nobody adopts. This guide places Atlas in the Fortcloud family; the other tools (Failover, Ark, Ballast, Vitals, Custodian, Crucible) are optional and independent.

## Minimal stack for week one

| Need | Choice | Note |
|---|---|---|
| Source of truth | This repo + `model/*.yaml` | Versioned, reviewed in PRs, validated in CI |
| Diagrams | Mermaid (or D2) | Rendered natively by GitHub/GitLab, no server |
| Measurement | Prometheus + Grafana | One control plane across all clouds |
| Backups | Immutable snapshots (object lock) + scripted restore test | The test matters more than the tool |
| Application resilience | Timeouts, retries with backoff, circuit breakers | Implement before buying chaos engineering |

## Target stack by domain

| Domain | Technologies | What it brings |
|---|---|---|
| Infrastructure as Code | OpenTofu / Terraform, Pulumi | Declarative, reproducible, reviewable diffs |
| GitOps | Argo CD, Flux | Desired state in Git; recovery becomes an `apply` |
| Internal catalogue | Backstage | Owners, dependencies and runbooks attached to services |
| C4 modelling | Structurizr DSL, Mermaid, D2 | Context/container views generated from code |
| Real dependency discovery | OpenTelemetry + Tempo / Jaeger | Reveals dependencies absent from documentation |
| Metrics / SLO | Prometheus + Thanos, Grafana, Sloth / Pyrra | Multi-cloud aggregation and error budgets |
| Logs / traces | Loki, Tempo, Elasticsearch if needed | Correlation during game days |
| High availability | Kubernetes (PDB, anti-affinity, HPA), multi-AZ LB, Anycast DNS | Shrinks the blast radius of an instance/AZ failure |
| Data replication | Synchronous replication for RPO ≈ 0, Kafka MirrorMaker 2, multi-region databases | Choose from the RPO, not from fashion |
| Backups | Immutable backups, Vault/KMS, versioned object storage | Ransomware and accidental-deletion protection |
| Identities | Federated OIDC/SAML IdP (Keycloak, Entra ID, Okta), SPIFFE/SPIRE, short-lived credentials | Avoids a single IdP and static secrets |
| Secrets | HashiCorp Vault, cloud KMS, External Secrets Operator | Centralised rotation and audit |
| Network | Cilium / Istio / Linkerd (mTLS, retries), BGP, Transit Gateway | Resilience and visibility for east-west traffic |
| External services | Envoy, Resilience4j, Polly + status-page monitoring | Graceful degradation instead of total outage |
| Chaos / validation | Chaos Mesh, LitmusChaos, Gremlin, AWS FIS, Azure Chaos Studio | Tests the RTO instead of assuming it |
| Risk review | This tool: `risks.yaml` + generated report | Living FMEA with owner and due date per action |

## Choices to avoid

- **Multi-cloud without a common control plane**: two clouds with separate identities, DNS and observability increase operational risk.
- **RPO 0 everywhere**: synchronous replication costs latency and availability. Reserve it for flows that justify it.
- **A single SaaS IdP for every environment, including DR**: the classic SPOF of hybrid architectures.
- **Backstage before clear ownership**: the tool does not create responsibility.
- **Chaos engineering in production without guardrails**: start in pre-production, with a scope and a stop button.

## How Atlas integrates

- `components.yaml` ↔ Backstage catalogue and IaC tags.
- `dependencies.yaml` ↔ OpenTelemetry traces (declared vs observed).
- `flows.yaml` ↔ Sloth/Pyrra SLOs and Grafana dashboards.
- `risks.yaml` ↔ corrective-action backlog and game days.
- CI ↔ validation and report regeneration on every change.
