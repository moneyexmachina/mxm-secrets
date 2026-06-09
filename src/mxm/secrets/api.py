"""Public API boundary for mxm-secrets.

This module defines SecretsApi, the public service boundary for configured
secret access inside the Money Ex Machina ecosystem.

SecretsApi owns the configured registries needed for authorization-aware secret
resolution, but it does not own secret values. It resolves public secret names,
derives principals from supplied RuntimeIdentity objects, evaluates configured
policies, resolves authorized backend locations, and retrieves secret values
through the supported backend.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.authorization import (
    is_secret_access_allowed,
)
from mxm.secrets.backends import gopass_backend
from mxm.secrets.config_data import SecretsConfigData
from mxm.secrets.config_data.require import require_mapping
from mxm.secrets.registries import (
    SecretPolicyRegistry,
    SecretRefRegistry,
    SecretStoreRegistry,
)
from mxm.secrets.resolution import (
    principal_from_runtime_identity,
    resolve_secret_location,
    retrieve_resolved_secret,
)
from mxm.types.runtime_identity import RuntimeIdentity


@dataclass(frozen=True, slots=True)
class SecretsApi:
    """Configured public API for authorization-aware secret retrieval.

    SecretsApi is constructed from registries supplied by the caller, usually by
    mxm-runtime after loading configuration through mxm-config.

    The API is intentionally explicit: it does not discover configuration, load
    mxm-config, or infer runtime identity. Those responsibilities belong to the
    runtime materialisation layer.

    Attributes:
        secret_ref_registry: Registry mapping public secret names to configured
            secret references.
        secret_store_registry: Registry mapping logical store names to
            configured secret stores.
        secret_policy_registry: Registry mapping policy names to configured
            secret policies.
    """

    secret_ref_registry: SecretRefRegistry
    secret_store_registry: SecretStoreRegistry
    secret_policy_registry: SecretPolicyRegistry

    @classmethod
    def from_config_data(
        cls,
        config: SecretsConfigData,
    ) -> SecretsApi:
        """Construct a configured SecretsApi from plain config data.

        Expected config shape:

        ```yaml
        stores:
          ...

        refs:
          ...

        policies:
          ...
        ```

        Args:
            config: Resolved secrets configuration data.

        Returns:
            Configured SecretsApi.

        Raises:
            TypeError: If the config structure is invalid.
            ValueError: If any configured model fails validation.
        """
        stores_config = require_mapping(
            value=config.get("stores"),
            description="Secrets config section 'stores'",
        )

        refs_config = require_mapping(
            value=config.get("refs"),
            description="Secrets config section 'refs'",
        )

        policies_config = require_mapping(
            value=config.get("policies"),
            description="Secrets config section 'policies'",
        )

        return cls(
            secret_ref_registry=SecretRefRegistry.from_config_data(
                refs_config,
            ),
            secret_store_registry=SecretStoreRegistry.from_config_data(
                stores_config,
            ),
            secret_policy_registry=SecretPolicyRegistry.from_config_data(
                policies_config,
            ),
        )

    def get_secret(
        self,
        secret_name: str,
        *,
        identity: RuntimeIdentity,
        default: str | None = None,
    ) -> str | None:
        """Retrieve a secret by public secret name.

        The retrieval flow is:

        ```text
        secret_name
            ↓
        SecretRefRegistry
            ↓
        RuntimeIdentity → Principal
            ↓
        policy evaluation
            ↓
        SecretStoreRegistry
            ↓
        backend location
            ↓
        gopass retrieval
        ```

        Args:
            secret_name: Public secret name requested by application code.
            identity: Runtime identity supplied by the caller.
            default: Value to return if the resolved backend cannot retrieve the
                secret.

        Returns:
            The resolved secret value, or default if the backend is unavailable
            or cannot resolve the configured backend path.

        Raises:
            KeyError: If secret_name, the referenced store, or the referenced
                policy is not registered.
            PermissionError: If the derived principal is not authorized to
                access the requested secret.
            ValueError: If the resolved location references an unsupported
                backend or if identity.role cannot form a valid Principal.
        """
        secret_ref = self.secret_ref_registry.get(secret_name)
        principal = principal_from_runtime_identity(identity)

        if not is_secret_access_allowed(
            secret_ref=secret_ref,
            principal=principal,
            policy_registry=self.secret_policy_registry,
        ):
            raise PermissionError(
                "Secret access denied: "
                f"{secret_ref.qualified_name} for principal {principal.name}"
            )

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
