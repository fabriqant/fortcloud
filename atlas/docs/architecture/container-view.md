# Vue C4 — conteneurs et frontières de panne

Niveau 2 : les composants du modèle répartis selon leurs frontières d'exécution. Les couleurs reprennent la criticité du [graphe des dépendances](../generated/dependency-graph.md).

```mermaid
flowchart TB
  classDef p0 fill:#fde2e2,stroke:#c0392b,color:#2b1a1a;
  classDef p1 fill:#fff3cd,stroke:#b8860b,color:#3b2f00;
  classDef p2 fill:#e8f5e9,stroke:#2e7d32,color:#183b1a;

  subgraph CLOUD_A["Cloud A — eu-west-3 / eu-west-1"]
    direction TB
    pg["Base transactionnelle<br/>pg-core"]:::p0
    kafka["Bus d'événements<br/>kafka-bus"]:::p0
    k8s["Plan de contrôle K8s<br/>k8s-control"]:::p0
    objA["Lac de données (réplique)<br/>obj-lake"]:::p0
    idp["IdP SaaS<br/>idp-oidc"]:::p0
  end

  subgraph ONPREM["On-prem — DC1"]
    direction TB
    hub["Hub réseau<br/>network-hub"]:::p0
    vault["Vault / KMS<br/>vault-secrets"]:::p1
    argo["Argo CD<br/>argocd"]:::p1
    etl["Workers ETL<br/>etl-workers"]:::p1
    obs["Observabilité<br/>observability"]:::p1
  end

  subgraph CLOUD_B["Cloud B — europe-west1"]
    objB["Lac de données (réplique)<br/>obj-lake"]:::p0
  end

  subgraph EXT["Externe"]
    dns["DNS global<br/>dns-global"]:::p0
    pay["API paiements<br/>payments-api"]:::p0
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

## Frontières de panne

| Frontière | Ce qu'elle protège | Ce qu'elle ne protège pas |
|---|---|---|
| Zones dans une région | Défaillance d'un serveur ou d'une AZ | Panne régionale, DNS, IdP |
| Régions dans un cloud | Panne régionale | Panne du fournisseur cloud, identité partagée |
| Deux clouds | Panne d'un fournisseur cloud | DNS unique, hub on-prem, IdP SaaS unique |
| Site on-prem secondaire | Panne du DC principal | Dépendances SaaS partagées |

Le modèle ne considère pas qu'une redondance est effective tant que le test de basculement correspondant n'est pas daté dans `model/flows.yaml`.
