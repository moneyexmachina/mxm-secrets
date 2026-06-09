"""Resolved secret location model for mxm-secrets.

This module defines the result of resolving a configured SecretRef through a
configured SecretStore.

A ResolvedSecretLocation identifies the backend and backend-specific location
from which a secret value can be retrieved. It does not contain the secret value
itself and does not perform authorization or backend access.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.models.secret_ref import SecretRef
from mxm.secrets.models.secret_store import SecretStore


@dataclass(frozen=True, slots=True)
class ResolvedSecretLocation:
    """Resolved backend location for a configured secret reference.

    A ResolvedSecretLocation is produced after resolving a secret name through a
    SecretRefRegistry and then resolving the referenced store through a
    SecretStoreRegistry.

    Attributes:
        secret_ref: Configured secret reference being resolved.
        store: Configured secret store used for backend resolution.
        backend: Backend name used to retrieve the secret value.
        backend_path: Backend-specific path or identifier for the secret.
    """

    secret_ref: SecretRef
    store: SecretStore
    backend: str
    backend_path: str

    def __post_init__(self) -> None:
        """Validate the resolved secret location.

        Raises:
            ValueError: If backend or backend_path is empty, whitespace-only, or
                contains leading or trailing whitespace.
            ValueError: If backend does not match the resolved store backend.
        """
        _validate_non_empty_clean("backend", self.backend)
        _validate_non_empty_clean("backend_path", self.backend_path)

        if self.backend != self.store.backend:
            raise ValueError("backend must match store backend")

    @property
    def secret_name(self) -> str:
        """Return the logical secret name.

        Returns:
            The logical secret name from the configured SecretRef.
        """
        return self.secret_ref.name

    @property
    def store_name(self) -> str:
        """Return the logical store name.

        Returns:
            The logical store name from the configured SecretStore.
        """
        return self.store.name

    @property
    def diagnostic_name(self) -> str:
        """Return a backend path-free diagnostic name.

        Returns:
            A stable diagnostic name that identifies the secret and store without
            exposing the backend path.
        """
        return f"{self.store.name}:{self.secret_ref.name}"


def _validate_non_empty_clean(field_name: str, value: str) -> None:
    """Validate that a string field is non-empty and whitespace-clean.

    Args:
        field_name: Name of the field being validated.
        value: Field value to validate.

    Raises:
        ValueError: If value is empty, whitespace-only, or has leading or
            trailing whitespace.
    """
    if not value:
        raise ValueError(f"{field_name} must not be empty")

    if value.strip() != value:
        raise ValueError(f"{field_name} must not contain surrounding whitespace")

    if not value.strip():
        raise ValueError(f"{field_name} must not be whitespace-only")
