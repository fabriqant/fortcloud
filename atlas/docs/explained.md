# FortCloud Atlas, explained simply

> **Map every dependency. See every risk.**

This guide is for someone who has never used Atlas and does not want to guess what the words mean. It explains the idea, the files you write, the checks the CLI runs, the two reports it produces, and every technical term in a glossary at the end.

No cloud account, agent or platform is required: Atlas works on text files you keep in Git.

## The idea in one paragraph

You describe your system in four small YAML files: **what exists**, **what depends on what**, **which business flows matter**, and **what can go wrong**. Atlas checks that the description is complete and consistent, then draws the dependency graph and writes a resilience report. The point is not the document — it is to find, *before* an incident, that a single DNS provider or identity service is holding up four business flows and that nobody has tested a restore in three months.

## Why a normal diagram is not enough

An application diagram usually shows databases and services. It rarely shows:

- DNS, the identity provider (IdP), the secrets vault, the network hub or the CI/CD pipeline;
- whether a component has one instance or several;
- which business flow actually stops when that component fails;
- whether the promised recovery time has ever been tested.

Atlas asks you to write those facts down once, as code, and then checks them automatically on every pull request. If a critical component has one instance and no owner or corrective action, the check fails.

## How Atlas works, step by step

```text
 4 YAML files         structural checks       resilience rules        2 generated files
 components.yaml  ─┐
 dependencies.yaml ─┼──►  JSON Schemas  ──►  errors / warnings  ──►  dependency-graph.md
 flows.yaml       ─┤                                                  resilience-report.md
 risks.yaml       ─┘
      you edit            CLI validates           CLI decides           CLI writes, CI publishes
```

1. **You edit the model.** Four files in `model/`. They are the only source of truth.
2. **The CLI reads the files.** `fortcloud-atlas check` loads them from `--model DIR` (the bundled example by default).
3. **Structural validation.** Each file must match its JSON Schema: correct field names, allowed values, identifiers in the expected format. An unknown field is an error — schemas set `additionalProperties: false`.
4. **Semantic validation.** The CLI applies rules that a schema cannot express: references must exist, a critical single instance needs a risk, restore tests must be recent, and so on.
5. **Rendering.** A Mermaid graph shows `A --> B` for "A depends on B". The report lists single points of failure, an RTO/RPO matrix, the risk register and restore tests to refresh.
6. **CI gate.** The same command runs in GitHub Actions. Exit code `0` means success, `1` means validation failed, `2` means you used the CLI wrongly. Add `--strict` to turn warnings into errors once your model is clean.

Generated files are **disposable**: they are rebuilt every time. Never edit `docs/generated/` by hand.

## The four files, in plain English

| File | What it describes | Everyday analogy |
|---|---|---|
| `components.yaml` | The pieces of the system and their redundancy/backup | An inventory of machines and spare parts |
| `dependencies.yaml` | Directed links: `from` **depends on** `to` | A wall of arrows showing what breaks what |
| `flows.yaml` | The services users actually rely on, with targets | The promises made to customers |
| `risks.yaml` | What could fail, how bad it would be, who fixes it | A risk register with owners and due dates |

### `components.yaml` — what exists

```yaml
- id: pg-core                       # short unique name used by other files
  name: Primary transactional database   # human-readable name
  category: storage                 # storage | processing | orchestration | network | identity | external_service
  criticality: P0                   # P0 critical, P1 important, P2 support
  owner: data-platform              # team accountable for it
  provider: hybride (on-prem + cloud)
  regions: [eu-west-3, on-prem-dc1]
  redundancy:
    instances: 2                    # 1 means a single point of failure
    active_passive: true            # is one instance standing by?
    replication: async              # none | async | sync | multi_region
  backup:
    enabled: true
    immutable: true                 # backups cannot be deleted or altered
    retention_days: 35
    last_restore_test: "2026-10-12"
```

A **component** is any piece the system relies on — including a SaaS product you do not control. Give each one an owner; "the cloud team" is fine, "nobody" is not.

### `dependencies.yaml` — what depends on what

```yaml
- id: d-001
  from: k8s-control       # the component that NEEDS something
  to: dns-global          # the component it NEEDS
  kind: dns               # data | control | identity | network | dns | secret | config
  required: true          # false = the graph draws a dotted arrow
  description: Internal and external name resolution for the cluster.
```

The direction is the most common mistake: the arrow goes **from the consumer to the provider**. If four components point at `dns-global`, a DNS outage breaks all four. That is the **blast radius**.

### `flows.yaml` — what the business promises

```yaml
- id: order-to-cash
  criticality: P0
  availability_target: 99.95%       # normal-operation target
  rto: 30m                          # max time to restore the service
  rpo: 5m                           # max acceptable data loss
  strategy: Multi-AZ + async replication + immutable backups...
  components: [pg-core, kafka-bus, idp-oidc, payments-api, dns-global]
  steps: [...]                      # the narrative of the flow
  external_dependencies: [payments-api]
  last_restore_test: "2026-10-12"
```

Durations are `0` or a number followed by `s`, `m`, `h` or `d`. Quote `"0"` in YAML so it stays text. A flow is the user-visible outcome ("can a customer place an order?"), not a technical task ("is the database up?").

