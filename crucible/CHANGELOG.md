# Changelog — Fortcloud Crucible

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone drill model with four YAML files: `environments.yaml`, `scenarios.yaml`, `communication.yaml`, `verification.yaml`.
- Controlled-first rule: isolated, non-production, approved environments; a production drill needs a passed rehearsal of the same kind in a controlled environment.
- Role assignments: coordinator, operator, communicator and verifier drawn from a participant roster.
- Communication plan: channels, stakeholder notifications at start/update/end, cadence and escalation.
- Verification: passed service and data checks, evidence links and an approved verifier sign-off before a drill can be marked passed.
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- CLI commands `validate`, `scenarios`, `roles`, `communication`, `verification`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `scenario-plan.md`, `roles-matrix.md`, `communication-plan.md`, `verification-report.md`, `crucible-status.json`.
- Working hybrid/multi-cloud example, 20 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud-io/releases/tag/crucible-v0.1.0
