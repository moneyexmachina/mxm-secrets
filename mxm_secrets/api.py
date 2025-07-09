"""mxm_secrets.api

This module provides the public API surface for secrets access within the 
Money Ex Machina infrastructure. All MXM packages should retrieve secrets 
exclusively through `get_secret(...)` defined here.

Philosophy:
- Explicit: Secrets must be requested individually
- Scoped: Only secrets needed by the current process are retrieved
- Modular: This interface abstracts over multiple backends (gopass, env, vault, etc.)

This module defines the function `get_secret(key, default)` which:
- Resolves a secret using a prioritized set of backends
- Is the only access point that should be used by MXM packages
- Supports backend extensibility and config-based dispatch (future)

Current behavior:
- Attempts resolution using `gopass` first
- Falls back to environment variables if no match is found
- Returns `default` if all backends fail

Future plans:
- Make backend priority configurable via `mxm-config`
- Add support for Vault, Age, and runtime session backends

Example:
    from mxm_secrets import get_secret

    api_key = get_secret("prod/some-api-key")

Do not use backend modules directly; rely on this interface for all access.
"""

from typing import Optional, Callable
from mxm_secrets.backends import gopass_backend, env_backend


# Static backend priority (to be moved into mxm-config)
_BACKEND_PRIORITY = ["gopass", "env"]


_BACKEND_DISPATCH: dict[str, dict[str, Callable]] = {
    "gopass": {
        "access": gopass_backend.access_secret,
        "check": gopass_backend.is_gopass_available,
    },
    "env": {
        "access": env_backend.access_secret,
        "check": lambda: True,
    },
}


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from the configured backend chain.

    Attempts each backend in order. Skips unavailable backends silently.

    Args:
        key: The secret identifier (e.g., "prod/smtp-password").
        default: Value to return if no backend resolves the secret.

    Returns:
        The resolved secret value, or `default` if not found.

    Raises:
        ValueError: If an unknown backend is listed in _BACKEND_PRIORITY.
    """
    for backend in _BACKEND_PRIORITY:
        if backend not in _BACKEND_DISPATCH:
            raise ValueError(f"Unknown backend: {backend}")

        if not _BACKEND_DISPATCH[backend]["check"]():
            continue

        result = _BACKEND_DISPATCH[backend]["access"](key, None)
        if result is not None:
            return result

    return default


def check_backend_ready() -> bool:
    """
    Return True if at least one usable backend is available.

    Useful for CLI diagnostics or startup assertions.
    """
    for backend in _BACKEND_PRIORITY:
        if backend not in _BACKEND_DISPATCH:
            continue
        if _BACKEND_DISPATCH[backend]["check"]():
            return True
    return False