### `risks.yaml` — what can go wrong

```yaml
- id: R-002                         # format R-001, R-002, ...
  title: Single DNS provider
  components: [dns-global]
  flows: [order-to-cash, identity-auth]
  failure_mode: DNS provider outage — every name resolution fails.
  likelihood: 3                     # 1 rare ... 5 frequent
  impact: 5                         # 1 low ... 5 critical
  status: in_progress               # open | in_progress | mitigated | accepted | closed
  owner: net-team
  mitigations: [Short TTLs on critical records]
  action: Deploy a second anycast DNS provider and test a full failover.
  target_date: "2026-12-20"
```

The score is computed for you: `likelihood × impact`, from 1 to 25. You do not write the score in the file — this avoids drift between what people claim and what the model says.

## Reading the two outputs

### The dependency graph (`dependency-graph.md`)

It is a [Mermaid](https://mermaid.js.org/) diagram, so GitHub renders it automatically.

- `A --> B` means **A depends on B**.
- `A -.-> B` means the dependency is not critical (`required: false`).
- **Red** = P0, **amber** = P1, **green** = P2.
- The table "Most depended-upon nodes" counts **direct** incoming arrows. The higher the count, the larger the blast radius.

In the bundled example, `dns-global` receives four required arrows and `network-hub` receives three. That is why they appear at the top of the single-points-of-failure table.

### The resilience report (`resilience-report.md`)

| Section | What it tells you |
|---|---|
| Summary | Counts of components, flows, dependencies, SPOFs, single-region P0s and critical risks |
| Single points of failure | Components with one instance, their owner, their dependents, their linked risk and the corrective action |
| P0 components in a single region | Critical pieces that a whole-region outage would remove |
| RTO / RPO matrix | The declared recovery promise for each flow and the age of its last restore test |
| Recovery strategies | The written plan for each flow |
| Risk register | All risks sorted by descending score, with status, owner and due date |
| Critical action plans | The actions attached to risks scoring 15 or more |
| Restore tests to refresh | Tests missing or older than 90 days |

## The checks, in plain English

| Check | Result | Why it matters | What to do |
|---|---|---|---|
| Files match their JSON Schema; no duplicate ids | **Error** | The model must be unambiguous | Fix the field name, value or duplicate id |
| A dependency or risk points at an unknown component or flow | **Error** | A graph with dangling references cannot be trusted | Declare the component/flow or correct the reference |
| A P0 component with one instance has no active risk, owner and action | **Error** | A critical single point of failure cannot be unmanaged | Add a risk with `status` other than `closed`, an owner and an action |
| A P0 storage component has no immutable backup | **Error** | If the primary copy is lost, an erasable backup is not a backup | Enable an immutable backup |
| A P0 component runs in one region | **Warning** | A regional outage is enough to lose it | Add a second region or document an accepted risk |
| P0 storage has no restore test, or one older than 90 days | **Warning** | An untested backup is a hypothesis | Perform a restore test and update `last_restore_test` |
| A restore test for any flow is missing or older than 90 days | **Warning** | The RTO claim gets weaker every month | Refresh the test |
| A risk scores 15+ and is still open, in progress or accepted | **Warning** | A critical risk needs a visible treatment | Mitigate it or record a reviewed acceptance |
| A component has no declared dependency | **Warning** | It may be orphaned or the model is incomplete | Add its links or document why it stands alone |
| A P0 flow has no associated active risk | **Warning** | The most important flow has no failure analysis | Add a risk linked to that flow |

Errors stop the command. Warnings are shown but the command still succeeds, unless you use `--strict`.

## A guided tour of the bundled example

The example in `examples/hybrid-multicloud/model/` deliberately contains realistic problems. A run on 2026-11-20 produced:

- 12 components (8 P0, 4 P1), 4 business flows, 20 dependencies;
- **5 single points of failure** — `dns-global`, `idp-oidc`, `network-hub`, `payments-api`, `argocd`;
- **6 P0 components in a single region**;
- **3 critical risks** — R-007 (payments API, score 16), R-001 (IdP, 15), R-002 (DNS, 15).

Follow one story through the files:

1. `components.yaml` says `dns-global` has `instances: 1` and `regions: [global]`.
2. `dependencies.yaml` shows that the cluster, the database, the IdP and the payment API all need it.
3. `flows.yaml` says `order-to-cash` is P0 with RTO 30m and RPO 5m, and includes `dns-global`.
4. `risks.yaml` has R-002, likelihood 3 × impact 5 = 15, status `in_progress`, owner `net-team`, action "second anycast DNS provider".
5. The report puts `dns-global` in the SPOF table with 4 dependents and R-002 in the critical action plans.

That is the whole method: one fact per file, assembled automatically into a decision.

## Glossary

| Term | Plain-language definition |
|---|---|
| **Availability target** | The percentage of time a service is expected to work, e.g. `99.95%`. In normal operation, not during recovery. |
| **Backup** | A separate copy of data that can be used to recover it. |
| **Blast radius** | How much is affected when one thing fails. Counted here as the number of components that directly depend on it. |
| **CI (Continuous Integration)** | An automated check that runs when someone proposes a change, here on every pull request. |
| **Component** | Any piece the system relies on — database, queue, DNS, SaaS, network hub. |
| **Criticality (P0 / P1 / P2)** | How urgent it is: P0 critical (interruption unacceptable), P1 important (short degradation tolerated), P2 support (recovery in hours). |
| **Dependency** | A need: "A depends on B". Written `from: A`, `to: B`. |
| **Disaster recovery (DR)** | Recovering in another location after a major failure. Different from HA. |
| **Error / warning** | An error fails the command; a warning is reported but does not fail unless `--strict` is used. |
| **External dependency** | A service you do not operate. You can mitigate its failure but not fix it yourself. |
| **FMEA** | Failure Mode and Effects Analysis: listing what fails, how likely it is, and how bad the impact would be. |
| **HA (High Availability)** | Surviving a local failure (one instance, one zone) without a full disaster recovery. |
| **Impact** | How bad the business consequence is, from 1 (low) to 5 (critical). |
| **Immutable backup** | A backup that cannot be deleted or modified, so ransomware or a mistake cannot erase it. |
| **Instance** | One running copy of a component. One instance means no redundancy. |
| **JSON Schema** | A machine-readable contract describing which fields a YAML file may contain and which values are allowed. |
| **Likelihood** | How often a failure is expected, from 1 (rare) to 5 (frequent). |
| **Mitigation** | Something that reduces the probability or the impact of a failure, short of a full fix. |
| **Mermaid** | A text format that GitHub turns into diagrams. Atlas writes Mermaid so the graph needs no image files. |
| **Multi-cloud / hybrid** | Using several cloud providers, or combining cloud with your own datacentres. |
| **Owner** | The team accountable for a component, flow or risk. |
| **Provider** | Who operates the component: a cloud provider, a SaaS vendor, or your own datacentre. |
| **Region / zone** | A geographic area / an isolated failure domain inside it. A zone failure is smaller than a region failure. |
| **Replication** | Copying data to another place: `none`, `async` (with delay), `sync` (no acknowledged loss) or `multi_region`. |
| **Restore test** | An actual exercise of restoring from backup, with a date. This is what makes a backup credible. |
| **RPO (Recovery Point Objective)** | Maximum acceptable data loss measured in time. RPO 5m means "losing up to five minutes of writes is acceptable". |
| **RTO (Recovery Time Objective)** | Maximum time allowed to get the service back, including detection and validation. |
| **Risk register** | The list of identified risks with score, status, owner, action and due date. |
| **Schema validation** | The first check Atlas runs: does every file obey its contract before any resilience rule is applied? |
| **SLI / SLO** | SLI = a measured signal such as success rate; SLO = the target for that signal (the availability target here). |
| **SPOF (Single Point Of Failure)** | A component with one instance whose failure stops something important. Atlas detects `instances: 1`. |
| **Strict mode** | `--strict` makes warnings fail the command. Useful once the model has no known gaps. |
| **YAML** | A human-readable text format for configuration. Indentation matters; keys and values are written `key: value`. |

## Common mistakes

| Mistake | Correction |
|---|---|
| Writing `A --> B` as "A provides B" | It means "A **depends on** B". Reverse the fields if needed. |
| Declaring RPO 0 with asynchronous replication | Async replication has a delay; measure it and declare a non-zero RPO. |
| Calling a backup a recovery plan | Without a dated restore test, there is no evidence it works. |
| Forgetting DNS, IdP, vault or network links | Those are the dependencies that cause the largest surprise outages. |
| Leaving a critical risk `open` | Give it an owner, an action and a due date, or mark it `accepted` with a review. |
| Editing `dependency-graph.md` by hand | It is regenerated. Edit `dependencies.yaml` instead. |
| Putting secrets in the model | The model is not a secret store; only names and references belong there. |

## Frequently asked questions

**Does Atlas connect to my cloud account?**
No. It reads four YAML files. Nothing is installed on your infrastructure and no credentials are used.

**Does Atlas measure my real RTO?**
No. It checks the RTO/RPO you declared and whether a restore test is recent enough. Actually measuring recovery is what FortCloud Crucible and Ark are for.

**Can I use it with a single cloud provider?**
Yes. The example is hybrid/multi-cloud, but the model has no such requirement.

**What if I add a field that is not in the schema?**
Validation fails with `Additional properties are not allowed`. This is deliberate: a typo should not silently disappear.

**Why 90 days for restore tests?**
It is the built-in `TEST_MAX_AGE_DAYS` rule: a quarterly cadence keeps a declared RTO from quietly becoming fiction.

**Do I need to fix every warning before merging?**
Not necessarily. Use `check` while improving the model; switch CI to `--strict` when the remaining warnings are reviewed and accepted.

## Next

- [Quickstart](quickstart.md) — the commands and their options.
- [Concepts and method](concepts.md) — the reasoning behind the rules.
- [Service levels and error budgets](guides/service-levels.md).
- [Generated resilience report](generated/resilience-report.md) — the real output of the example.
- [Back to the Atlas documentation index](index.md).
