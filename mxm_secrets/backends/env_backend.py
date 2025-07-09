"""mxm_secrets.backends.env_backend

Backend for resolving secrets from environment variables.

This is the highest-priority fallback backend, used primarily in:
- Local development (for quick testing)
- CI/CD pipelines where secrets are injected via ENV
- Runtime overrides

Secret keys are transformed into uppercase, underscore-safe environment variable names.

Example:
    Key:    "prod/email-password"
    Looks for: PROD_EMAIL_PASSWORD in os.environ

This module defines a single public function: `access_secret(key, default)`.

Use via the public API:
    from mxm_secrets import get_secret
"""

import os
from typing import Optional


def access_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Attempt to resolve a secret from environment variables.

    The logical secret key is converted to uppercase and all dashes and slashes are
    replaced with underscores. For example, "prod/email-password" becomes "PROD_EMAIL_PASSWORD".

    Args:
        key: Logical secret key (e.g. "prod/email-password").
        default: Fallback value to return if the environment variable is not set.

    Returns:
        The resolved secret value, or `default` if not found in the environment.
    """
    env_key = key.upper().replace("-", "_").replace("/", "_")
    return os.environ.get(env_key, default)
