# Concepts

Custodian models five connected control families. Each one answers a different question, but they reinforce each other: an access grant is only acceptable if the secret it reads is isolated, the deployment using it is reviewed and the operation is logged.

## 1. Least privilege

A grant says **who** (`principal`), **what** (`permissions`), **where** (`resources`) and **in which environment**, plus an expiry and an optional approval. Least privilege means:

- permissions are explicit — no `*`, `*:*` or `read:*`;
- the permission list is short (8 or fewer);
- elevated roles (`admin`, `owner`, `root`, `superuser`) are time-bound and approved;
- every grant has an expiry, no more than 365 days away;
- resources belong to the declared environment.

Custodian fails validation on wildcards, expired grants and elevated standing access. It warns on broad grants, missing expiry and long-lived access.

## 2. Environment separation

Every environment has a classification: `public`, `internal`, `confidential` or `restricted`. A principal declares the environments it may touch. Custodian checks that each grant stays inside that scope and that resource patterns do not point at another declared environment.

CI identities should be **one per environment**. A single runner scoped to both staging and production is a warning: compromise of that identity crosses the boundary. Secrets inherit the same rule — a secret shared with a restricted environment is an error.

## 3. Secret protection

The model stores only a **reference** (`vault://prod/checkout/db` or `${ENV_VAR}`), never a value. The schema rejects unknown keys, so adding a `value` field fails validation. Each secret declares:

- a store (Vault, AWS/GCP/Azure managers or Kubernetes Secret);
- the environments that may use it;
- a rotation policy and the last rotation date;
- the principals allowed to read it.

Rotation overdue on a restricted secret is an error; on other environments it is a warning. A policy above 90 days is a warning, and a Kubernetes Secret in production is a warning.

## 4. Change control

A pipeline declares its environment, trigger, deployer, review requirements, test stages and rollback configuration. For a restricted environment Custodian requires:

- review with at least 2 approvers;
- unit and integration tests (security test produces a warning if absent);
- a deployer scoped to the target environment;
- rollback enabled, automated and verified within 90 days.

The deployer is a principal from `access.yaml`, so a pipeline cannot silently use an identity that has no access to production.

## 5. Audit trail

Sinks describe where logs go, for how long and whether records can be altered. Operations describe sensitive actions: `grant_change`, `secret_access`, `deploy`, `pipeline_change`, `infra_change`. Custodian requires coverage of the first four, a declared sink for every logged operation, at least 365 days of retention, immutability and recent evidence.

An audit control with `result: failed` is an error — a control that failed is not a control you can claim.

## How they connect

```text
principal ──grant──> environment ──pipeline──> deployer (the same principal)
                          │                         │
                        secret                    audit operation
                          └──────── referenced in evidence ──────┘
```

A reviewer sees all five relationships in one `check` run, in a pull request, without querying the live platform.
