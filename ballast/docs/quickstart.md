# Quickstart

## Install

```bash
cd fortcloud/ballast
python -m pip install -e .
fortcloud-ballast --version
```

## Run on the bundled example

```bash
fortcloud-ballast check --out ./docs/generated
```

You get 7 warnings on purpose. Read them — they are the point of the demo.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-ballast-model
fortcloud-ballast check --model ./my-ballast-model --out ./my-ballast-artifacts
```

The four files must keep their names:

- `services.yaml` — services with `latency_budget`, criticality and owner;
- `dependencies.yaml` — outbound calls with type, operation and idempotency;
- `policies.yaml` — timeout, retries, backoff, breaker, bulkhead and fallback;
- `flows.yaml` — ordered steps referencing a dependency and its policy.

Durations are `0` or `<number><ms|s|m|h|d>` and can be combined: `150ms`, `1m30s`, `2m12s`. Internally everything is stored as integer milliseconds, so `format_duration()` output can be pasted straight back into the model.

## CI gate

Once the model is clean:

```bash
fortcloud-ballast check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-ballast-policies`.

## Fixing a finding

| Message | Fix |
|---|---|
| `worst case 3s exceeds the 1s latency budget` | reduce timeouts/retries, or revise the SLO |
| `step 'dep-catalog' consumes 74% of the latency budget` | tighten that policy or reorder the chain |
| `retries without jitter` | enable jitter on the retry policy |
| `4 retries exceed the maximum of 3` | reduce retries or move the work to a queue |
| `backoff multiplier 1 is below 2` | use exponential backoff (`2` or more) |
| `no bulkhead isolation` | assign a dedicated worker/connection pool |
| `optional dependency has no fallback` | declare `cached`, `default`, `degraded` or `queue` |
| `retries on a non-idempotent write` | set `retries: 0` or add an idempotency key |
