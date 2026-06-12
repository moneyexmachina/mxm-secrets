"""Tests for principal resolution."""

import pytest

from mxm.secrets.models import Principal
from mxm.secrets.resolution import principal_from_runtime_identity
from mxm.types.runtime_identity import (
    RuntimeIdentity,
)


def make_runtime_identity(
    *,
    machine: str = "bridge",
    environment: str = "dev",
    substrate: str = "local_process",
    role: str = "marketdata",
    app_id: str = "mxm-secrets-test",
) -> RuntimeIdentity:
    """Create a valid RuntimeIdentity for principal resolution tests."""
    return RuntimeIdentity(
        app=app_id,
        environment=environment,
        machine=machine,
        substrate=substrate,
        role=role,
    )


def test_principal_from_runtime_identity_uses_runtime_role() -> None:
    """Test that RuntimeIdentity.role becomes Principal.name."""
    principal = principal_from_runtime_identity(
        make_runtime_identity(role="marketdata")
    )

    assert principal == Principal(name="marketdata")


def test_principal_from_runtime_identity_maps_different_role() -> None:
    """Test that different valid runtime roles map correctly."""
    principal = principal_from_runtime_identity(make_runtime_identity(role="execution"))

    assert principal == Principal(name="execution")


def test_principal_from_runtime_identity_rejects_invalid_role() -> None:
    """Test that invalid runtime roles are rejected by Principal validation."""
    with pytest.raises(ValueError, match="name must match pattern"):
        principal_from_runtime_identity(make_runtime_identity(role="market-data"))
