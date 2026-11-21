# C4 view — system context

Level 1: the platform in its environment. External systems are sources of risk outside our direct control.

```mermaid
C4Context
  title System context — hybrid / multi-cloud platform

  Person(user, "Internal user", "Places orders, reads dashboards")
  Person(ops, "Engineering team", "Deploys, operates, restores")

  System(platform, "Business platform", "Orders, processing, analytics")
  System_Ext(idp, "Identity provider", "OIDC — single SaaS (SPOF)")
  System_Ext(payments, "Payments API", "Third party — contractual SLA required")
  System_Ext(dns, "Public DNS", "Single provider (SPOF)")
  System_Ext(ci, "Git repository / CI", "Source of manifests and artifacts")

  Rel(user, platform, "Uses", "HTTPS")
  Rel(platform, idp, "Authenticates via", "OIDC")
  Rel(platform, payments, "Charges", "HTTPS")
  Rel(platform, dns, "Resolves names via", "DNS")
  Rel(ci, platform, "Deploys via GitOps")
  Rel(ops, platform, "Operates and restores")
  Rel(ops, ci, "Changes the model and code")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

> Mermaid C4 rendering requires a recent version (≥ 9). The detailed component graph is in [dependency-graph.md](../generated/dependency-graph.md).

## Reading this view

- The user only sees the platform: an IdP, DNS or payments API outage looks like a platform outage to them.
- The engineering team also depends on the Git/CI repository to recover: include it in the SPOF analysis if CI is hosted by a third party.
- Flows and their objectives are detailed in `model/flows.yaml` and the [resilience report](../generated/resilience-report.md).
