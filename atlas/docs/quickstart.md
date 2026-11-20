# Fortcloud Atlas — Quickstart

## 1. Install

```bash
python -m pip install -e .
```

Or, without installing:

```bash
python -m pip install -r requirements.txt
python -m fortcloud_atlas --help
```

Requires Python 3.9+.

## 2. Run on the shipped example

```bash
fortcloud-atlas check
```

You get:

- `docs/generated/dependency-graph.md`
- `docs/generated/resilience-report.md`

The example model is in `examples/hybrid-multicloud/model/`. It intentionally contains warnings (stale restore tests, mono-region P0 components) so you can see the checks fire.

## 3. Point it at your infrastructure

Copy the four YAML files and edit them:

```bash
cp -r examples/hybrid-multicloud/model ./my-model
fortcloud-atlas check --model ./my-model --out ./my-report
```

| File | What to put in it |
|---|---|
| `components.yaml` | Every critical component with category, criticality, owner, provider, regions and redundancy |
| `dependencies.yaml` | Directed edges: `from` depends on `to` |
| `flows.yaml` | Business flows with availability target, RTO/RPO, strategy and last restore test |
| `risks.yaml` | FMEA entries with likelihood, impact, owner, mitigations and corrective action |

Validation will refuse an unknown component reference, a P0 single instance without an owned risk, or a P0 storage component without an immutable backup.

## 4. Add it to CI

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: python -m pip install -e .
- run: fortcloud-atlas check --model ./my-model --out ./report
- uses: actions/upload-artifact@v4
  with:
    name: atlas-report
    path: ./report
```

Exit code is `1` when the model is invalid, so the job fails automatically.

## 5. Tighten the rules

Once the warnings are resolved:

```bash
fortcloud-atlas validate --strict
```

`--strict` turns warnings into errors. A sane progression is: non-strict in CI first, strict after the first cleanup sprint.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Schema introuvable` | Run from the repo root, or pass `--schema-dir /path/to/schema`, or set `FORTCLOUD_ATLAS_SCHEMA_DIR` |
| `Fichier de modèle introuvable` | Check `--model`: it must contain all four YAML files |
| `P0 en instance unique sans risque actif` | Add a `risks.yaml` entry referencing the component with an owner and an action |
| `availability_target does not match ...` | Use two decimals, e.g. `99.95%` |
| `rpo is not of type string` | Quote it: `rpo: "0"` |

## Next

Read [Concepts](concepts.md) for the FMEA scoring and the RTO/RPO definitions.
