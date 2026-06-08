"""Secret reference registry for mxm-secrets.

This module defines the registry used to resolve public secret names into
configured SecretRef objects.

Application code supplies a secret name to the public API. The registry maps
that name to the configured store, storage path, and policy required by the
resolution layer.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from mxm.secrets.models import SecretRef


class SecretRefRegistry:
    """Registry of configured secret references.

    The registry maps public secret names to configured SecretRef objects. It is
    intentionally small and read-only after construction.

    In production usage, registry entries are expected to be supplied from
    mxm-config-store. In tests and local development, they can be constructed
    directly in memory.

    Args:
        refs: Iterable of configured secret references.

    Raises:
        ValueError: If duplicate secret names are supplied.
    """

    def __init__(self, refs: Iterable[SecretRef]) -> None:
        """Create a secret reference registry.

        Args:
            refs: Configured secret references to register.

        Raises:
            ValueError: If two or more references use the same name.
        """
        registry: dict[str, SecretRef] = {}

        for ref in refs:
            if ref.name in registry:
                raise ValueError(f"Duplicate secret reference name: {ref.name}")
            registry[ref.name] = ref

        self._refs: Mapping[str, SecretRef] = MappingProxyType(registry)

    def get(self, secret_name: str) -> SecretRef:
        """Return the configured SecretRef for a secret name.

        Args:
            secret_name: Public secret name supplied by application code.

        Returns:
            The configured SecretRef associated with the supplied name.

        Raises:
            KeyError: If secret_name is not registered.
        """
        try:
            return self._refs[secret_name]
        except KeyError as exc:
            raise KeyError(f"Unknown secret name: {secret_name}") from exc

    def contains(self, secret_name: str) -> bool:
        """Return whether a secret name is registered.

        Args:
            secret_name: Public secret name to check.

        Returns:
            True if the name exists in the registry, otherwise False.
        """
        return secret_name in self._refs

    def names(self) -> tuple[str, ...]:
        """Return all registered secret names.

        Returns:
            Registered secret names sorted lexicographically.
        """
        return tuple(sorted(self._refs))
