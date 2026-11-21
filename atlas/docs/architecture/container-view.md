# C4 view — containers and failure boundaries

Level 2: the components of the model arranged by execution boundary. Colours follow the criticality of the [dependency graph](../generated/dependency-graph.md).

```mermaid
flowchart TB
  classDef p0 fill:#fde2e2,stroke:#c0392b,color:#2b1a1a;
  classDef p1 fill:#fff3cd,stroke:#b8860b,color:#3b2f00;
  classDef p2 fill:#e8f5e9,stroke:#2e7d32,color:#183b1a;

  subgraph CLOUD_A["Cloud A — eu-west-3 / eu-west-1"]
    direction TB
    pg["Primary transactional DB<br/>pg-core"]:::p0
    kafka["Event bus<br/>kafka-bus"]:::p0
    k8s["Kubernetes control plane<br/>k8s-control"]:::p0
    objA["Data lake (replica)<br/>obj-lake"]:::p0
    idp["SaaS IdP<br/>idp-oidc"]:::p0
  end

  subgraph ONPREM["On-prem — DC1"]
    direction TB
    hub["Network hub<br/>network-hub"]:::p0
    vault["Vault / KMS<br/>vault-secrets"]:::p1
    argo["Argo CD<br/>argocd"]:::p1
    etl["ETL workers<br/>etl-workers"]:::p1
    obs["Observability<br/>observability"]:::p1
  end

  subgraph CLOUD_B["Cloud B — europe-west1"]
    objB["Data lake (replica)<br/>obj-lake"]:::p0
  end

  subgraph EXT["External"]
    dns["Global DNS<br/>dns-global"]:::p0
    pay["Payments API<br/>payments-api"]:::p0
  end

  etl --> kafka
  kafka --> pg
  etl --> objA
  objA --> objB
  etl --> pay
  etl --> hub
  pg --> hub
  pg --> vault
  etl --> k8s
  argo --> k8s
  k8s --> idp
  idp --> dns
  pg --> dns
  obs -.-> etl
```

## Failure boundaries

| Boundary | What it protects | What it does not protect |
|---|---|---|
| Zones within a region | A server or AZ failure | Regional outage, DNS, IdP |
| Regions within a cloud | A regional outage | Cloud provider outage, shared identity |
| Two clouds | One cloud provider failing | Single DNS, on-prem hub, single SaaS IdP |
| Secondary on-prem site | Failure of the primary DC | Shared SaaS dependencies |

The model does not consider redundancy effective until the corresponding failover test is dated in `model/flows.yaml`.
