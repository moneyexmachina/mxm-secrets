"""Principal resolution for mxm-secrets.

This module contains stateless logic for deriving an authorization Principal
from a RuntimeIdentity.

RuntimeIdentity is supplied by the caller. mxm-secrets does not discover runtime
identity itself.
"""

from __future__ import annotations

from mxm.secrets.models import Principal
from mxm.types.runtime_identity import RuntimeIdentity


def principal_from_runtime_identity(identity: RuntimeIdentity) -> Principal:
    """Derive a Principal from a RuntimeIdentity.

    The current Session 47C rule is intentionally minimal: the runtime role is
    used as the principal name. More elaborate mappings can be introduced later
    if the policy model requires them.

    Args:
        identity: Runtime identity supplied by the caller.

    Returns:
        Principal derived from the runtime role.

    Raises:
        ValueError: If the runtime role is not a valid principal identifier.
    """
    return Principal(name=str(identity.role))
