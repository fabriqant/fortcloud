# Fortcloud Ark — Restore Evidence

> Generated on 2026-11-21 by `fortcloud-ark evidence`. Do not edit by hand.

Measured values come from the drill record and are compared with the tightest
target of the services using the restored asset.

| Restore | Asset | Scenario | Date | Age | Meas. RTO | Target RTO | RTO | Meas. RPO | Target RPO | RPO | Result | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `rst-config` | `config-repo` | Restauration à un instant donné | 2026-10-20 | 32 d | 2h | 8h | PASS | 0 | 1d | PASS | partial | https://ci.example.com/restores/rst-config-04 |
| `rst-idp` | `idp-db` | Suppression accidentelle | 2026-11-02 | 19 d | 12m | 15m | PASS | 0 | 0 | PASS | passed | https://ci.example.com/restores/rst-idp-23 |
| `rst-kafka` | `kafka-events` | Restauration à un instant donné | 2026-10-30 | 22 d | 45m | 4h | PASS | 30m | 1h | PASS | passed | https://ci.example.com/restores/rst-kafka-09 |
| `rst-lake` | `obj-lake` | Ransomware | 2026-10-25 | 27 d | 3h | 4h | PASS | 50m | 1h | PASS | passed | https://ci.example.com/restores/rst-lake-17 |
| `rst-pg` | `pg-core` | Restauration à un instant donné | 2026-11-08 | 13 d | 26m | 30m | PASS | 4m | 5m | PASS | passed | https://ci.example.com/restores/rst-pg-42 |
| `rst-pg-ransomware` | `pg-core` | Ransomware | 2026-09-30 | 52 d | 28m | 30m | PASS | 5m | 5m | PASS | passed | https://ci.example.com/restores/rst-pg-ransomware-11 |
| `rst-vault` | `vault-secrets` | Perte de région | 2026-07-15 | **129 d (stale)** | 12m | 15m | PASS | 0 | 0 | PASS | passed | https://ci.example.com/restores/rst-vault-08 |

## `config-repo` — Dépôt de configuration GitOps

- **Owner:** platform
- **Criticality:** P1
- **Targets:** RTO 8h / RPO 1d

- `rst-config` — Restauration à un instant donné on 2026-10-20: RTO 2h / RPO 0, result **partial**, evidence https://ci.example.com/restores/rst-config-04
  - Note: Restoration worked but the Git mirror was 20 minutes behind.


## `idp-db` — Base d'identités

- **Owner:** sec-team
- **Criticality:** P0
- **Targets:** RTO 15m / RPO 0

- `rst-idp` — Suppression accidentelle on 2026-11-02: RTO 12m / RPO 0, result **passed**, evidence https://ci.example.com/restores/rst-idp-23


## `kafka-events` — File d'événements

- **Owner:** data-platform
- **Criticality:** P1
- **Targets:** RTO 4h / RPO 1h

- `rst-kafka` — Restauration à un instant donné on 2026-10-30: RTO 45m / RPO 30m, result **passed**, evidence https://ci.example.com/restores/rst-kafka-09


## `obj-lake` — Lac de données objet

- **Owner:** data-platform
- **Criticality:** P0
- **Targets:** RTO 4h / RPO 1h

- `rst-lake` — Ransomware on 2026-10-25: RTO 3h / RPO 50m, result **passed**, evidence https://ci.example.com/restores/rst-lake-17


## `pg-core` — Base transactionnelle principale

- **Owner:** data-platform
- **Criticality:** P0
- **Targets:** RTO 30m / RPO 5m

- `rst-pg` — Restauration à un instant donné on 2026-11-08: RTO 26m / RPO 4m, result **passed**, evidence https://ci.example.com/restores/rst-pg-42
- `rst-pg-ransomware` — Ransomware on 2026-09-30: RTO 28m / RPO 5m, result **passed**, evidence https://ci.example.com/restores/rst-pg-ransomware-11


## `vault-secrets` — Coffre de secrets

- **Owner:** sec-team
- **Criticality:** P0
- **Targets:** RTO 15m / RPO 0

- `rst-vault` — Perte de région on 2026-07-15: RTO 12m / RPO 0, result **passed**, evidence https://ci.example.com/restores/rst-vault-08
  - Note: Old drill and no ransomware scenario — both are flagged.

