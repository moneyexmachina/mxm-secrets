"""Secret policy models for mxm-secrets.

This module defines the policy model used by the authorization layer.

A SecretPolicy defines which principals may access secrets governed by the
policy. SecretRef objects refer to policies by name.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.models.principal import Principal
from mxm.secrets.validators import validate_identifier


@dataclass(frozen=True, slots=True)
class SecretPolicy:
    """Configured secret access policy.

    A SecretPolicy represents an authorization rule for one or more configured
    secret references. It answers whether a resolved Principal may access a
    secret governed by this policy.

    Attributes:
        name: Stable policy name used as the registry lookup key.
        allowed_principals: Principal names allowed by this policy.
    """

    name: str
    allowed_principals: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate the configured secret policy.

        Raises:
            ValueError: If name or any allowed principal is not a valid
                mxm-secrets identifier, or if duplicate principals are supplied.
        """
        validate_identifier("name", self.name)

        seen_principals: set[str] = set()
        for principal_name in self.allowed_principals:
            validate_identifier("allowed_principal", principal_name)

            if principal_name in seen_principals:
                raise ValueError(
                    f"Duplicate allowed principal in policy {self.name}: "
                    f"{principal_name}"
                )

            seen_principals.add(principal_name)

    def allows(self, principal: Principal) -> bool:
        """Return whether the policy allows the supplied principal.

        Args:
            principal: Principal requesting access.

        Returns:
            True if the principal is listed in allowed_principals, otherwise
            False.
        """
        return principal.name in self.allowed_principals
