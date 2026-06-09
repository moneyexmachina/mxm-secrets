"""Secret location resolver for mxm-secrets.

This module resolves a public secret name into a backend-specific secret
location by combining the SecretRefRegistry and SecretStoreRegistry.

It performs no authorization and retrieves no secret values.
"""

from __future__ import annotations

from mxm.secrets.models import ResolvedSecretLocation
from mxm.secrets.registries import SecretRefRegistry, SecretStoreRegistry


def resolve_secret_location(
    *,
    secret_name: str,
    secret_ref_registry: SecretRefRegistry,
    secret_store_registry: SecretStoreRegistry,
) -> ResolvedSecretLocation:
    """Resolve a public secret name into a backend-specific secret location.

    Args:
        secret_name: Public secret name supplied by application code.
        secret_ref_registry: Registry mapping secret names to configured
            SecretRef objects.
        secret_store_registry: Registry mapping store names to configured
            SecretStore objects.

    Returns:
        A resolved backend location for the requested secret.

    Raises:
        KeyError: If the secret name or referenced store name is unknown.
        ValueError: If the configured SecretRef and SecretStore are
            inconsistent.
    """
    secret_ref = secret_ref_registry.get(secret_name)
    store = secret_store_registry.get(secret_ref.store)
    backend_path = store.resolve_path(secret_ref.path)

    return ResolvedSecretLocation(
        secret_ref=secret_ref,
        store=store,
        backend=store.backend,
        backend_path=backend_path,
    )
