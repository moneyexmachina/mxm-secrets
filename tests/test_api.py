"""Tests for the public mxm-secrets API."""

import pytest

from mxm.secrets.api import SecretsApi
from mxm.secrets.models import SecretRef, SecretStore
from mxm.secrets.registries import SecretRefRegistry, SecretStoreRegistry


def make_secret_ref(
    *,
    name: str = "test_api_key",
    store: str = "red",
    path: str = "opaque/test_api_key",
    policy: str = "test_policy",
) -> SecretRef:
    """Create a valid SecretRef for API tests."""
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
    """Create a valid SecretStore for API tests."""
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def make_secrets_api(
    *,
    secret_ref: SecretRef | None = None,
    secret_store: SecretStore | None = None,
) -> SecretsApi:
    """Create a SecretsApi with in-memory test registries."""
    return SecretsApi(
        secret_ref_registry=SecretRefRegistry(
            [secret_ref if secret_ref is not None else make_secret_ref()]
        ),
        secret_store_registry=SecretStoreRegistry(
            [secret_store if secret_store is not None else make_secret_store()]
        ),
    )


def test_get_secret_retrieves_configured_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that SecretsApi resolves registries and retrieves via gopass."""
    api = make_secrets_api()
    observed_key = ""
    observed_default: str | None = None

    def mock_is_gopass_available() -> bool:
        return True

    def mock_access_secret(key: str, default: str | None = None) -> str:
        nonlocal observed_key
        nonlocal observed_default

        observed_key = key
        observed_default = default
        return "secret_value"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    result = api.get_secret("test_api_key", default="fallback")

    assert result == "secret_value"
    assert observed_key == "mxm/red/opaque/test_api_key"
    assert observed_default == "fallback"


def test_get_secret_returns_default_when_gopass_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that SecretsApi returns default when gopass is unavailable."""
    api = make_secrets_api()
    access_called = False

    def mock_is_gopass_available() -> bool:
        return False

    def mock_access_secret(key: str, default: str | None = None) -> str | None:
        nonlocal access_called
        _ = key
        _ = default

        access_called = True
        return "should_not_be_used"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    result = api.get_secret("test_api_key", default="fallback")

    assert result == "fallback"
    assert access_called is False


def test_get_secret_raises_for_unknown_secret_name() -> None:
    """Test that unknown secret names fail at the API boundary."""
    api = make_secrets_api()

    with pytest.raises(KeyError, match="Unknown secret name: missing_secret"):
        api.get_secret("missing_secret")


def test_get_secret_raises_for_unknown_store_name() -> None:
    """Test that SecretRefs referencing unknown stores fail at the API boundary."""
    api = make_secrets_api(secret_ref=make_secret_ref(store="missing_store"))

    with pytest.raises(KeyError, match="Unknown secret store: missing_store"):
        api.get_secret("test_api_key")


def test_get_secret_raises_for_unsupported_backend() -> None:
    """Test that non-gopass backends are rejected in the interim API."""
    api = make_secrets_api(secret_store=make_secret_store(backend="vault"))

    with pytest.raises(ValueError, match="Unsupported secret backend: vault"):
        api.get_secret("test_api_key")


def test_get_secret_currently_does_not_enforce_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Document that policy authorization is not yet enforced."""
    api = make_secrets_api(secret_ref=make_secret_ref(policy="deny_all"))

    def mock_is_gopass_available() -> bool:
        return True

    def mock_access_secret(key: str, default: str | None = None) -> str:
        _ = key
        _ = default
        return "secret_value"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    assert api.get_secret("test_api_key") == "secret_value"
