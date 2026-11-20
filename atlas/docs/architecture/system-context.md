# Vue C4 — contexte système

Niveau 1 : la plateforme dans son environnement. Les systèmes externes sont des sources de risque hors de notre contrôle direct.

```mermaid
C4Context
  title Contexte système — plateforme hybride / multi-cloud

  Person(user, "Utilisateur interne", "Passe commande, consulte les tableaux de bord")
  Person(ops, "Équipe d'ingénierie", "Déploie, exploite, restaure")

  System(platform, "Plateforme métier", "Commandes, traitements, analytique")
  System_Ext(idp, "Fournisseur d'identité", "OIDC — SaaS unique (SPOF)")
  System_Ext(payments, "API de paiement", "Tiers — SLA contractuel requis")
  System_Ext(dns, "DNS public", "Fournisseur unique (SPOF)")
  System_Ext(ci, "Dépôt Git / CI", "Source des manifests et des artefacts")

  Rel(user, platform, "Utilise", "HTTPS")
  Rel(platform, idp, "Authentifie", "OIDC")
  Rel(platform, payments, "Débite", "HTTPS")
  Rel(platform, dns, "Résout les noms", "DNS")
  Rel(ci, platform, "Déploie via GitOps")
  Rel(ops, platform, "Exploite et restaure")
  Rel(ops, ci, "Modifie le modèle et le code")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

> Le rendu C4 de Mermaid nécessite une version récente (≥ 9). Le graphe détaillé des composants est dans [dependency-graph.md](../generated/dependency-graph.md).

## Lectures

- L'utilisateur ne voit que la plateforme : une panne de l'IdP, du DNS ou de l'API de paiement se traduit pour lui par une panne de la plateforme.
- L'équipe d'ingénierie est elle-même dépendante du dépôt Git/CI pour rétablir : à inclure dans l'analyse des SPOF si la CI est hébergée chez un tiers.
- Les flux et leurs objectifs sont détaillés dans `model/flows.yaml` et le [rapport de résilience](../generated/resilience-report.md).
