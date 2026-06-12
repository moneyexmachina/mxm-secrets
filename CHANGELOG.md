# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
## [0.3.2] - 2026-06-12

### Changed

- Updated dependency on `mxm-types` to v0.3.1.
- Adopted simplified `RuntimeIdentity` typing based on validated string identifiers.
- Removed dependency on custom runtime identifier alias types throughout the authorization and resolution layers.

### Architecture

`mxm-secrets` now consumes the simplified `RuntimeIdentity` model introduced in `mxm-types` v0.3.1.

Runtime identity dimensions:

```text
app
environment
machine
substrate
role
```

are now represented directly as validated strings.

This simplifies integration with:

```text
runtime identity discovery
configuration loading
tests
CLI tooling
RuntimeContext materialisation
```

while preserving all authorization and secret-resolution semantics.

### Internal

- Simplified RuntimeIdentity construction in tests.
- Removed unnecessary type-conversion helpers introduced solely to satisfy custom runtime identifier aliases.
- Reduced friction at package boundaries between:
  - `mxm-config`
  - `mxm-runtime`
  - `mxm-secrets`

### Compatibility

No configuration format changes.

No secret-resolution behaviour changes.

No public API changes beyond adoption of the simplified `RuntimeIdentity` type definitions provided by `mxm-types` v0.3.1.

## [0.3.1] - 2026-06-09

### Added

- Added config-data ingestion layer for secret stores, secret references, and secret policies.
- Added `SecretsApi.from_config_data(...)` as the preferred construction path for configured secret services.
- Added `SecretStoreRegistry.from_config_data(...)`.
- Added `SecretRefRegistry.from_config_data(...)`.
- Added `SecretPolicyRegistry.from_config_data(...)`.
- Added shared config-data validation helpers for structural configuration validation.
- Added comprehensive test coverage for:
  - config-data ingestion,
  - registry construction from config data,
  - SecretsApi construction from config data.

### Changed

- Extended the public API to support configuration-driven construction of authorization-aware secret services.
- Clarified separation of responsibilities between:
  - `mxm-config` (configuration ownership),
  - `mxm-secrets` (authorization and resolution semantics),
  - `mxm-runtime` (service materialisation and RuntimeContext construction).

### Architecture

This release completes the configuration-ingestion layer of the MXM Runtime Context Architecture:

```text
configuration data
    ↓
SecretStore
SecretRef
SecretPolicy
    ↓
registries
    ↓
SecretsApi
```

`mxm-secrets` now supports construction of fully configured secret-resolution services from plain configuration data while remaining independent of configuration discovery and runtime materialisation concerns.

RuntimeContext integration remains the responsibility of `mxm-runtime`.

## [0.3.0] - 2026-06-09

### Added

#### Resolution Domain Model

Added explicit secret resolution models:

- `SecretStore`
- `SecretRef`
- `ResolvedSecretLocation`

These establish the internal representation of:

```text
logical store
logical secret
resolved backend location
```

and replace direct dependency on backend paths throughout the package.

---

#### Registry Infrastructure

Added typed registries:

- `SecretStoreRegistry`
- `SecretRefRegistry`
- `SecretPolicyRegistry`

The registries provide immutable lookup and validation for configured secret metadata.

---

#### Authorization Domain Model

Added authorization primitives:

- `Principal`
- `SecretPolicy`

Added explicit authorization vocabulary:

```text
marketdata
execution
research
human_admin
```

and policy-based access control through:

```python
SecretPolicy(
    name="marketdata_access",
    allowed_principals=(...)
)
```

---

#### Policy Evaluation

Added authorization evaluation layer:

```python
is_secret_access_allowed(...)
```

Authorization is now evaluated independently of storage and backend retrieval.

Added:

- policy evaluation tests
- authorization failure handling
- policy registry integration

---

#### RuntimeIdentity Integration

Added explicit RuntimeIdentity support.

Secret access now requires:

```python
RuntimeIdentity
```

and no longer relies on implicit process identity.

Added:

```python
principal_from_runtime_identity(...)
```

Current mapping:

```text
RuntimeIdentity.role
    ↓
Principal
```

---

#### SecretsApi

Added authorization-aware API orchestration.

`SecretsApi` now performs:

```text
secret name
    ↓
SecretRef
    ↓
Principal derivation
    ↓
Policy evaluation
    ↓
Store resolution
    ↓
Backend retrieval
```

through a single API boundary.

---

#### Validation Infrastructure

Added shared validation utilities:

- `validate_identifier(...)`
- `validate_non_empty_clean(...)`

Applied consistently across:

- principals
- secret references
- secret stores
- secret policies

---

### Changed

#### Secret Access Architecture

Refactored the package from a backend-oriented secret lookup abstraction into an authorization-aware secret resolution system.

Applications now depend on:

```text
logical secret names
```

rather than:

```text
backend paths
```

or backend-specific storage semantics.

---

#### Identifier Convention

Standardized identifier semantics across the package.

Adopted:

```text
snake_case
```

identifier format:

```text
^[a-z][a-z0-9_]*$
```

Examples:

```text
marketdata
marketdata_access
databento_api_key
human_admin
```

---

#### Public API Design

Replaced direct secret retrieval patterns with a configured API object:

```python
SecretsApi(...)
```

Secret retrieval now requires:

```python
api.get_secret(
    secret_name=...,
    identity=runtime_identity,
)
```

---

### Removed

#### Environment Backend

Removed environment variable secret resolution.

The package now supports:

```text
gopass
```

as the active backend implementation.

Backend abstraction remains in place for future expansion.

---

#### Implicit Authorization

Removed the assumption that successful backend retrieval implies authorization.

Authorization is now an explicit package responsibility.

---

### Notes

This release completes the Resolution layer of the MXM Runtime Context Architecture.

The package now provides:

```text
SecretRef
    ↓
Authorization
    ↓
SecretStore
    ↓
Backend Retrieval
```

through a fully typed and tested API.

Configuration materialisation remains outside package scope and will be introduced through RuntimeContext construction in a future release.

---

### Upgrade Guidance

Direct use of:

```python
get_secret(...)
```

should be migrated to:

```python
SecretsApi(...)
```

with explicit RuntimeIdentity input.

Applications are expected to consume configured API instances provided by:

```text
mxm-runtime
```

rather than constructing production secret infrastructure directly.
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

