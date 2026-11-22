# Changelog — FortCloud Failover

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone failover model with four YAML files: `topology.yaml`, `services.yaml`, `strategies.yaml`, `drills.yaml`.
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- Semantic checks: false redundancy, standby capacity, switchover versus RTO, replication versus RPO, DNS TTL, manual switchover, drill age/result/evidence, uncovered P0 components.
- CLI commands `validate`, `matrix`, `plan`, `drills`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `failover-matrix.md`, `failover-plan.md`, `drill-scenarios.md`, `failover-status.json`.
- Working hybrid/multi-cloud example, 20 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud/releases/tag/failover-v0.1.0
