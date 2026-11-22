# Contributing to FortCloud Ballast

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud.git
cd fortcloud/ballast
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
```

## Day-to-day

```bash
python -m unittest discover -s tests -v
fortcloud-ballast check --out ./docs/generated
fortcloud-ballast check --strict --out ./artifacts
```

## Rules for changes

1. **Model contract changes require a schema change.** Edit `schema/*.schema.json` and add a test.
2. **Check changes require a test.** Add a case to `tests/test_validate.py`.
3. **Renderer changes require a test.** Add a case to `tests/test_render.py`.
4. **Duration changes must round-trip.** `format_duration(parse_duration(x))` must be stable; add a case to `tests/test_core.py`.
5. **Generated files are disposable.** Never edit `docs/generated/` by hand; regenerate with `fortcloud-ballast check`.
6. **Stay standalone.** Ballast must not import `fortcloud_atlas`, `fortcloud_failover` or `fortcloud_ark`, and does not read their models.
7. **Keep exit codes stable.** `0` success, `1` validation failure, `2` CLI usage error.

## Commit and pull request

- One logical change per commit.
- Describe which rule or artifact changed and include the `check` output.
- The root `.github/workflows/ci.yml` runs the tests and publishes `fortcloud-ballast-policies` for every push and pull request.

## Roadmap ideas

- Detect cyclic timeout dependencies between flows.
- Import measured p99 latencies from tracing to compare with declared timeouts.
- Check retry budgets against service error budgets (SLO-based admission control).
- Validate bulkhead size against concurrency limits declared in deployment manifests.
