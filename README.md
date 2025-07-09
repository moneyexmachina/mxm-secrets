# mxm-secrets

A minimal, pluggable Python interface to encrypted secrets — built for the [Money Ex Machina](https://moneyexmachina.com) stack, powered by [`gopass`](https://www.gopass.pw).

---

## Philosophy

* **Explicit**: Secrets must be requested by name (`get_secret()`), not preloaded or injected globally.
* **Scoped**: Each runtime process loads only the secrets it needs.
* **Composable**: Works cleanly in Unix-style environments, CLI scripts, and REPL workflows.
* **Pluggable**: Supports `gopass` and environment variable backends today; Vault and Age are future-compatible.
* **Minimal**: No third-party dependencies. Pure Python interface. Fully testable.

---

## Installation

Install from source:

```bash
git clone https://github.com/moneyexmachina/mxm-secrets.git
cd mxm-secrets
poetry install
```

Or add to your project:

```bash
poetry add git+https://github.com/moneyexmachina/mxm-secrets.git
```

---

## Usage

Use in your Python code:

```python
from mxm_secrets import get_secret

api_key = get_secret("mxm/dev/api-key", default="changeme")
```

Or via the CLI:

```bash
poetry run python -m mxm_secrets get mxm/dev/api-key
```

---

### Secret Resolution Logic

When you call `get_secret("mxm/dev/api-key")`, the system attempts:

1. `gopass show mxm/dev/api-key`
2. `os.environ.get("MXM_DEV_API_KEY")`.
3. If not found, return `None` or the `default` value if provided.

---

## Secret Store Layout

Secrets are organized in a [gopass mount](https://www.gopass.pw/docs/features/mounts/) called `mxm`, separated by purpose or environment:

```
mxm/
├── prod/
│   └── email-password
├── dev/
│   └── test-api-key
├── runtime/
├── bootstrap/
```

Each subfolder can have its own `.gpg-id` file, allowing access control per environment:

* `dev/`: accessible to `mxm@my_dev_box`
* `prod/`: encrypted to `mxm@my_prod_box`
* `runtime/`, `bootstrap/`: optionally multi-user

Write secrets like this:

```bash
gopass insert mxm/dev/test-api-key
```

---

## Configuration

No configuration is required beyond setting up `gopass`:

* Install and initialize `gopass`
* Ensure your GPG key is trusted and unlocked
* Clone or mount the correct secrets store (e.g. `~/.mxm-secrets-store`)
* Set `.gpg-id` files appropriately per environment

---

## Available Backends

| Backend     | Status                 | Description                                  |
| ----------- | ---------------------- | -------------------------------------------- |
| `gopass`    | ✅ Stable               | Primary backend using local GPG encryption   |
| Environment | ✅ Supported (fallback) | Uses uppercased env vars                     |
| `age`       | 🕸️ Planned            | For lightweight, file-based secret sharing   |
| Vault       | 🕸️ Future-compatible  | For centralized secure secret infrastructure |

---

## CLI Commands

### Get a secret

```bash
poetry run python -m mxm_secrets get mxm/dev/api-key
```

With fallback:

```bash
poetry run python -m mxm_secrets get mxm/dev/api-key --default "changeme"
```

Verbose mode (prints gopass errors):

```bash
poetry run python -m mxm_secrets get mxm/dev/api-key --verbose
```

---

## Tests

Run the full test suite:

```bash
poetry run pytest
```

Includes tests for:

* API dispatch and fallback logic
* Backend integration
* CLI interface (via `click.testing.CliRunner`)

---

## Security Notes

This package does not store, cache, or globally export any secrets. Secrets are retrieved on demand, scoped to the current process.

---

## License

MIT © [Money Ex Machina](https://moneyexmachina.com)

---

## Links

* [gopass documentation](https://www.gopass.pw)
* [GPG best practices](https://riseup.net/en/security/message-security/openpgp/best-practices)
