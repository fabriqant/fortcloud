# Contributing to FortCloud Failover

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/failover
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
```

## Day-to-day

```bash
python -m unittest discover -s tests -v
fortcloud-failover check --out ./docs/generated
fortcloud-failover check --strict --out ./artifacts
```

## Rules for changes

1. **Model contract changes require a schema change.** Edit `schema/*.schema.json` and add a test.
2. **Check changes require a test.** Add a case to `tests/test_validate.py`.
3. **Renderer changes require a test.** Add a case to `tests/test_render.py`.
4. **Generated files are disposable.** Never edit `docs/generated/` by hand; regenerate with `fortcloud-failover check`.
5. **Stay standalone.** Failover must not import `fortcloud_atlas` or require Atlas at runtime. The two tools use independent models.
6. **Keep exit codes stable.** `0` success, `1` validation failure, `2` CLI usage error.

## Commit and pull request

- One logical change per commit.
- Describe which rule or artifact changed and include the `check` output.
- The root `.github/workflows/ci.yml` runs the tests and publishes `fortcloud-failover-plan` for every push and pull request.

## Roadmap ideas

- `simulate --kill <component> | --region <region>`: what-if impact and cumulative switchover time.
- Drift detection against declared health probes and DNS TTLs.
- Import of measured drill durations from CI to compare with declared RTO.
