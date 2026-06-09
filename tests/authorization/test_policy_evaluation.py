"""Tests for secret policy evaluation."""

import pytest

from mxm.secrets.authorization import is_secret_access_allowed
from mxm.secrets.models import Principal, SecretPolicy, SecretRef
from mxm.secrets.registries import SecretPolicyRegistry


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for policy evaluation tests."""
    return SecretRef(
        name=name,
        store=store,
        path=path,
        policy=policy,
    )


def make_secret_policy(
    *,
    name: str = "marketdata_access",
    allowed_principals: tuple[str, ...] = ("marketdata",),
) -> SecretPolicy:
    """Create a valid SecretPolicy for policy evaluation tests."""
    return SecretPolicy(
        name=name,
        allowed_principals=allowed_principals,
    )


def test_allowed_principal_returns_true() -> None:
    """Test that an allowed principal is granted access."""
    allowed = is_secret_access_allowed(
        secret_ref=make_secret_ref(),
        principal=Principal(name="marketdata"),
        policy_registry=SecretPolicyRegistry([make_secret_policy()]),
    )

    assert allowed is True


def test_unlisted_principal_returns_false() -> None:
    """Test that an unlisted principal is denied access."""
    allowed = is_secret_access_allowed(
        secret_ref=make_secret_ref(),
        principal=Principal(name="execution"),
        policy_registry=SecretPolicyRegistry([make_secret_policy()]),
    )

    assert allowed is False


def test_deny_all_policy_returns_false() -> None:
    """Test that a policy with no allowed principals denies access."""
    allowed = is_secret_access_allowed(
        secret_ref=make_secret_ref(policy="deny_all"),
        principal=Principal(name="marketdata"),
        policy_registry=SecretPolicyRegistry(
            [make_secret_policy(name="deny_all", allowed_principals=())]
        ),
    )

    assert allowed is False


def test_unknown_policy_raises_key_error() -> None:
    """Test that an unknown policy reference raises KeyError."""
    with pytest.raises(KeyError, match="Unknown secret policy: missing_policy"):
        is_secret_access_allowed(
            secret_ref=make_secret_ref(policy="missing_policy"),
            principal=Principal(name="marketdata"),
            policy_registry=SecretPolicyRegistry([]),
        )
