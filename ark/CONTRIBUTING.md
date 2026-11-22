# Contributing to FortCloud Ark

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud.git
cd fortcloud/ark
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
```

## Day-to-day

```bash
python -m unittest discover -s tests -v
fortcloud-ark check --out ./docs/generated
fortcloud-ark check --strict --out ./artifacts
```

## Rules for changes

1. **Model contract changes require a schema change.** Edit `schema/*.schema.json` and add a test.
2. **Check changes require a test.** Add a case to `tests/test_validate.py`.
3. **Renderer changes require a test.** Add a case to `tests/test_render.py`.
4. **Generated files are disposable.** Never edit `docs/generated/` by hand; regenerate with `fortcloud-ark check`.
5. **Stay standalone.** Ark must not import `fortcloud_atlas` or `fortcloud_failover`, and does not read their models.
6. **Keep exit codes stable.** `0` success, `1` validation failure, `2` CLI usage error.

## Commit and pull request

- One logical change per commit.
- Describe which rule or artifact changed and include the `check` output.
- The root `.github/workflows/ci.yml` runs the tests and publishes `fortcloud-ark-evidence` for every push and pull request.

## Roadmap ideas

- Import real restore results from CI rather than hand-maintaining `restores.yaml`.
- Verify backup retention against legal/compliance policies per classification.
- Cross-check backup targets with an Atlas risk register (optional, never required at runtime).
- `simulate --asset <id>`: show the restore sequence and cumulative RTO for a service.
