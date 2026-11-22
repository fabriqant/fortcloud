# Changelog

All notable changes to FortCloud Atlas are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses semantic versioning.

## [Unreleased]

### Added

- Nothing yet.

## [0.1.0] — 2026-11-20

### Added

- Four-file YAML model with JSON Schema validation: `components`, `dependencies`, `flows`, `risks`.
- `fortcloud-atlas validate` with structural and resilience rules (P0 SPOF, single-region P0, immutable backups, stale restore tests, FMEA owners and due dates).
- `fortcloud-atlas graph` generating a Mermaid dependency graph with blast-radius ranking.
- `fortcloud-atlas report` generating the RTO/RPO matrix, SPOF audit and risk register.
- `fortcloud-atlas check` combining validation and generation with CI-friendly exit codes.
- Complete hybrid/multi-cloud example model under `examples/hybrid-multicloud/`.
- Documentation: overview, quickstart, concepts, service levels, C4 views, ADRs and runbook template.
- GitHub Actions CI with unit tests and published artifacts.

[Unreleased]: https://github.com/fabriqant/fortcloud/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabriqant/fortcloud/releases/tag/v0.1.0
