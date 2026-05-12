# mxm-secrets
![Version](https://img.shields.io/github/v/release/moneyexmachina/mxm-secrets)
![License](https://img.shields.io/github/license/moneyexmachina/mxm-secrets)
![Python](https://img.shields.io/badge/python-3.13+-blue)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

A typed, minimal, pluggable Python interface for operational secret access within the Money Ex Machina ecosystem.

Built around explicit, scoped secret retrieval using [`gopass`](https://www.gopass.pw), with support for additional backends and deployment environments over time.

## Purpose

`mxm-secrets` provides the canonical secret access layer for MXM packages.

The package exists to separate:

```text
application code
```

from:

```text
secret storage and operational credential management
```

MXM packages should never:

- hardcode secrets,
- preload global credential blobs,
- depend directly on backend implementations,
- or assume a particular secret storage mechanism.

Instead, packages retrieve secrets explicitly:

```python
from mxm.secrets import get_secret

api_key = get_secret("prod/some-api-key")
```

This establishes:

- explicit dependency boundaries,
- process-local secret access,
- backend composability,
- operational portability,
- and testable infrastructure interfaces.

## Philosophy

### Explicit

Secrets must be requested individually by name.

No global credential injection or hidden runtime state.

### Scoped

Each process retrieves only the secrets it requires.

### Composable

Designed for Unix-style workflows, automation pipelines, REPLs, and distributed runtime environments.

### Pluggable

Supports multiple backend implementations behind a stable API surface.

### Minimal

Small dependency surface, strict typing, and reproducible operational behavior.

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

### Python API

```python
from mxm.secrets import get_secret

api_key = get_secret("mxm/dev/api-key")
smtp_password = get_secret("prod/smtp-password", default="changeme")
```

### CLI Usage

Retrieve a secret:

```bash
python -m mxm.secrets get mxm/dev/api-key
```

With fallback value:

```bash
python -m mxm.secrets get mxm/dev/api-key --default "changeme"
```

Verbose mode:

```bash
python -m mxm.secrets get mxm/dev/api-key --verbose
```

## Secret Resolution Logic

When:

```python
get_secret("mxm/dev/api-key")
```

is called, the package attempts resolution using configured backends in priority order.

Current default order:

1. `gopass`
2. environment variables

Example:

```text
mxm/dev/api-key
```

maps to:

```bash
gopass show mxm/dev/api-key
```

and environment fallback:

```text
MXM_DEV_API_KEY
```

If no backend resolves the secret:

- the provided `default` value is returned,
- otherwise `None`.

## Secret Store Layout

Typical `gopass` structure:

```text
mxm/
├── prod/
│   └── email-password
├── dev/
│   └── test-api-key
├── runtime/
└── bootstrap/
```

Each subtree may use separate `.gpg-id` files for scoped access control.

Example:

```bash
gopass insert mxm/dev/test-api-key
```

---

## Available Backends

| Backend       | Status      | Description                              |
|----------------|-------------|------------------------------------------|
| `gopass`       | Stable      | Local encrypted secret storage via GPG  |
| Environment    | Stable      | Environment variable fallback backend    |
| `age`          | Planned     | File-based encrypted secret backend      |
| Vault          | Planned     | Centralized secret infrastructure        |

## Configuration

Current backend priority is statically defined inside the package.

Future versions will support configuration through:

```text
mxm-config
```

Planned future capabilities:

- configurable backend ordering,
- runtime session backends,
- Vault integration,
- Age integration,
- deployment-specific backend chains.

## Security Notes

`mxm-secrets`:

- does not cache secrets,
- does not preload credentials,
- does not globally export secrets,
- does not persist runtime secret state.

Secrets remain external to MXM repositories and operational codebases.

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

- backend dispatch,
- gopass integration behavior,
- environment fallback logic,
- CLI functionality,
- typing and packaging integration.

Tests are executed using:

```bash
pytest
```

## License

MIT License. See [LICENSE](LICENSE).

## Links

- [Money Ex Machina](https://moneyexmachina.com)
- [gopass](https://www.gopass.pw)
- [Keep a Changelog](https://keepachangelog.com)
- [Semantic Versioning](https://semver.org)
