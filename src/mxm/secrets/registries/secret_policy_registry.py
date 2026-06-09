"""Secret policy registry for mxm-secrets.

This module defines the registry used to resolve configured policy names into
SecretPolicy objects.

SecretRef objects refer to policies by logical name. The policy registry maps
those names to configured authorization policies used by the authorization
layer.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from mxm.secrets.config_data import (
    SecretPoliciesConfigData,
    load_secret_policies_from_config_data,
)
from mxm.secrets.models import SecretPolicy


class SecretPolicyRegistry:
    """Registry of configured secret policies.

    The registry maps logical policy names to configured SecretPolicy objects.
    It is intentionally small and read-only after construction.

    In production usage, registry entries are expected to be supplied from
    mxm-config-store. In tests and local development, they can be constructed
    directly in memory.

    Args:
        policies: Iterable of configured secret policies.

    Raises:
        ValueError: If duplicate policy names are supplied.
    """

    def __init__(self, policies: Iterable[SecretPolicy]) -> None:
        """Create a secret policy registry.

        Args:
            policies: Configured secret policies to register.

        Raises:
            ValueError: If two or more policies use the same name.
        """
        registry: dict[str, SecretPolicy] = {}

        for policy in policies:
            if policy.name in registry:
                raise ValueError(f"Duplicate secret policy name: {policy.name}")
            registry[policy.name] = policy

        self._policies: Mapping[str, SecretPolicy] = MappingProxyType(registry)

    @classmethod
    def from_config_data(
        cls,
        config: SecretPoliciesConfigData,
    ) -> SecretPolicyRegistry:
        """Create a registry from plain secret-policy config data.

        Args:
            config: Mapping from logical policy name to policy configuration.

        Returns:
            Secret policy registry containing policies constructed from the
            supplied config data.

        Raises:
            TypeError: If the config data has an invalid structural shape.
            ValueError: If any configured policy fails validation, or if
                duplicate policy names are supplied.
        """
        return cls(load_secret_policies_from_config_data(config))

    def get(self, policy_name: str) -> SecretPolicy:
        """Return the configured SecretPolicy for a policy name.

        Args:
            policy_name: Logical policy name referenced by a SecretRef.

        Returns:
            The configured SecretPolicy associated with the supplied name.

        Raises:
            KeyError: If policy_name is not registered.
        """
        try:
            return self._policies[policy_name]
        except KeyError as exc:
            raise KeyError(f"Unknown secret policy: {policy_name}") from exc

    def contains(self, policy_name: str) -> bool:
        """Return whether a policy name is registered.

        Args:
            policy_name: Logical policy name to check.

        Returns:
            True if the name exists in the registry, otherwise False.
        """
        return policy_name in self._policies

    def names(self) -> tuple[str, ...]:
        """Return all registered policy names.

        Returns:
            Registered policy names sorted lexicographically.
        """
        return tuple(sorted(self._policies))
