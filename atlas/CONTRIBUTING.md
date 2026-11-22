# Contributing to FortCloud Atlas

Thanks for helping make infrastructure risk visible.

## Setup

```bash
git clone https://github.com/fabriqant/fortcloud-io.git
cd atlas
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
make test
make check
```

## Ground rules

1. **The model is the source of truth.** Never hand-edit files in `docs/generated/`.
2. **Changes to rules need a test.** Validation logic lives in `src/fortcloud_atlas/validate.py`; tests live in `tests/`.
3. **Changes to the model format need a schema update** in `schema/` and a note in `CHANGELOG.md`.
4. **Architectural choices go in an ADR** under `docs/adrs/` using the existing numbering.
5. **Keep the tool standalone.** Atlas must not import or require another FortCloud tool.

## Adding a validation rule

- Put the rule in `semantic_checks()` in `src/fortcloud_atlas/validate.py`.
- Use `Error` for a broken guarantee (invalid reference, P0 without mitigation) and `Warning` for a risk that should be reviewed.
- Add a test with a temporary model in `tests/test_validate.py`.
- Document the rule in `README.md` and `docs/concepts.md`.

## Commit and PR conventions

- Conventional commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- PR description should state: what changed, which rule or output is affected, and whether the example model was updated.
- CI must be green: unit tests + `fortcloud-atlas check`.

## Reporting issues

Open an issue with the command you ran, the relevant YAML snippet (redacted), the CLI output and your Python version. Do not paste production secrets or live topology if it is sensitive.

## License

By contributing you agree that your changes are licensed under the MIT License.
