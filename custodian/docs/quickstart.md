# Quickstart

## Install

```bash
cd fortcloud-io/custodian
python -m pip install -e .
fortcloud-custodian --version
```

## Run on the bundled example

```bash
fortcloud-custodian check --out ./docs/generated
```

You get 7 warnings on purpose. Read them — they are the point of the demo.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-custodian-model
fortcloud-custodian check --model ./my-custodian-model --out ./my-custodian-artifacts
```

The four files must keep their names:

- `access.yaml` — `environments`, `principals`, `grants`;
- `secrets.yaml` — `secrets`;
- `changes.yaml` — `pipelines`;
- `audit.yaml` — `sinks`, `operations`.

Dates are ISO `YYYY-MM-DD` and should be quoted in YAML. Secrets contain **references only** — a `value` key is rejected by the schema.

## CI gate

Once the model is clean:

```bash
fortcloud-custodian check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-custodian-access`.

## Fixing a finding

| Message | Fix |
|---|---|
| `wildcard permission '*:*'` | list the exact permissions the identity needs |
| `environment 'prod' is outside the principal scope` | use a dedicated identity scoped to that environment |
| `resource 'proj/dev/*' targets another environment` | correct the resource pattern |
| `expired 42 days ago` | remove the grant or renew it with approval |
| `secret shared across 2 environments` | issue one secret per environment |
| `last rotated 265 days ago` | rotate the secret and update `last_rotated` |
| `review is not required` | set `review.required: true` and at least 2 approvers |
| `missing mandatory test(s): integration` | add the test stage to the pipeline |
| `rollback has no verified date` | perform a rollback drill and record the date |
| `rollback is not automated` | automate the rollback for restricted environments |
| `sensitive operation is not logged` | set `logged: true` and reference a sink |
| `log sink is mutable` | enable immutability / object lock on the sink |
