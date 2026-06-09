"""Tests for secret policy models."""

import pytest

from mxm.secrets.models import Principal, SecretPolicy


def make_secret_policy(
    *,
    name: str = "marketdata_access",
    allowed_principals: tuple[str, ...] = ("marketdata",),
) -> SecretPolicy:
    """Create a valid SecretPolicy for model tests.

    Args:
        name: Policy name.
        allowed_principals: Principal names allowed by the policy.

    Returns:
        A valid SecretPolicy instance.
    """
    return SecretPolicy(
        name=name,
        allowed_principals=allowed_principals,
    )


def test_secret_policy_can_be_created() -> None:
    """Test that a valid SecretPolicy can be created."""
    policy = make_secret_policy()

    assert policy.name == "marketdata_access"
    assert policy.allowed_principals == ("marketdata",)


def test_secret_policy_allows_allowed_principal() -> None:
    """Test that allows returns True for an allowed principal."""
    policy = make_secret_policy(allowed_principals=("marketdata", "research"))

    assert policy.allows(Principal(name="marketdata")) is True


def test_secret_policy_rejects_unlisted_principal() -> None:
    """Test that allows returns False for an unlisted principal."""
    policy = make_secret_policy(allowed_principals=("marketdata",))

    assert policy.allows(Principal(name="execution")) is False


def test_secret_policy_allows_empty_allowed_principals() -> None:
    """Test that a policy may intentionally allow no principals."""
    policy = make_secret_policy(
        name="deny_all",
        allowed_principals=(),
    )

    assert policy.allowed_principals == ()
    assert policy.allows(Principal(name="marketdata")) is False


def test_secret_policy_rejects_invalid_name_identifier() -> None:
    """Test that policy name must be a valid identifier."""
    with pytest.raises(ValueError, match="name must match pattern"):
        make_secret_policy(name="marketdata-access")


def test_secret_policy_rejects_invalid_allowed_principal_identifier() -> None:
    """Test that allowed principal names must be valid identifiers."""
    with pytest.raises(ValueError, match="allowed_principal must match pattern"):
        make_secret_policy(allowed_principals=("human-admin",))


def test_secret_policy_rejects_duplicate_allowed_principals() -> None:
    """Test that duplicate allowed principals are rejected."""
    with pytest.raises(
        ValueError,
        match="Duplicate allowed principal in policy marketdata_access: marketdata",
    ):
        make_secret_policy(
            allowed_principals=("marketdata", "marketdata"),
        )
