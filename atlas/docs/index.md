# Fortcloud Atlas — Overview

**Dependency & Risk Map for hybrid and multi-cloud infrastructure.**

Atlas answers four questions for an engineering team:

1. What does the system depend on, including the invisible dependencies (DNS, IdP, secrets, network hub, CI/CD)?
2. Which components are single points of failure, and how large is their blast radius?
3. What availability, RTO and RPO does each business flow promise?
4. Are those promises backed by a dated restore test and an owned mitigation?

## How it works

```text
model/*.yaml  ──►  validate  ──►  graph + report  ──►  CI artifact
   (edit)            (rules)         (generated)
```

- The **model** is four small YAML files you own and version.
- **Validation** applies JSON Schemas plus resilience rules (P0 SPOF without owner = error).
- **Rendering** produces a Mermaid dependency graph and a Markdown resilience report.
- Generated files are disposable: never edit them by hand.

## Where it sits in the Fortcloud family

Atlas is the mapping layer. It is intentionally standalone — no backend, no agent, no dependency on the other tools:

| Tool | Role | Uses Atlas output? |
|---|---|---|
| **Atlas** | Dependency & Risk Map | — |
| Failover | SPOF Eliminator | Yes, optionally |
| Ark | Backup & Restore Prover | Yes, optionally |
| Ballast | Fault-Tolerant Processing | Yes, optionally |
| Vitals | Service & Data Health | Yes, optionally |
| Custodian | Access & Change Guard | No |
| Crucible | Failure Drill Runner | Yes, optionally |

## Read next

- [Quickstart](quickstart.md)
- [Concepts, SPOF rules, FMEA and RTO/RPO](concepts.md)
- [Service levels and error budgets](guides/service-levels.md)
- [Technology context](guides/technology.md)
- [C4 system context](architecture/system-context.md)
- [C4 container view](architecture/container-view.md)
- [ADR 0001 — YAML as source of truth](adrs/0001-yaml-as-source-of-truth.md)
- [Runbook template](templates/runbook.md)
