# Fortcloud Atlas — Concepts and method

This method applies to hybrid and multi-cloud infrastructure: failure domains do not line up with team boundaries or provider boundaries.

## 1. Model flows before components

Do not map "a database, a cluster, a DNS" — map a **service outcome**: *is the order actually captured?* For each flow:

1. Identify the trigger, the data path, the final store and the consumer.
2. Add control dependencies: DNS, IAM/OIDC, secrets, certificates, image registry, orchestrator, observability, CI/CD.
3. Name one owner per flow. A flow without an owner has no credible objective.

The C4 views under `docs/architecture/` provide context; `dependencies.yaml` is the source of truth consumed by the CLI. The generated graph exposes **blast radius**: a node with many inbound arrows is a SPOF candidate.

## 2. Detect single points of failure

Rules applied by `fortcloud-atlas validate` and `fortcloud-atlas report`:

| Rule | Detection | Consequence |
|---|---|---|
| Single instance | `redundancy.instances == 1` | SPOF: everything depends on that one instance |
| Mono-region P0 | `criticality == P0` with one `region` | A regional outage takes it down despite intra-zone redundancy |
| Shared dependency | Several flows point at the same component | Blast radius spans multiple flows, not just instances |
| External service | `category == external_service` | Outside our control: circuit breaker, timeout, fallback and contractual SLA required |

Watch the **invisible dependencies**: DNS, IdP, Vault/KMS, image registry, CA/TLS, NTP, cloud quotas. They never appear in application diagrams yet break everything else.

## 3. FMEA analysis

For each failure mode, fill in `risks.yaml`:

```
score = likelihood (1 to 5) × impact (1 to 5)
```

| Score | Severity | Expected treatment |
|---|---|---|
| 15–25 | Critical | Corrective action planned, with owner and due date (mandatory) |
| 8–14 | High | Mitigation and recovery test within the quarter |
| 4–7 | Medium | Monitor, mitigate if cheap |
| 1–3 | Low | Accept and document |

An "accepted" risk must be reviewed at every architecture review. A critical risk cannot remain `open` without an explanation.

## 4. RTO / RPO: definitions and pitfalls

| Term | Definition | Implication |
|---|---|---|
| **RPO** | Maximum acceptable data loss, in time | RPO ≈ 0 requires synchronous replication; asynchronous replication gives a non-zero RPO that must be measured |
| **RTO** | Maximum time until service is restored | Includes detection, decision, restoration and validation — not just the technical restore time |
| **SLO** | Availability / latency target during normal operation | Must be expressed as measurable SLIs and driven by an error budget |

Classic pitfalls:

- declaring RPO 0 with asynchronous replication;
- confusing HA (survives intra-region failure) with DR (recovers in another region);
- treating a backup as an RTO without a restore test;
- ignoring detection time and human coordination in the RTO;
- assuming multi-cloud protects against a shared IdP or DNS.

Every flow in the model carries its own RTO/RPO pair. A cache may have an "infinite" RPO and a short RTO; a transactional database aims for minutes.

## 5. Validate through experience

The map is only trustworthy when confronted with reality:

- **automated restore tests**: at least every 90 days for P0/P1 flows (`TEST_MAX_AGE_DAYS`);
- **chaos engineering**: kill an instance, an AZ, a standby IdP, an external API in pre-production;
- **game days**: full scenario with owners, measuring the real RTO;
- **CI review**: `make check` on every pull request that touches `model/`.

Gaps between declared and measured RTO are risks of their own — add them to the register.

## 6. Recommended cadence

| Frequency | Action |
|---|---|
| Every PR | CI validation and report regeneration |
| Monthly | Review risks above 8 and stale restore tests |
| Quarterly | Full restore test on P0 flows, update measured RTO/RPO |
| Twice a year | Multi-region / IdP failover game day, review external SLAs |
