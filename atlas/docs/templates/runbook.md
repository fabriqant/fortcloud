# Fortcloud Atlas — Runbook template

> Copy this template to `docs/runbooks/<flow-id>.md` in your own repository. A tested runbook beats a perfect one.

## Identité du flux

| Champ | Valeur |
|---|---|
| Flux | `<id du flux>` |
| Propriétaire | `<équipe / personne>` |
| Criticité | `P0 / P1 / P2` |
| Disponibilité cible | `<99,xx %>` |
| RTO / RPO | `<minutes> / <minutes>` |
| Dernier test | `<AAAA-MM-DD>` |
| Composants impliqués | `<ids du modèle>` |

## Détection

- **Signaux** : `<alertes Prometheus, logs, status page externe>`.
- **Seuil de déclenchement** : `<ex. > 5 % d'erreurs sur 5 min>`.
- **Impact attendu** : `<que se passe-t-il pour les utilisateurs ?>`.

## Diagnostic rapide

1. `<vérifier le composant le plus en amont du flux>`.
2. `<vérifier les dépendances partagées : DNS, IdP, secrets, réseau>`.
3. `<vérifier si un changement récent est en cause (GitOps, infrastructure)>`.

## Décision

| Situation | Action | Décideur |
|---|---|---|
| `<ex. base indisponible>` | `<bascule vers le DC secondaire>` | `<rôle>` |
| `<ex. IdP hors service>` | `<activer le cache de sessions / IdP de secours>` | `<rôle>` |
| `<ex. API externe dégradée>` | `<mode dégradé : file d'attente locale>` | `<rôle>` |

## Rétablissement

1. `<étape 1 — commande exacte>`.
2. `<étape 2 — vérification>`.
3. `<validation métier : comment savoir que le flux est revenu ?>`.

## Après l'incident

- [ ] Durée réelle du rétablissement : `<...>` — comparée au RTO de `<...>`.
- [ ] Perte de données réelle : `<...>` — comparée au RPO de `<...>`.
- [ ] Mettre à jour `model/risks.yaml` si un nouveau mode de défaillance apparaît.
- [ ] Post-mortem et action corrective : `<lien>`.
