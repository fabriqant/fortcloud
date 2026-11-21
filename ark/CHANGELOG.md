# Changelog — Fortcloud Ark

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone backup/restore model with four YAML files: `assets.yaml`, `backups.yaml`, `restores.yaml`, `services.yaml`.
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- Semantic checks: immutable/encrypted/cross-region backups, backup freshness, schedule versus RPO, restore freshness, measured RTO/RPO versus targets, deletion/ransomware scenarios, evidence links.
- CLI commands `validate`, `coverage`, `evidence`, `plan`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `backup-coverage.md`, `restore-evidence.md`, `recovery-plan.md`, `restore-status.json`.
- Working hybrid/multi-cloud example, 19 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud-io/releases/tag/ark-v0.1.0
