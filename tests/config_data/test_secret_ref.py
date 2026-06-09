"""Tests for secret-reference config-data ingestion."""

from __future__ import annotations

import pytest

from mxm.secrets.config_data import load_secret_refs_from_config_data
from mxm.secrets.models import SecretRef
from mxm.types import JSONValue


def test_load_secret_refs_from_config_data_returns_secret_refs() -> None:
    """Valid ref config data should produce validated SecretRef objects."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
    }

    refs = load_secret_refs_from_config_data(config)

    assert refs == (
        SecretRef(
            name="databento_api_key",
            store="red",
            path="marketdata/databento/api_key",
            policy="marketdata_access",
        ),
    )


def test_load_secret_refs_from_config_data_supports_multiple_refs() -> None:
    """Multiple ref configs should produce one SecretRef per entry."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
        "polygon_api_key": {
            "store": "red",
            "path": "marketdata/polygon/api_key",
            "policy": "marketdata_access",
        },
    }

    refs = load_secret_refs_from_config_data(config)

    assert refs == (
        SecretRef(
            name="databento_api_key",
            store="red",
            path="marketdata/databento/api_key",
            policy="marketdata_access",
        ),
        SecretRef(
            name="polygon_api_key",
            store="red",
            path="marketdata/polygon/api_key",
            policy="marketdata_access",
        ),
    )


def test_load_secret_refs_from_config_data_rejects_non_mapping_entry() -> None:
    """Each configured ref entry must be a mapping."""
    config: dict[str, JSONValue] = {
        "databento_api_key": "not-a-mapping",
    }

    with pytest.raises(TypeError, match="Secret reference config"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_store() -> None:
    """Each ref config must include a string store field."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(TypeError, match="store"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_string_store() -> None:
    """The store field must be a string."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": 123,
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(TypeError, match="store"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_path() -> None:
    """Each ref config must include a string path field."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(TypeError, match="path"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_string_path() -> None:
    """The path field must be a string."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": ["marketdata", "databento", "api_key"],
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(TypeError, match="path"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_policy() -> None:
    """Each ref config must include a string policy field."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "marketdata/databento/api_key",
        },
    }

    with pytest.raises(TypeError, match="policy"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_requires_string_policy() -> None:
    """The policy field must be a string."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "marketdata/databento/api_key",
            "policy": ["marketdata_access"],
        },
    }

    with pytest.raises(TypeError, match="policy"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_rejects_invalid_ref_name() -> None:
    """Ref name validation should be delegated to SecretRef."""
    config: dict[str, JSONValue] = {
        "not-valid": {
            "store": "red",
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(ValueError, match="name"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_rejects_invalid_store() -> None:
    """Store validation should be delegated to SecretRef."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "not-valid",
            "path": "marketdata/databento/api_key",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(ValueError, match="store"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_rejects_empty_path() -> None:
    """Path validation should be delegated to SecretRef."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(ValueError, match="path"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_rejects_unclean_path() -> None:
    """Path whitespace validation should be delegated to SecretRef."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": " marketdata/databento/api_key ",
            "policy": "marketdata_access",
        },
    }

    with pytest.raises(ValueError, match="path"):
        load_secret_refs_from_config_data(config)


def test_load_secret_refs_from_config_data_rejects_invalid_policy() -> None:
    """Policy validation should be delegated to SecretRef."""
    config: dict[str, JSONValue] = {
        "databento_api_key": {
            "store": "red",
            "path": "marketdata/databento/api_key",
            "policy": "not-valid",
        },
    }

    with pytest.raises(ValueError, match="policy"):
        load_secret_refs_from_config_data(config)
