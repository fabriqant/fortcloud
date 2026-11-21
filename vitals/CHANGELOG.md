# Changelog — Fortcloud Vitals

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone quality model with four YAML files: `services.yaml`, `signals.yaml`, `objectives.yaml`, `checks.yaml`.
- Millisecond-aware duration format: `0` or `<number><ms|s|m|h|d>`, combinable (`1m30s`, `150ms`).
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- Error-budget computation for percentile targets; alert margin and sampling checks for duration targets.
- Semantic checks: alert tightness, signal kind, P0 availability and data-quality coverage, check freshness, evidence, result and runbook.
- CLI commands `validate`, `dashboard`, `signals`, `plan`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `slo-dashboard.md`, `signal-catalog.md`, `quality-plan.md`, `vitals-status.json`.
- Working hybrid/multi-cloud example, 19 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud-io/releases/tag/vitals-v0.1.0
