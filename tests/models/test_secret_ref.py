"""Tests for configured secret reference models."""

import pytest

from mxm.secrets.models import SecretRef


def test_secret_ref_can_be_created() -> None:
    ref = SecretRef(
        name="databento_api_key",
        store="red",
        path="opaque/path",
        policy="marketdata_access",
    )

    assert ref.name == "databento_api_key"
    assert ref.store == "red"
    assert ref.path == "opaque/path"
    assert ref.policy == "marketdata_access"


def test_secret_ref_qualified_name_excludes_path() -> None:
    ref = SecretRef(
        name="databento_api_key",
        store="red",
        path="sensitive/provider/path",
        policy="marketdata_access",
    )

    assert ref.qualified_name == "red:databento_api_key"
    assert "sensitive" not in ref.qualified_name
    assert "provider" not in ref.qualified_name


@pytest.mark.parametrize("field_name", ["name", "store", "path", "policy"])
def test_secret_ref_rejects_empty_fields(field_name: str) -> None:
    values = {
        "name": "databento_api_key",
        "store": "red",
        "path": "opaque/path",
        "policy": "marketdata_access",
    }
    values[field_name] = ""

    with pytest.raises(ValueError, match=f"{field_name} must not be empty"):
        SecretRef(**values)


@pytest.mark.parametrize("field_name", ["name", "store", "path", "policy"])
def test_secret_ref_rejects_surrounding_whitespace(field_name: str) -> None:
    values = {
        "name": "databento_api_key",
        "store": "red",
        "path": "opaque/path",
        "policy": "marketdata_access",
    }
    values[field_name] = f" {values[field_name]} "

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not contain surrounding whitespace",
    ):
        SecretRef(**values)


@pytest.mark.parametrize("field_name", ["name", "store", "path", "policy"])
def test_secret_ref_rejects_whitespace_only_fields(field_name: str) -> None:
    values = {
        "name": "databento_api_key",
        "store": "red",
        "path": "opaque/path",
        "policy": "marketdata_access",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not contain surrounding whitespace",
    ):
        SecretRef(**values)
