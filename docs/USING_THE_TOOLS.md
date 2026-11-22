# Using the tools in practice

This guide answers one question: **"I have real infrastructure — what do I actually do with these tools?"**

If you expect an agent that continuously discovers your cloud accounts, these tools will look empty. They are deliberately not that. They are **declaration → validation → evidence** tools: you maintain a small, versioned description of your infrastructure, and the tools check whether the resilience story it tells is coherent.

## 1. The mental model

```text
Your cloud accounts            Your model (YAML, in Git)           Generated artifacts
(AWS / Azure / GCP)  ──propose──▶  components, dependencies,  ──check──▶  graphs, reports,
                                  flows, risks, evidence                   status JSON
```

- The **model is the source of truth**. It lives in `web/workspaces/<tool>/model/` when you use the console, or in `<tool>/examples/hybrid-multicloud/model/` when you use a CLI directly.
- A **connector only proposes**. It writes `components.yaml` into `web/workspaces/atlas/imports/`. Nothing is applied until you review and accept the proposal in the console.
- **Generated files are disposable**. Graphs and reports are rebuilt by `check`; never edit them by hand.
- The console never receives cloud credentials. It can run the local connectors on request, using your already-configured cloud CLI profiles.

## 2. What "reviewable in a pull request" means

A **pull request** (PR) is a Git workflow: you change files on a branch, open a request to merge that branch, and teammates review the diff before it lands. CI runs automatically on that diff.

Applied here:

1. Someone changes `components.yaml` because a database lost its standby.
2. The PR shows the exact line that changed — no hidden state, no dashboard snapshot.
3. CI runs `fortcloud-atlas check --strict`. If the change creates an unmitigated single point of failure, the command exits `1` and the PR cannot merge.
4. A reviewer discusses the *decision* ("do we accept this risk?"), not the syntax.

This is pertinent because resilience claims are usually **assertions without evidence**. Putting them in versioned files makes them diffable, testable and attributable. It is not the only possible design: a live discovery platform would show current state, but it would also need credentials, hosting, auth and drift handling. This repository chooses the smaller, auditable trade-off: **a curated model, reviewed like code**.

## 3. End-to-end walkthrough

### Step 1 — Pick one tool and one scope

Start with **Atlas** and one production service. Atlas answers "where is the risk and what is the blast radius?" The other six tools answer different questions and have independent models.

### Step 2 — Get an inventory proposal

In the web console, click **Cloud connectors** in the header. Choose AWS, Azure or Google Cloud, fill in the non-secret identifiers, and run the local connector. It writes `web/workspaces/atlas/imports/components.yaml`.

You can also run the same commands yourself:

```bash
python -m pip install -r web/connectors/requirements-aws.txt
python -m connectors.aws --profile my-profile --region eu-west-3

python -m pip install -r web/connectors/requirements-azure.txt
python -m connectors.azure --subscription-id 00000000-0000-0000-0000-000000000000

python -m pip install -r web/connectors/requirements-gcp.txt
python -m connectors.gcp --project-id my-project
```

If your infrastructure is defined in Terraform, `terraform show -json > tfstate.json` is often a better source than the cloud APIs. Each collector maps resources to Atlas components with deliberate defaults: `criticality: P1`, `owner` from tags when present, and `backup.enabled: false`.

### Step 3 — Review, do not blindly accept

Open the **Import** tab, read the unified diff, then accept or discard.

> Accepting a proposal **replaces** the whole `components.yaml` file. Create a scenario first if you want a copy of the previous model.

### Step 4 — Add what no API can tell you

Cloud APIs return resources. They do not know:

- which component is truly `P0`;
- who is accountable;
- whether a restore test actually happened;
- which dependency is required or optional.

Complete `dependencies.yaml`, `flows.yaml` and `risks.yaml`, and enrich the components. Example:

```yaml
  - id: pg-azure
    name: Azure Database for PostgreSQL
    category: storage
    criticality: P0
    owner: data-platform
    provider: azure
    environments: [prod]
    regions: [francecentral]
    zones: [az1, az2]
    redundancy:
      instances: 2
      active_passive: true
      replication: sync
    backup:
      enabled: true
      immutable: false
      retention_days: 35
      last_restore_test: "2026-11-02"
    notes: Restore test evidence DR-2026-11. Geo-redundancy disabled.
```

And the dependency that APIs cannot infer:

```yaml
  - id: d-101
    from: payments-api
    to: pg-azure
    kind: data
    required: true
    description: Synchronous write path. No fallback database.
```

### Step 5 — Validate and generate

In the console: **Validate**, then **Check**. Read the findings, then open **Outputs** for the graph, reports and status JSON.

From the CLI, against the same console workspace:

```bash
fortcloud-atlas check --model web/workspaces/atlas/model --out web/workspaces/atlas/artifacts --strict
```

Every tool returns `0` on success and `1` on validation failure; `--strict` turns warnings into failures.

### Step 6 — Put it in CI

Commit the model, then run the same command on each pull request. A change that breaks redundancy or removes restore evidence fails the build. That is the practical meaning of "make infrastructure risk reviewable in a pull request".

## 4. The seven questions

| Tool | Question it answers |
|---|---|
| Atlas | Where is the risk, and what is the blast radius? |
| Failover | Can we switch to the standby within the RTO? |
| Ark | Can we restore the data within the RTO/RPO, with evidence? |
| Ballast | Can the request chain still meet its latency budget when a dependency fails? |
| Vitals | Can we see a breach early enough, with credible SLOs and data quality? |
| Custodian | Is access least-privileged, are secrets safe, can every change be audited? |
| Crucible | Have we actually rehearsed restore, failover and recovery? |

Each tool is independent and reads its own four YAML files. Nothing is derived from Atlas automatically: you can feed the other models from the same inventory, but you must do it explicitly.

## 5. Current limits

- No continuous discovery, no drift detection, no live monitoring.
- No authentication or multi-user hosting in the console; it binds to `127.0.0.1`.
- Azure and GCP use generic resource listings; tags and evidence still need enrichment.
- Accepting an import replaces a model file; it is not a merge.
- `web/workspaces/` and `web/catalog.sqlite3` are local and ignored by Git.

See [web/README.md](../web/README.md) for API details and [atlas/docs/explained.md](../atlas/docs/explained.md) for a plain-language introduction to the terminology.
