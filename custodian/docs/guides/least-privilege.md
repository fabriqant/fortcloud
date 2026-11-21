# Least privilege guide

## Start from the action, not the role name

Write down the exact calls an identity makes, then map them to permissions. A role name like `developer` or `deployer` is a label — the `permissions` list is the contract Custodian checks.

```yaml
permissions: [deploy:create, deploy:rollback, secrets:read, read:logs]
resources: [proj/prod/checkout/*]
```

Never use `*`, `*:*` or a prefix wildcard: Custodian treats every permission containing `*` as an error. If the list grows beyond 8 entries, split the identity rather than growing the grant.

## One identity, one environment

Declare the allowed environments on the principal:

```yaml
principals:
  - id: ci-deploy
    type: ci
    environments: [prod]
```

A CI identity scoped to several environments is a warning. Use `ci-staging`, `ci-prod`, and so on. This limits the blast radius of a leaked token and makes audit entries unambiguous.

## Elevated roles are exceptions with an end date

```yaml
- id: grant-alice-admin
  role: admin
  environment: dev
  permissions: [read:code, write:config, iam:grant, secrets:read]
  expires: "2026-12-31"
  approval: change-board
```

An `admin`, `owner`, `root` or `superuser` grant without `expires` is an error. A grant that expires more than 365 days from today is a warning; a grant already expired is an error. Short, approved windows are the point.

## Restricted environments need approval

Any grant whose environment is classified `restricted` must carry an `approval` field naming the board or process that approved it. Custodian warns when it is missing.

## Resource patterns must match the environment

A resource such as `proj/dev/*` inside a `prod` grant is an error. Use the environment id in the path so a reviewer can spot the boundary immediately.

## Review the generated matrix

`access-matrix.md` lists every grant with its principal type, environment, classification, permission count and expiry. Sort review meetings by that table: elevated and broad grants first, then anything `AT RISK`.
