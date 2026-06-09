"""Tests for configured secret reference models."""

import pytest

from mxm.secrets.models import SecretRef


def make_secret_ref(
    *,
    name: str = "databento_api_key",
    store: str = "red",
    path: str = "opaque/path",
    policy: str = "marketdata_access",
) -> SecretRef:
    """Create a valid SecretRef for model tests.

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


def test_secret_ref_can_be_created() -> None:
    """Test that a valid SecretRef can be created."""
    ref = make_secret_ref()

    assert ref.name == "databento_api_key"
    assert ref.store == "red"
    assert ref.path == "opaque/path"
    assert ref.policy == "marketdata_access"


def test_secret_ref_rejects_invalid_name_identifier() -> None:
    """Test that secret reference name must be a valid identifier."""
    with pytest.raises(ValueError, match="name must match pattern"):
        make_secret_ref(name="databento-api-key")


def test_secret_ref_rejects_invalid_store_identifier() -> None:
    """Test that store name must be a valid identifier."""
    with pytest.raises(ValueError, match="store must match pattern"):
        make_secret_ref(store="Red")


def test_secret_ref_rejects_invalid_policy_identifier() -> None:
    """Test that policy name must be a valid identifier."""
    with pytest.raises(ValueError, match="policy must match pattern"):
        make_secret_ref(policy="marketdata-access")


def test_secret_ref_rejects_empty_path() -> None:
    """Test that empty path is rejected."""
    with pytest.raises(ValueError, match="path must not be empty"):
        make_secret_ref(path="")


def test_secret_ref_rejects_path_with_surrounding_whitespace() -> None:
    """Test that path with surrounding whitespace is rejected."""
    with pytest.raises(
        ValueError,
        match="path must not contain surrounding whitespace",
    ):
        make_secret_ref(path=" opaque/path ")


def test_secret_ref_rejects_whitespace_only_path() -> None:
    """Test that whitespace-only path is rejected."""
    with pytest.raises(
        ValueError,
        match="path must not contain surrounding whitespace",
    ):
        make_secret_ref(path="   ")


def test_secret_ref_qualified_name_excludes_path() -> None:
    """Test that qualified_name does not expose storage path details."""
    ref = make_secret_ref(path="sensitive/provider/path")

    assert ref.qualified_name == "red:databento_api_key"
    assert "sensitive" not in ref.qualified_name
    assert "provider" not in ref.qualified_name
