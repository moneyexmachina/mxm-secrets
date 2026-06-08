"""Configured secret reference models for mxm-secrets.

This module defines the internal representation of a configured secret
reference.

Application code does not construct SecretRef objects directly. Applications
request secrets by name through the public API. mxm-secrets then resolves that
name through a secret reference registry to obtain a SecretRef containing the
store, storage path, and policy needed for authorization-aware resolution.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecretRef:
    """Configured reference to a secret.

    A SecretRef is the internal, resolved representation of a secret reference.
    It is loaded from a registry, typically supplied by mxm-config-store, and
    used by mxm-secrets to authorize and resolve a secret request.

    Attributes:
        name: Logical secret name used as the registry lookup key.
        store: Logical store name identifying the configured secret store.
        path: Storage path inside the selected store. This may be opaque or
            otherwise private to the configured registry and backing store.
        policy: Policy name identifying the authorization policy that governs
            access to this secret.
    """

    name: str
    store: str
    path: str
    policy: str

    def __post_init__(self) -> None:
        """Validate the configured secret reference.

        Raises:
            ValueError: If any field is empty, whitespace-only, or contains
                leading or trailing whitespace.
        """
        _validate_non_empty_clean("name", self.name)
        _validate_non_empty_clean("store", self.store)
        _validate_non_empty_clean("path", self.path)
        _validate_non_empty_clean("policy", self.policy)

    @property
    def qualified_name(self) -> str:
        """Return the stable qualified name for diagnostics.

        Returns:
            A string combining store and name without exposing the storage path.
        """
        return f"{self.store}:{self.name}"


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
