# Changelog — FortCloud Custodian

All notable changes to this tool are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-11-21

### Added

- Standalone control model with four YAML files: `access.yaml`, `secrets.yaml`, `changes.yaml`, `audit.yaml`.
- Least-privilege checks: explicit permissions, wildcard rejection, permission count, expiry, approved elevated roles.
- Environment separation: declared environments, per-principal scope, cross-environment resource detection, isolated secrets.
- Secret protection: reference-only schema, rotation policy and age, declared consumers, storage backend inventory.
- Change control: mandatory review and approvers, unit/integration/security tests, scoped deployer, verified automated rollback.
- Audit trail: immutable durable sinks, sensitive-operation coverage, evidence freshness and audit result.
- Four JSON Schemas in `schema/` and structural validation with `jsonschema`.
- CLI commands `validate`, `access`, `secrets`, `changes`, `audit`, `check` with `--model`, `--schema-dir`, `--out`, `--strict`.
- Generated artifacts: `access-matrix.md`, `secret-inventory.md`, `change-control.md`, `audit-trail.md`, `custodian-status.json`.
- Working hybrid/multi-cloud example, 20 unit tests, documentation and root CI job.

[0.1.0]: https://github.com/fabriqant/fortcloud/releases/tag/custodian-v0.1.0
