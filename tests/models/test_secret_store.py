"""Tests for configured secret store models."""

import pytest

from mxm.secrets.models import SecretStore


def make_secret_store(
    *,
    name: str = "red",
    backend: str = "gopass",
    root: str = "mxm/red",
) -> SecretStore:
    """Create a valid SecretStore for model tests.

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


def test_secret_store_can_be_created() -> None:
    """Test that a valid SecretStore can be created."""
    store = make_secret_store()

    assert store.name == "red"
    assert store.backend == "gopass"
    assert store.root == "mxm/red"


def test_secret_store_rejects_invalid_name_identifier() -> None:
    """Test that store name must be a valid identifier."""
    with pytest.raises(ValueError, match="name must match pattern"):
        make_secret_store(name="red-store")


def test_secret_store_rejects_invalid_backend_identifier() -> None:
    """Test that backend name must be a valid identifier."""
    with pytest.raises(ValueError, match="backend must match pattern"):
        make_secret_store(backend="GoPass")


def test_secret_store_rejects_empty_root() -> None:
    """Test that empty root is rejected."""
    with pytest.raises(ValueError, match="root must not be empty"):
        make_secret_store(root="")


def test_secret_store_rejects_root_with_surrounding_whitespace() -> None:
    """Test that root with surrounding whitespace is rejected."""
    with pytest.raises(
        ValueError,
        match="root must not contain surrounding whitespace",
    ):
        make_secret_store(root=" mxm/red ")


def test_secret_store_rejects_whitespace_only_root() -> None:
    """Test that whitespace-only root is rejected."""
    with pytest.raises(
        ValueError,
        match="root must not contain surrounding whitespace",
    ):
        make_secret_store(root="   ")


def test_resolve_path_joins_root_and_relative_path() -> None:
    """Test that resolve_path joins the store root and secret path."""
    store = make_secret_store(root="mxm/red")

    assert store.resolve_path("opaque/path") == "mxm/red/opaque/path"


def test_resolve_path_handles_trailing_root_slash() -> None:
    """Test that resolve_path avoids duplicate slashes after root."""
    store = make_secret_store(root="mxm/red/")

    assert store.resolve_path("opaque/path") == "mxm/red/opaque/path"


def test_resolve_path_rejects_empty_secret_path() -> None:
    """Test that resolve_path rejects empty secret paths."""
    store = make_secret_store()

    with pytest.raises(ValueError, match="secret_path must not be empty"):
        store.resolve_path("")


def test_resolve_path_rejects_surrounding_whitespace() -> None:
    """Test that resolve_path rejects paths with surrounding whitespace."""
    store = make_secret_store()

    with pytest.raises(
        ValueError,
        match="secret_path must not contain surrounding whitespace",
    ):
        store.resolve_path(" opaque/path ")


def test_resolve_path_rejects_whitespace_only_path() -> None:
    """Test that resolve_path rejects whitespace-only paths."""
    store = make_secret_store()

    with pytest.raises(
        ValueError,
        match="secret_path must not contain surrounding whitespace",
    ):
        store.resolve_path("   ")


def test_resolve_path_rejects_absolute_path() -> None:
    """Test that resolve_path rejects absolute paths."""
    store = make_secret_store()

    with pytest.raises(ValueError, match="secret_path must be relative"):
        store.resolve_path("/opaque/path")


def test_resolve_path_does_not_mutate_store() -> None:
    """Test that resolve_path leaves the store configuration unchanged."""
    store = make_secret_store()

    _ = store.resolve_path("opaque/path")

    assert store.name == "red"
    assert store.backend == "gopass"
    assert store.root == "mxm/red"
