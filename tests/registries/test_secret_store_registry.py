"""Tests for the secret store registry."""

import pytest

from mxm.secrets.models import SecretStore
from mxm.secrets.registries import SecretStoreRegistry
from mxm.types import JSONValue


def make_secret_store(
    *,
    name: str = "red",
    backend: str = "gopass",
    root: str = "mxm/red",
) -> SecretStore:
    """Create a valid SecretStore for registry tests.

    Args:
        name: Logical store name.
        backend: Backend name used by the store.
        root: Backend-specific store root.

    Returns:
        A valid SecretStore instance.
    """
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def test_registry_returns_registered_secret_store() -> None:
    """Test that a registered store name resolves to its SecretStore."""
    store = make_secret_store()
    registry = SecretStoreRegistry([store])

    assert registry.get("red") == store


def test_registry_contains_registered_store_name() -> None:
    """Test that contains returns True for a registered store name."""
    registry = SecretStoreRegistry([make_secret_store()])

    assert registry.contains("red") is True


def test_registry_does_not_contain_unknown_store_name() -> None:
    """Test that contains returns False for an unknown store name."""
    registry = SecretStoreRegistry([make_secret_store()])

    assert registry.contains("unknown_store") is False


def test_registry_returns_sorted_names() -> None:
    """Test that names returns registered store names in sorted order."""
    store_b = make_secret_store(name="yellow", root="mxm/yellow")
    store_a = make_secret_store(name="green", root="mxm/green")
    registry = SecretStoreRegistry([store_b, store_a])

    assert registry.names() == ("green", "yellow")


def test_registry_rejects_duplicate_store_names() -> None:
    """Test that duplicate store names are rejected during construction."""
    store_a = make_secret_store(
        name="red",
        backend="gopass",
        root="mxm/red",
    )
    store_b = make_secret_store(
        name="red",
        backend="gopass",
        root="mxm/red-alternate",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate secret store name: red",
    ):
        SecretStoreRegistry([store_a, store_b])


def test_registry_raises_for_unknown_store_name() -> None:
    """Test that get raises KeyError for an unknown store name."""
    registry = SecretStoreRegistry([make_secret_store()])

    with pytest.raises(KeyError, match="Unknown secret store: unknown_store"):
        registry.get("unknown_store")


def test_registry_is_not_affected_by_source_list_mutation() -> None:
    """Test that mutating the source list does not change the registry."""
    stores = [make_secret_store(name="red", root="mxm/red")]
    registry = SecretStoreRegistry(stores)

    stores.append(make_secret_store(name="yellow", root="mxm/yellow"))

    assert registry.contains("red") is True
    assert registry.contains("yellow") is False
    assert registry.names() == ("red",)


def test_from_config_data_creates_registry() -> None:
    """from_config_data should construct a registry from store config data."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
            "root": "mxm/red",
        },
    }

    registry = SecretStoreRegistry.from_config_data(config)

    assert registry.contains("red")
    assert registry.get("red") == SecretStore(
        name="red",
        backend="gopass",
        root="mxm/red",
    )


def test_from_config_data_rejects_invalid_config() -> None:
    """from_config_data should propagate config-data validation errors."""
    config: dict[str, JSONValue] = {
        "red": "not-a-mapping",
    }

    with pytest.raises(TypeError, match="Secret store config"):
        SecretStoreRegistry.from_config_data(config)
