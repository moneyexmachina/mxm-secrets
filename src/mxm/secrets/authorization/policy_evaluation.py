"""Secret policy evaluation for mxm-secrets.

This module contains stateless authorization logic for evaluating whether a
principal may access a configured secret reference.

It does not resolve secret names, resolve stores, retrieve secret values, or
construct principals. It only applies the policy referenced by a SecretRef to a
Principal using a SecretPolicyRegistry.
"""

from __future__ import annotations

from mxm.secrets.models import Principal, SecretRef
from mxm.secrets.registries import SecretPolicyRegistry


def is_secret_access_allowed(
    *,
    secret_ref: SecretRef,
    principal: Principal,
    policy_registry: SecretPolicyRegistry,
) -> bool:
    """Return whether a principal may access a configured secret reference.

    Args:
        secret_ref: Configured secret reference being requested.
        principal: Principal requesting access.
        policy_registry: Registry containing configured secret policies.

    Returns:
        True if the policy referenced by secret_ref allows the supplied
        principal, otherwise False.

    Raises:
        KeyError: If secret_ref references an unknown policy.
    """
    policy = policy_registry.get(secret_ref.policy)

    return policy.allows(principal)
