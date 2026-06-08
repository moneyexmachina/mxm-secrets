"""Secret store registry for mxm-secrets.

This module defines the registry used to resolve logical store names into
configured SecretStore objects.

SecretRef objects refer to stores by logical name. The store registry maps those
names to backend-specific store configuration used by the resolution layer.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from mxm.secrets.models import SecretStore


class SecretStoreRegistry:
    """Registry of configured secret stores.

    The registry maps logical store names to configured SecretStore objects. It
    is intentionally small and read-only after construction.

    In production usage, registry entries are expected to be supplied from
    mxm-config-store. In tests and local development, they can be constructed
    directly in memory.

    Args:
        stores: Iterable of configured secret stores.

    Raises:
        ValueError: If duplicate store names are supplied.
    """

    def __init__(self, stores: Iterable[SecretStore]) -> None:
        """Create a secret store registry.

        Args:
            stores: Configured secret stores to register.

        Raises:
            ValueError: If two or more stores use the same name.
        """
        registry: dict[str, SecretStore] = {}

        for store in stores:
            if store.name in registry:
                raise ValueError(f"Duplicate secret store name: {store.name}")
            registry[store.name] = store

        self._stores: Mapping[str, SecretStore] = MappingProxyType(registry)

    def get(self, store_name: str) -> SecretStore:
        """Return the configured SecretStore for a store name.

        Args:
            store_name: Logical store name referenced by a SecretRef.

        Returns:
            The configured SecretStore associated with the supplied name.

        Raises:
            KeyError: If store_name is not registered.
        """
        try:
            return self._stores[store_name]
        except KeyError as exc:
            raise KeyError(f"Unknown secret store: {store_name}") from exc

    def contains(self, store_name: str) -> bool:
        """Return whether a store name is registered.

        Args:
            store_name: Logical store name to check.

        Returns:
            True if the name exists in the registry, otherwise False.
        """
        return store_name in self._stores

    def names(self) -> tuple[str, ...]:
        """Return all registered store names.

        Returns:
            Registered store names sorted lexicographically.
        """
        return tuple(sorted(self._stores))
