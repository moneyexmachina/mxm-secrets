"""Configured secret store models for mxm-secrets.

This module defines the internal representation of a configured secret store.

A SecretStore describes how a logical store name maps to a backend and a root
location inside that backend. It does not retrieve secrets directly. Retrieval
belongs to the backend and resolution layers.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.validators import (
    validate_identifier,
    validate_non_empty_clean,
)


@dataclass(frozen=True, slots=True)
class SecretStore:
    """Configured secret store.

    A SecretStore represents a logical authority from which secrets may be
    resolved. It maps a stable store name to a backend implementation and a
    backend-specific root path.

    Attributes:
        name: Logical store name, for example "green", "yellow", "red", or
            "black".
        backend: Backend name used to retrieve secrets from this store, for
            example "gopass".
        root: Root path or namespace for this store inside the selected backend.
    """

    name: str
    backend: str
    root: str

    def __post_init__(self) -> None:
        """Validate the configured secret store.

        Raises:
            ValueError: If any field is invalid.
        """
        validate_identifier("name", self.name)
        validate_identifier("backend", self.backend)
        validate_non_empty_clean("root", self.root)

    def resolve_path(self, secret_path: str) -> str:
        """Resolve a store-relative secret path into a backend path.

        Args:
            secret_path: Path of the secret relative to this store.

        Returns:
            Backend-specific path formed by joining the store root and the
            supplied secret path.

        Raises:
            ValueError: If secret_path is empty, whitespace-only, contains
                leading or trailing whitespace, or is absolute.
        """
        validate_non_empty_clean("secret_path", secret_path)

        if secret_path.startswith("/"):
            raise ValueError("secret_path must be relative")

        return f"{self.root.rstrip('/')}/{secret_path.lstrip('/')}"
