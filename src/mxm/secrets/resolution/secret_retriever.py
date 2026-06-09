"""Resolved secret retrieval for mxm-secrets.

This module retrieves secret values from backend implementations after a secret
request has already been resolved to a ResolvedSecretLocation.

It does not perform secret-name lookup, store resolution, principal derivation,
policy evaluation, or authorization. Callers must only retrieve resolved
locations after authorization has succeeded.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from mxm.secrets.backends import gopass_backend
from mxm.secrets.models import ResolvedSecretLocation

AccessFn = Callable[[str, str | None], str | None]
CheckFn = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class SecretBackend:
    """Backend adapter used by resolved secret retrieval.

    Attributes:
        access: Function used to retrieve a secret value from the backend.
        check: Function used to determine whether the backend is available.
    """

    access: AccessFn
    check: CheckFn


def retrieve_resolved_secret(
    location: ResolvedSecretLocation,
    default: str | None = None,
) -> str | None:
    """Retrieve a secret value from a resolved backend location.

    Args:
        location: Backend-specific location produced by secret resolution.
        default: Value to return if the backend is unavailable or does not
            resolve the secret.

    Returns:
        The resolved secret value, or default if the configured backend is
        unavailable or returns no value.

    Raises:
        ValueError: If the resolved location references an unknown backend.
    """
    if location.backend != "gopass":
        raise ValueError(f"Unsupported secret backend: {location.backend}")

    if not gopass_backend.is_gopass_available():
        return default

    return gopass_backend.access_secret(location.backend_path, default)
