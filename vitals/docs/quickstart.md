# Quickstart

## Install

```bash
cd fortcloud-io/vitals
python -m pip install -e .
fortcloud-vitals --version
```

## Run on the bundled example

```bash
fortcloud-vitals check --out ./docs/generated
```

You get 7 warnings on purpose. Read them — they are the point of the demo.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-vitals-model
fortcloud-vitals check --model ./my-vitals-model --out ./my-vitals-artifacts
```

The four files must keep their names:

- `services.yaml` — criticality and owner;
- `signals.yaml` — source, kind, query and sampling interval;
- `objectives.yaml` — target, alert threshold and window;
- `checks.yaml` — dated verification with result, evidence and runbook.

Durations are `0` or `<number><ms|s|m|h|d>` and can be combined: `150ms`, `1m30s`, `43m12s`. Internally everything is stored as integer milliseconds, so `format_duration()` output can be pasted straight back into the model.

## CI gate

Once the model is clean:

```bash
fortcloud-vitals check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-vitals-dashboard`.

## Fixing a finding

| Message | Fix |
|---|---|
| `alert fires after 80% of the error budget is spent` | tighten the alert threshold to `99.6` or higher |
| `signal interval 15m is too coarse` | sample more often than a tenth of the error budget |
| `alert margin 10% is below the 20% minimum` | lower the alert threshold for duration targets |
| `P0 service has no data-quality objective` | add a freshness, completeness or validity objective |
| `last check is 129 days old` | run the check and update `last` |
| `result is 'partial'` | complete the verification, or fix what it found |
| `no evidence link` | point `evidence` at the CI run or dashboard export |
| `no runbook` | document the response in `runbook` |
| `failed check on a P0 service` | treat it as an incident; fix before release |
