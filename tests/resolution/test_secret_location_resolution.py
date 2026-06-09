"""Tests for secret location resolution."""

import pytest

from mxm.secrets.models import ResolvedSecretLocation, SecretRef, SecretStore
from mxm.secrets.registries import SecretRefRegistry, SecretStoreRegistry
from mxm.secrets.resolution import resolve_secret_location


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for resolver tests."""
    return SecretRef(
        name=name,
        store=store,
        path=path,
        policy=policy,
    )


def make_secret_store(
    *,
    name: str = "red",
    backend: str = "gopass",
    root: str = "mxm/red",
) -> SecretStore:
    """Create a valid SecretStore for resolver tests."""
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def test_resolves_registered_secret_name() -> None:
    """Test that a registered secret name resolves to a backend location."""
    secret_ref = make_secret_ref()
    store = make_secret_store()

    location = resolve_secret_location(
        secret_name="databento_api_key",
        secret_ref_registry=SecretRefRegistry([secret_ref]),
        secret_store_registry=SecretStoreRegistry([store]),
    )

    assert isinstance(location, ResolvedSecretLocation)
    assert location.secret_ref == secret_ref
    assert location.store == store
    assert location.backend == "gopass"
    assert location.backend_path == "mxm/red/opaque/path"


def test_unknown_secret_name_raises_key_error() -> None:
    """Test that an unknown secret name fails at secret ref lookup."""
    store = make_secret_store()

    with pytest.raises(KeyError, match="Unknown secret name: missing_secret"):
        resolve_secret_location(
            secret_name="missing_secret",
            secret_ref_registry=SecretRefRegistry([]),
            secret_store_registry=SecretStoreRegistry([store]),
        )


def test_unknown_store_name_raises_key_error() -> None:
    """Test that a SecretRef referencing an unknown store fails."""
    secret_ref = make_secret_ref(store="missing_store")

    with pytest.raises(KeyError, match="Unknown secret store: missing_store"):
        resolve_secret_location(
            secret_name="databento_api_key",
            secret_ref_registry=SecretRefRegistry([secret_ref]),
            secret_store_registry=SecretStoreRegistry([]),
        )


def test_resolver_uses_store_root_for_backend_path() -> None:
    """Test that backend_path is composed from store root and secret path."""
    secret_ref = make_secret_ref(path="vendor/api-key")
    store = make_secret_store(root="mxm/red")

    location = resolve_secret_location(
        secret_name="databento_api_key",
        secret_ref_registry=SecretRefRegistry([secret_ref]),
        secret_store_registry=SecretStoreRegistry([store]),
    )

    assert location.backend_path == "mxm/red/vendor/api-key"


def test_resolver_uses_store_backend() -> None:
    """Test that resolved backend is taken from the configured store."""
    secret_ref = make_secret_ref()
    store = make_secret_store(backend="gopass")

    location = resolve_secret_location(
        secret_name="databento_api_key",
        secret_ref_registry=SecretRefRegistry([secret_ref]),
        secret_store_registry=SecretStoreRegistry([store]),
    )

    assert location.backend == store.backend
