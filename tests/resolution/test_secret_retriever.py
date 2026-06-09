"""Tests for resolved secret retrieval."""

import pytest

from mxm.secrets.models import ResolvedSecretLocation, SecretRef, SecretStore
from mxm.secrets.resolution import retrieve_resolved_secret


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for retriever tests."""
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
    """Create a valid SecretStore for retriever tests."""
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def make_resolved_secret_location(
    *,
    backend: str = "gopass",
    backend_path: str = "mxm/red/opaque/path",
) -> ResolvedSecretLocation:
    """Create a valid ResolvedSecretLocation for retriever tests."""
    store = make_secret_store(backend=backend)

    return ResolvedSecretLocation(
        secret_ref=make_secret_ref(),
        store=store,
        backend=backend,
        backend_path=backend_path,
    )


def test_retrieve_resolved_secret_calls_gopass_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that gopass retrieval passes backend_path and default to backend."""
    location = make_resolved_secret_location(
        backend="gopass",
        backend_path="mxm/red/opaque/path",
    )

    observed_path = ""
    observed_default: str | None = None

    def mock_is_gopass_available() -> bool:
        return True

    def mock_access_secret(key: str, default: str | None = None) -> str:
        nonlocal observed_path
        nonlocal observed_default

        observed_path = key
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

    result = retrieve_resolved_secret(location, default="fallback")

    assert result == "secret_value"
    assert observed_path == "mxm/red/opaque/path"
    assert observed_default == "fallback"


def test_retrieve_resolved_secret_returns_default_when_gopass_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that unavailable gopass returns default without access call."""
    location = make_resolved_secret_location(backend="gopass")
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

    result = retrieve_resolved_secret(location, default="fallback")

    assert result == "fallback"
    assert access_called is False


def test_retrieve_resolved_secret_passes_default_to_gopass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that gopass fallback behavior receives the supplied default."""
    location = make_resolved_secret_location(backend="gopass")

    def mock_is_gopass_available() -> bool:
        return True

    def mock_access_secret(key: str, default: str | None = None) -> str | None:
        _ = key
        return default

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    result = retrieve_resolved_secret(location, default="fallback")

    assert result == "fallback"


def test_retrieve_resolved_secret_raises_for_unsupported_backend() -> None:
    """Test that unsupported backend names are rejected."""
    location = make_resolved_secret_location(backend="vault")

    with pytest.raises(ValueError, match="Unsupported secret backend: vault"):
        retrieve_resolved_secret(location)
