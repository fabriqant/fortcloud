# Quickstart

## Install

```bash
cd fortcloud-io/failover
python -m pip install -e .
fortcloud-failover --version
```

## Run on the bundled example

```bash
fortcloud-failover check --out ./docs/generated
```

You get 7 warnings on purpose. Read them — they are the point of the demo.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-failover-model
fortcloud-failover check --model ./my-failover-model --out ./my-failover-artifacts
```

The four files must keep their names:

- `topology.yaml` — components with `role`, `pair`, `region`, `provider`, `capacity`, `health_check`;
- `services.yaml` — services with `rto`, `rpo`, `criticality`, `owner`, `components`;
- `strategies.yaml` — `primary`, `standby`, `mode`, `replication`, timings;
- `drills.yaml` — dated evidence per strategy.

Durations are written as `0` or `<number><s|m|h|d>` and can be combined: `1h30m`, `2m12s`.

## CI gate

Once the model is clean:

```bash
fortcloud-failover check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-failover-plan`.

## Fixing a finding

The message tells you which file and concept is wrong. Examples:

| Message | Fix |
|---|---|
| `false redundancy: both instances are in 'eu-west-1'` | place the standby in another region |
| `switchover 26m exceeds the tightest RTO 15m` | reduce `promotion_time`/`detection_time`, or revisit the RTO |
| `'async' replication cannot satisfy RPO 0` | use `sync`/`stateless`, or accept a non-zero RPO |
| `drill drill-vault is 129 days old` | run the drill and update `last`, `result`, `evidence` |
| `P0 component without a failover strategy` | add a strategy with a standby in `strategies.yaml` |
