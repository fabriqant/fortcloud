# Changelog — Fortcloud Ballast

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone resilience model with four YAML files: `services.yaml`, `dependencies.yaml`, `policies.yaml`, `flows.yaml`.
- Millisecond-aware duration format: `0` or `<number><ms|s|m|h|d>`, combinable (`1m30s`, `150ms`).
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- Semantic checks: timeout budget, dominant step, retry amplification, jitter, exponential backoff, circuit breakers, bulkheads, fallbacks, non-idempotent writes.
- CLI commands `validate`, `budget`, `policies`, `plan`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `timeout-budget.md`, `policy-matrix.md`, `resilience-plan.md`, `ballast-status.json`.
- Working hybrid/multi-cloud example, 19 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud-io/releases/tag/ballast-v0.1.0
