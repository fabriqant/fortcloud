# Contributing to Fortcloud Crucible

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/crucible
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
```

## Day-to-day

```bash
python -m unittest discover -s tests -v
fortcloud-crucible check --out ./docs/generated
fortcloud-crucible check --strict --out ./artifacts
```

## Rules for changes

1. **Model contract changes require a schema change.** Edit `schema/*.schema.json` and add a test.
2. **Check changes require a test.** Add a case to `tests/test_validate.py`.
3. **Renderer changes require a test.** Add a case to `tests/test_render.py`.
4. **A drill is never green without evidence.** Do not relax the service check, data check or verifier sign-off rules.
5. **Never let a production drill be the first of its kind.** Keep the controlled-first rule.
6. **Generated files are disposable.** Never edit `docs/generated/` by hand; regenerate with `fortcloud-crucible check`.
7. **Stay standalone.** Crucible must not import any other Fortcloud tool package, and does not read their models.
8. **Keep exit codes stable.** `0` success, `1` validation failure, `2` CLI usage error.

## Commit and pull request

- One logical change per commit.
- Describe which control or artifact changed and include the `check` output.
- The root `.github/workflows/ci.yml` runs the tests and publishes `fortcloud-crucible-drills` for every push and pull request.

## Roadmap ideas

- Record measured RTO/RPO from drill timestamps and compare them with declared targets.
- Import real incident timelines and diff them against the communication plan.
- Track findings from failed drills as issues with a due date.
- Generate a calendar of drills from the model.
