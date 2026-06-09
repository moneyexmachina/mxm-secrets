"""Principal models for mxm-secrets.

This module defines the principal model used by the authorization layer.

A Principal represents the operational actor requesting access to a secret.
Principals are the unit against which secret policies are evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass

from mxm.secrets.validators import validate_identifier


@dataclass(frozen=True, slots=True)
class Principal:
    """Operational actor requesting secret access.

    A Principal represents the resolved operational identity used for policy
    evaluation. It is not the same as RuntimeIdentity. RuntimeIdentity describes
    the runtime context; a Principal is derived from that context and used for
    authorization decisions.

    Examples include "marketdata", "execution", "research", "prefect-worker",
    and "human-admin".

    Attributes:
        name: Stable principal name used in policy evaluation.
    """

    name: str

    def __post_init__(self) -> None:
        """Validate the principal.

        Raises:
            ValueError: If name is not a valid mxm-secrets identifier.
        """
        validate_identifier("name", self.name)
