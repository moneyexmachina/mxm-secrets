# mxm-secrets

![Version](https://img.shields.io/github/v/release/moneyexmachina/mxm-secrets)
![License](https://img.shields.io/github/license/moneyexmachina/mxm-secrets)
![Python](https://img.shields.io/badge/python-3.13+-blue)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Typed, authorization-aware secret resolution for the Money Ex Machina ecosystem.

`mxm-secrets` resolves public secret names into backend secret values using configured secret references, stores, policies, and runtime identity.

The package provides the Resolution layer of the MXM Runtime Context Architecture.

## Purpose

`mxm-secrets` exists to separate:

```text
application code
```

from:

```text
secret storage
authorization
runtime identity
secret resolution
```

Applications should never:

- hardcode secret values,
- depend on gopass paths,
- implement authorization logic,
- or perform secret discovery themselves.

Instead, applications request secrets through a configured API:

```python
secret = api.get_secret(
    secret_name="databento_api_key",
    identity=runtime_identity,
)
```

The package then:

```text
resolves the secret reference
derives the principal
evaluates authorization
resolves the backend location
retrieves the secret value
```

## Architecture

`mxm-secrets` implements the Resolution layer:

```text
RuntimeIdentity
    ↓
Principal
    ↓
SecretPolicy
    ↓
Authorization
    ↓
SecretRef
    ↓
SecretStore
    ↓
ResolvedSecretLocation
    ↓
Backend Retrieval
```

The package accepts plain configuration data and can construct configured
registries and API instances from that data.

Configuration discovery and loading remain the responsibility of
mxm-runtime and mxm-config.


```text
mxm-runtime
```

which constructs configured API instances from configuration data.

## Core Concepts

### RuntimeIdentity

Represents the operational runtime requesting access.

Example:

```text
machine      bridge
environment  dev
role         marketdata
```

Runtime identity is always supplied explicitly.

### Principal

Represents the operational authority requesting a secret.

Examples:

```text
marketdata
execution
research
human_admin
```

Principals are derived from runtime identity.

### SecretRef

Represents a logical secret reference.

Example:

```python
SecretRef(
    name="databento_api_key",
    store="red",
    path="marketdata/databento/api_key",
    policy="marketdata_access",
)
```

Applications depend on secret names rather than storage locations.

### SecretStore

Represents a configured secret authority.

Example:

```python
SecretStore(
    name="red",
    backend="gopass",
    root="mxm/red",
)
```

### SecretPolicy

Represents authorization rules.

Example:

```python
SecretPolicy(
    name="marketdata_access",
    allowed_principals=(
        "marketdata",
        "research",
    ),
)
```

## Resolution Flow

A secret request follows the path:

```text
secret_name
    ↓
SecretRefRegistry
    ↓
RuntimeIdentity
    ↓
Principal
    ↓
SecretPolicyRegistry
    ↓
Policy Evaluation
    ↓
SecretStoreRegistry
    ↓
ResolvedSecretLocation
    ↓
Secret Retrieval
    ↓
secret value
```

Unauthorized requests fail before backend retrieval occurs.

## Installation

Install from PyPI:

```bash
poetry add mxm-secrets
```

Or install from source:

```bash
git clone https://github.com/moneyexmachina/mxm-secrets.git
cd mxm-secrets
poetry install
```

## Usage

### Constructing a SecretsApi

The package is intentionally explicit.

Callers construct registries and provide them to `SecretsApi`.

Example:

```python
api = SecretsApi.from_config_data(
    {
        "stores": {...},
        "refs": {...},
        "policies": {...},
    }
)
```
Advanced callers may construct registries directly, but the preferred
construction path is through configuration data.

## Configuration Shape

The package accepts plain configuration data with the structure:

```yaml
stores:
  red:
    backend: gopass
    root: mxm/red

refs:
  databento_api_key:
    store: red
    path: marketdata/databento/api_key
    policy: marketdata_access

policies:
  marketdata_access:
    allowed_principals:
      - marketdata
      - research
```

This configuration is typically loaded by mxm-runtime from mxm-config
and passed to:

```python
SecretsApi.from_config_data(...)
```

### Retrieving a Secret

```python
secret = api.get_secret(
    secret_name="databento_api_key",
    identity=runtime_identity,
)
```

Authorization is evaluated automatically before secret retrieval.

## Backend Support

Current backend support:

| Backend | Status |
|----------|----------|
| gopass | Stable |

The backend abstraction remains intentionally small.

Future backends may be added if required by MXM deployment architecture.

## Security Model

`mxm-secrets` separates:

```text
storage
```

from:

```text
authorization
```

The existence of a secret in a backend does not imply authorization.

Authorization is evaluated through:

```text
Principal
SecretPolicy
SecretPolicyRegistry
```

before retrieval occurs.

The package:

- does not cache secrets,
- does not preload secret collections,
- does not expose backend paths to applications,
- does not infer runtime identity,
- does not perform configuration discovery.

## Relationship To mxm-runtime

`mxm-secrets` provides semantics.

`mxm-runtime` provides materialisation.

Responsibilities are separated:

```text
mxm-config
    owns configuration data

mxm-secrets
    owns resolution and authorization semantics

mxm-runtime
    owns assembly and RuntimeContext construction
```

Applications are expected to consume configured APIs through:

```python
RuntimeContext
```

rather than constructing production APIs directly.

## Development

Install development dependencies:

```bash
poetry install
```

Run formatting:

```bash
make fmt
```

Run linting:

```bash
make lint
```

Run static typing:

```bash
make type
```

Run tests:

```bash
make test
```

Run full validation:

```bash
make check
```

Run MXM package compliance validation:

```bash
mxm-foundry check .
```

## Testing

The test suite includes coverage for:

- secret references,
- secret stores,
- secret policies,
- principals,
- registries,
- policy evaluation,
- runtime identity mapping,
- secret resolution,
- backend retrieval,
- API orchestration,
- CLI diagnostics.

Tests are executed using:

```bash
pytest
```

## Status

Current release status:

```text
Resolution Layer Complete
Config-Driven Construction Complete
RuntimeContext Integration Pending
```
mxm-secrets now supports construction of configured registries and
SecretsApi instances from plain configuration data.

RuntimeContext materialisation remains the responsibility of
mxm-runtime.

## License

MIT License. See [LICENSE](LICENSE).

## Links

- https://moneyexmachina.com
- https://www.gopass.pw
- https://keepachangelog.com
- https://semver.org
