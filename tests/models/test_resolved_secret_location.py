"""Tests for resolved secret location models."""

import pytest

from mxm.secrets.models import ResolvedSecretLocation, SecretRef, SecretStore


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for resolved location tests."""
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
    """Create a valid SecretStore for resolved location tests."""
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def make_resolved_secret_location(
    *,
    secret_ref: SecretRef | None = None,
    store: SecretStore | None = None,
    backend: str = "gopass",
    backend_path: str = "mxm/red/opaque/path",
) -> ResolvedSecretLocation:
    """Create a valid ResolvedSecretLocation for model tests."""
    resolved_store = store if store is not None else make_secret_store(backend=backend)

    return ResolvedSecretLocation(
        secret_ref=secret_ref if secret_ref is not None else make_secret_ref(),
        store=resolved_store,
        backend=backend,
        backend_path=backend_path,
    )


def test_resolved_secret_location_can_be_created() -> None:
    """Test that a valid resolved secret location can be created."""
    secret_ref = make_secret_ref()
    store = make_secret_store()

    location = ResolvedSecretLocation(
        secret_ref=secret_ref,
        store=store,
        backend="gopass",
        backend_path="mxm/red/opaque/path",
    )

    assert location.secret_ref == secret_ref
    assert location.store == store
    assert location.backend == "gopass"
    assert location.backend_path == "mxm/red/opaque/path"


def test_secret_name_returns_secret_ref_name() -> None:
    """Test that secret_name exposes the logical secret name."""
    location = make_resolved_secret_location(
        secret_ref=make_secret_ref(name="polygon_api_key")
    )

    assert location.secret_name == "polygon_api_key"


def test_store_name_returns_store_name() -> None:
    """Test that store_name exposes the logical store name."""
    location = make_resolved_secret_location(store=make_secret_store(name="yellow"))

    assert location.store_name == "yellow"


def test_diagnostic_name_excludes_backend_path() -> None:
    """Test that diagnostic_name avoids exposing backend path information."""
    location = make_resolved_secret_location(
        secret_ref=make_secret_ref(name="databento_api_key"),
        store=make_secret_store(name="red"),
        backend_path="mxm/red/provider/live/private/path",
    )

    assert location.diagnostic_name == "red:databento_api_key"
    assert "provider" not in location.diagnostic_name
    assert "private" not in location.diagnostic_name
    assert "path" not in location.diagnostic_name


@pytest.mark.parametrize("field_name", ["backend", "backend_path"])
def test_resolved_secret_location_rejects_empty_string_fields(
    field_name: str,
) -> None:
    """Test that empty backend string fields are rejected."""
    values = {
        "backend": "gopass",
        "backend_path": "mxm/red/opaque/path",
    }
    values[field_name] = ""

    with pytest.raises(ValueError, match=f"{field_name} must not be empty"):
        make_resolved_secret_location(
            backend=values["backend"],
            backend_path=values["backend_path"],
        )


@pytest.mark.parametrize("field_name", ["backend", "backend_path"])
def test_resolved_secret_location_rejects_surrounding_whitespace(
    field_name: str,
) -> None:
    """Test that backend string fields with surrounding whitespace are rejected."""
    values = {
        "backend": "gopass",
        "backend_path": "mxm/red/opaque/path",
    }
    values[field_name] = f" {values[field_name]} "

    store = make_secret_store(backend=values["backend"].strip())

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not contain surrounding whitespace",
    ):
        make_resolved_secret_location(
            store=store,
            backend=values["backend"],
            backend_path=values["backend_path"],
        )


@pytest.mark.parametrize("field_name", ["backend", "backend_path"])
def test_resolved_secret_location_rejects_whitespace_only_string_fields(
    field_name: str,
) -> None:
    """Test that whitespace-only backend string fields are rejected."""
    values = {
        "backend": "gopass",
        "backend_path": "mxm/red/opaque/path",
    }
    values[field_name] = "   "

    store = make_secret_store(backend="gopass")

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not contain surrounding whitespace",
    ):
        make_resolved_secret_location(
            store=store,
            backend=values["backend"],
            backend_path=values["backend_path"],
        )


def test_resolved_secret_location_rejects_backend_mismatch() -> None:
    """Test that backend must match the resolved store backend."""
    store = make_secret_store(backend="vault")

    with pytest.raises(ValueError, match="backend must match store backend"):
        make_resolved_secret_location(
            store=store,
            backend="gopass",
        )
