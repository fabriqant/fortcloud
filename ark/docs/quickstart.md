# Quickstart

## Install

```bash
cd fortcloud/ark
python -m pip install -e .
fortcloud-ark --version
```

## Run on the bundled example

```bash
fortcloud-ark check --out ./docs/generated
```

You get 7 warnings on purpose. Read them — they are the point of the demo.

## Use your own model

Copy `examples/hybrid-multicloud/model/` into your repository and replace its contents:

```bash
cp -r examples/hybrid-multicloud/model ./my-ark-model
fortcloud-ark check --model ./my-ark-model --out ./my-ark-artifacts
```

The four files must keep their names:

- `assets.yaml` — data assets with classification and encryption;
- `backups.yaml` — policies with schedule, retention, immutability and freshness;
- `restores.yaml` — dated restore evidence with measured RTO/RPO;
- `services.yaml` — services that consume the assets and declare RTO/RPO.

Durations are `0` (continuous) or `<number><s|m|h|d>` and can be combined: `1h30m`. Quote zero values in YAML: `rpo: "0"`.

## CI gate

Once the model is clean:

```bash
fortcloud-ark check --strict --out ./artifacts
```

`--strict` makes warnings fail the command. The root CI job publishes the artifacts as `fortcloud-ark-evidence`.

## Fixing a finding

| Message | Fix |
|---|---|
| `P0 backup is not immutable` | enable immutability / object lock on the backup vault |
| `backup schedule 24h cannot satisfy RPO 5m` | use CDC or reduce the schedule below the RPO |
| `measured RTO 45m exceeds target 30m` | improve the restore procedure or revise the target |
| `no ransomware or deletion restore scenario` | run a destructive-scenario restore and record it |
| `restore rst-vault is 129 days old` | re-run the test and update `last`, `result`, `evidence` |
| `no restore test` | add an entry in `restores.yaml` |
