"""Public API boundary for mxm-secrets.

This module defines SecretsApi, the public service boundary for configured
secret access inside the Money Ex Machina ecosystem.

SecretsApi owns the configured secret registries needed for resolution, but it
does not own secret values. It resolves public secret names into configured
secret references, resolves their stores, and retrieves the resulting backend
location through the supported secret backend.

Current Session 47C interim behavior:
- callers request secrets by public secret name;
- SecretsApi resolves names through a SecretRefRegistry;
- SecretsApi resolves stores through a SecretStoreRegistry;
- SecretsApi retrieves the resolved backend location through gopass.

Authorization, principal derivation, and RuntimeIdentity integration are still
to be added in Session 47C. The current implementation deliberately keeps a
TODO at the point where authorization must happen.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.backends import gopass_backend
from mxm.secrets.registries import SecretRefRegistry, SecretStoreRegistry
from mxm.secrets.resolution import resolve_secret_location, retrieve_resolved_secret


@dataclass(frozen=True, slots=True)
class SecretsApi:
    """Configured public API for secret retrieval.

    SecretsApi is the object application code should use to request secrets. It
    is constructed from registries supplied by the caller, usually by
    mxm-runtime after loading configuration through mxm-config.

    The API is intentionally explicit: it does not discover configuration, load
    mxm-config, or infer runtime identity. Those responsibilities belong to the
    runtime materialisation layer.

    Attributes:
        secret_ref_registry: Registry mapping public secret names to configured
            secret references.
        secret_store_registry: Registry mapping logical store names to
            configured secret stores.
    """

    secret_ref_registry: SecretRefRegistry
    secret_store_registry: SecretStoreRegistry

    def get_secret(
        self,
        secret_name: str,
        *,
        default: str | None = None,
    ) -> str | None:
        """Retrieve a secret by public secret name.

        This interim implementation performs configured name resolution, store
        resolution, backend path resolution, and gopass retrieval.

        Args:
            secret_name: Public secret name requested by application code.
            default: Value to return if the resolved backend cannot retrieve the
                secret.

        Returns:
            The resolved secret value, or default if the backend is unavailable
            or cannot resolve the configured backend path.

        Raises:
            KeyError: If secret_name is not registered or references an
                unregistered store.
            ValueError: If the resolved location references an unsupported
                backend.

        Todo:
            Add RuntimeIdentity input, principal derivation, and policy
            evaluation before resolving the backend location or retrieving the
            secret value.
        """
        # TODO: Add RuntimeIdentity input, derive the principal, and evaluate
        # the configured policy for this secret before resolving the backend
        # location.
        location = resolve_secret_location(
            secret_name=secret_name,
            secret_ref_registry=self.secret_ref_registry,
            secret_store_registry=self.secret_store_registry,
        )

        return retrieve_resolved_secret(
            location=location,
            default=default,
        )

    def check_ready(self) -> bool:
        """Return whether the currently supported backend is available.

        Returns:
            True if gopass is installed and its store is accessible, otherwise
            False.
        """
        return gopass_backend.is_gopass_available()
