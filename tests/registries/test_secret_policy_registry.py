"""Tests for the secret policy registry."""

import pytest

from mxm.secrets.models import SecretPolicy
from mxm.secrets.registries import SecretPolicyRegistry
from mxm.types import JSONValue


def make_secret_policy(
    *,
    name: str = "marketdata_access",
    allowed_principals: tuple[str, ...] = ("marketdata",),
) -> SecretPolicy:
    """Create a valid SecretPolicy for registry tests.

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


def test_registry_returns_registered_secret_policy() -> None:
    """Test that a registered policy name resolves to its SecretPolicy."""
    policy = make_secret_policy()
    registry = SecretPolicyRegistry([policy])

    assert registry.get("marketdata_access") == policy


def test_registry_contains_registered_policy_name() -> None:
    """Test that contains returns True for a registered policy name."""
    registry = SecretPolicyRegistry([make_secret_policy()])

    assert registry.contains("marketdata_access") is True


def test_registry_does_not_contain_unknown_policy_name() -> None:
    """Test that contains returns False for an unknown policy name."""
    registry = SecretPolicyRegistry([make_secret_policy()])

    assert registry.contains("unknown_policy") is False


def test_registry_returns_sorted_names() -> None:
    """Test that names returns registered policy names in sorted order."""
    policy_b = make_secret_policy(name="z_policy")
    policy_a = make_secret_policy(name="a_policy")
    registry = SecretPolicyRegistry([policy_b, policy_a])

    assert registry.names() == ("a_policy", "z_policy")


def test_registry_rejects_duplicate_policy_names() -> None:
    """Test that duplicate policy names are rejected during construction."""
    policy_a = make_secret_policy(
        name="marketdata_access",
        allowed_principals=("marketdata",),
    )
    policy_b = make_secret_policy(
        name="marketdata_access",
        allowed_principals=("research",),
    )

    with pytest.raises(
        ValueError,
        match="Duplicate secret policy name: marketdata_access",
    ):
        SecretPolicyRegistry([policy_a, policy_b])


def test_registry_raises_for_unknown_policy_name() -> None:
    """Test that get raises KeyError for an unknown policy name."""
    registry = SecretPolicyRegistry([make_secret_policy()])

    with pytest.raises(KeyError, match="Unknown secret policy: unknown_policy"):
        registry.get("unknown_policy")


def test_registry_is_not_affected_by_source_list_mutation() -> None:
    """Test that mutating the source list does not change the registry."""
    policies = [make_secret_policy(name="first_policy")]
    registry = SecretPolicyRegistry(policies)

    policies.append(make_secret_policy(name="second_policy"))

    assert registry.contains("first_policy") is True
    assert registry.contains("second_policy") is False
    assert registry.names() == ("first_policy",)


def test_from_config_data_creates_registry() -> None:
    """from_config_data should construct a registry from policy config data."""
    config: dict[str, JSONValue] = {
        "marketdata_access": {
            "allowed_principals": [
                "marketdata",
                "research",
            ],
        },
    }

    registry = SecretPolicyRegistry.from_config_data(config)

    assert registry.contains("marketdata_access")
    assert registry.get("marketdata_access") == SecretPolicy(
        name="marketdata_access",
        allowed_principals=(
            "marketdata",
            "research",
        ),
    )


def test_from_config_data_rejects_invalid_config() -> None:
    """from_config_data should propagate config-data validation errors."""
    config: dict[str, JSONValue] = {
        "marketdata_access": "not-a-mapping",
    }

    with pytest.raises(TypeError, match="Secret policy config"):
        SecretPolicyRegistry.from_config_data(config)
