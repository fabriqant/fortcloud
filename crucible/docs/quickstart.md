# Quickstart

## Install

```bash
cd fortcloud/crucible
python -m pip install -e .
fortcloud-crucible --version
```

## Run on the bundled example

```bash
fortcloud-crucible check --out ./docs/generated
```

You get 6 warnings on purpose. They show what a realistic drill programme looks like before cleanup.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-crucible-model
fortcloud-crucible check --model ./my-crucible-model --out ./my-crucible-artifacts
```

The four files must keep their names:

- `environments.yaml` — `environments`;
- `scenarios.yaml` — `participants`, `scenarios`;
- `communication.yaml` — `channels`, `stakeholders`, `plan`;
- `verification.yaml` — `checks`, `signoffs`.

Durations are `0` or `<number><ms|s|m|h|d>` and can be combined (`1h30m`). Quote zero in YAML. Dates are ISO `YYYY-MM-DD`, also quoted.

## CI gate

Once the model is clean:

```bash
fortcloud-crucible check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-crucible-drills`.

## Fixing a finding

| Message | Fix |
|---|---|
| `no passed 'restore' exercise in a controlled environment` | run the drill in an isolated, non-production, approved environment first |
| `environment is not approved for exercises` | get approval and set `approved: true` |
| `no 'verifier' assigned to this exercise` | assign all four required roles |
| `participant 'ghost' not found` | add the person to the roster or correct the id |
| `invalid duration 'two weeks'` | use `1h30m`, `2d`, `0`, etc. |
| `scheduled 37 days ago and still 'planned'` | run the drill or reschedule it |
| `status updates every 30m exceed 15m` | set `plan.updates_every: 15m` or less |
| `no stakeholder is notified at 'start'` | add `start` to a stakeholder's `notify` list |
| `no passed 'service' verification` | add a service check with `result: passed` |
| `no passed 'data' verification` | add a data check with `result: passed` |
| `no approved verifier sign-off` | record an approved sign-off from the verifier |
| `no evidence link` | attach the check to a URL or artefact |
| `signed 1 day(s) before the scheduled exercise` | sign after the drill actually took place |
