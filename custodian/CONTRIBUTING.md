# Contributing to FortCloud Custodian

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd fortcloud-io/custodian
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e .
```

## Day-to-day

```bash
python -m unittest discover -s tests -v
fortcloud-custodian check --out ./docs/generated
fortcloud-custodian check --strict --out ./artifacts
```

## Rules for changes

1. **Model contract changes require a schema change.** Edit `schema/*.schema.json` and add a test.
2. **Check changes require a test.** Add a case to `tests/test_validate.py`.
3. **Renderer changes require a test.** Add a case to `tests/test_render.py`.
4. **Never allow secret values.** The secret schema intentionally rejects unknown keys; a `value` field must not be added.
5. **Generated files are disposable.** Never edit `docs/generated/` by hand; regenerate with `fortcloud-custodian check`.
6. **Stay standalone.** Custodian must not import any other FortCloud tool package, and does not read their models.
7. **Keep exit codes stable.** `0` success, `1` validation failure, `2` CLI usage error.

## Commit and pull request

- One logical change per commit.
- Describe which control or artifact changed and include the `check` output.
- The root `.github/workflows/ci.yml` runs the tests and publishes `fortcloud-custodian-access` for every push and pull request.

## Roadmap ideas

- Import live IAM policies and diff them against the declared grants.
- Check separation of duties between the author and the approver of a change.
- Verify deployment signatures and provenance (SBOM, attestation).
- Cross-check audit coverage against the sensitive operations found in pipelines and grants.
