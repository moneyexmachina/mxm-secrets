"""Tests for the secret reference registry."""

import pytest

from mxm.secrets.models import SecretRef
from mxm.secrets.registries import SecretRefRegistry


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for registry tests.

    Args:
        name: Logical secret name.
        store: Logical store name.
        path: Storage path inside the selected store.
        policy: Policy name governing access.

    Returns:
        A valid SecretRef instance.
    """
    return SecretRef(
        name=name,
        store=store,
        path=path,
        policy=policy,
    )


def test_registry_returns_registered_secret_ref() -> None:
    """Test that a registered secret name resolves to its SecretRef."""
    ref = make_secret_ref()
    registry = SecretRefRegistry([ref])

    assert registry.get("databento_api_key") == ref


def test_registry_contains_registered_secret_name() -> None:
    """Test that contains returns True for a registered secret name."""
    registry = SecretRefRegistry([make_secret_ref()])

    assert registry.contains("databento_api_key") is True


def test_registry_does_not_contain_unknown_secret_name() -> None:
    """Test that contains returns False for an unknown secret name."""
    registry = SecretRefRegistry([make_secret_ref()])

    assert registry.contains("unknown_secret") is False


def test_registry_returns_sorted_names() -> None:
    """Test that names returns registered names in sorted order."""
    ref_b = make_secret_ref(name="z_secret")
    ref_a = make_secret_ref(name="a_secret")
    registry = SecretRefRegistry([ref_b, ref_a])

    assert registry.names() == ("a_secret", "z_secret")


def test_registry_rejects_duplicate_secret_names() -> None:
    """Test that duplicate secret names are rejected during construction."""
    ref_a = make_secret_ref(
        name="databento_api_key",
        store="red",
        path="opaque/path/a",
        policy="marketdata_access",
    )
    ref_b = make_secret_ref(
        name="databento_api_key",
        store="yellow",
        path="opaque/path/b",
        policy="alternate_policy",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate secret reference name: databento_api_key",
    ):
        SecretRefRegistry([ref_a, ref_b])


def test_registry_raises_for_unknown_secret_name() -> None:
    """Test that get raises KeyError for an unknown secret name."""
    registry = SecretRefRegistry([make_secret_ref()])

    with pytest.raises(KeyError, match="Unknown secret name: unknown_secret"):
        registry.get("unknown_secret")


def test_registry_is_not_affected_by_source_list_mutation() -> None:
    """Test that mutating the source list does not change the registry."""
    refs = [make_secret_ref(name="first_secret")]
    registry = SecretRefRegistry(refs)

    refs.append(make_secret_ref(name="second_secret"))

    assert registry.contains("first_secret") is True
    assert registry.contains("second_secret") is False
    assert registry.names() == ("first_secret",)
