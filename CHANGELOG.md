# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.2.0] - 2026-05-12

### Added

#### MXM Package Standardisation
- Added full `mxm-foundry` compliance.
- Added canonical MXM package structure:
  - `src/mxm/secrets`
  - PEP 420 namespace package layout
  - `py.typed` packaging marker
- Added canonical `pyrightconfig.json`.
- Added canonical `Makefile` targets and CI-compatible validation workflow.
- Added `CHANGELOG.md` following Keep a Changelog structure.

#### Typing
- Added strict Pyright compatibility across the package.
- Added explicit backend callable typing via typed backend dispatch records.
- Added typed CLI and backend interfaces.
- Added typed pytest monkeypatch and subprocess test doubles.

#### Testing
- Added and hardened backend tests for:
  - gopass resolution
  - environment fallback behavior
  - dispatch logic
  - CLI integration
- Added strict `make check` integration:
  - Ruff
  - Black
  - Isort
  - Pyright
  - Pytest

#### Packaging
- Added PyPI-ready packaging metadata.
- Added canonical Poetry package inclusion:
  ```toml
  packages = [{ include = "mxm", from = "src" }]
  ```

### Changed

#### Backend Dispatch Architecture
- Refactored backend dispatch from nested untyped dictionaries to typed backend records.
- Introduced explicit backend callable contracts:
  - access functions
  - readiness checks
- Improved static type safety and Pyright inference across dispatch resolution.

#### Repository Standards
- Renamed default Git branch from `master` to `main`.
- Updated project structure to align with current MXM ecosystem publication standards.

#### Documentation
- Clarified package philosophy around:
  - explicit secret access
  - scoped retrieval
  - backend composability
  - operational isolation
- Improved documentation for:
  - gopass integration
  - environment fallback behavior
  - CLI usage
  - secret store structure

### Fixed

- Fixed Pyright unknown callable inference errors in backend dispatch.
- Fixed subprocess monkeypatch typing issues in pytest suite.
- Fixed test double signature mismatches for `subprocess.check_output`.
- Fixed packaging metadata to comply with MXM namespace package policy.
- Fixed strict typing issues preventing clean `make check`.

### Notes

- This release establishes `mxm-secrets` as a reusable public MXM infrastructure package.
- `mxm-secrets` is intended to provide the canonical secret access abstraction across the MXM ecosystem.
- Operational secrets remain external to all MXM repositories and are expected to be managed via:
  - `gopass`
  - environment variables
  - future Vault/Age integrations

### Upgrade Guidance

Replace Git-based dependency declarations:

```toml
mxm-secrets = { git = "https://github.com/moneyexmachina/mxm-secrets.git", branch = "master" }
```

with versioned package dependencies:

```toml
mxm-secrets = "^0.2.0"
```

Then update lockfiles:

```bash
poetry lock
poetry install
```

## [0.1.1] - 2025-10-31

### Added

- Initial public release of `mxm-secrets`.
- Minimal secret access abstraction for the MXM ecosystem.
- `gopass` backend support.
- Environment variable fallback backend.
- `get_secret(...)` public API.
- Basic CLI integration.
- Initial pytest coverage.
- Poetry packaging and namespace package structure.

### Notes

- This release established the initial operational philosophy for explicit, scoped, process-local secret access within MXM.

