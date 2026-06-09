"""Tests for mxm.secrets config-data ingestion helpers."""

from __future__ import annotations

import pytest

from mxm.secrets.config_data.secret_store import load_secret_stores_from_config_data
from mxm.secrets.models import SecretStore
from mxm.types import JSONValue


def test_load_secret_stores_from_config_data_returns_secret_stores() -> None:
    """Valid store config data should produce validated SecretStore objects."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
            "root": "mxm/red",
        },
    }

    stores = load_secret_stores_from_config_data(config)

    assert stores == (
        SecretStore(
            name="red",
            backend="gopass",
            root="mxm/red",
        ),
    )


def test_load_secret_stores_from_config_data_supports_multiple_stores() -> None:
    """Multiple store configs should produce one SecretStore per entry."""
    config: dict[str, JSONValue] = {
        "green": {
            "backend": "gopass",
            "root": "mxm/green",
        },
        "red": {
            "backend": "gopass",
            "root": "mxm/red",
        },
    }

    stores = load_secret_stores_from_config_data(config)

    assert stores == (
        SecretStore(
            name="green",
            backend="gopass",
            root="mxm/green",
        ),
        SecretStore(
            name="red",
            backend="gopass",
            root="mxm/red",
        ),
    )


def test_load_secret_stores_from_config_data_rejects_non_mapping_entry() -> None:
    """Each configured store entry must be a mapping."""
    config: dict[str, JSONValue] = {
        "red": "not-a-mapping",
    }

    with pytest.raises(TypeError, match="Secret store config for 'red'"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_requires_backend() -> None:
    """Each store config must include a string backend field."""
    config: dict[str, JSONValue] = {
        "red": {
            "root": "mxm/red",
        },
    }

    with pytest.raises(TypeError, match="backend"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_requires_string_backend() -> None:
    """The backend field must be a string."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": 123,
            "root": "mxm/red",
        },
    }

    with pytest.raises(TypeError, match="backend"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_requires_root() -> None:
    """Each store config must include a string root field."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
        },
    }

    with pytest.raises(TypeError, match="root"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_requires_string_root() -> None:
    """The root field must be a string."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
            "root": ["mxm", "red"],
        },
    }

    with pytest.raises(TypeError, match="root"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_rejects_invalid_store_name() -> None:
    """Store name validation should be delegated to SecretStore."""
    config: dict[str, JSONValue] = {
        "not-valid": {
            "backend": "gopass",
            "root": "mxm/red",
        },
    }

    with pytest.raises(ValueError, match="name"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_rejects_invalid_backend() -> None:
    """Backend validation should be delegated to SecretStore."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "not-valid",
            "root": "mxm/red",
        },
    }

    with pytest.raises(ValueError, match="backend"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_rejects_empty_root() -> None:
    """Root validation should be delegated to SecretStore."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
            "root": "",
        },
    }

    with pytest.raises(ValueError, match="root"):
        load_secret_stores_from_config_data(config)


def test_load_secret_stores_from_config_data_rejects_unclean_root() -> None:
    """Root whitespace validation should be delegated to SecretStore."""
    config: dict[str, JSONValue] = {
        "red": {
            "backend": "gopass",
            "root": " mxm/red ",
        },
    }

    with pytest.raises(ValueError, match="root"):
        load_secret_stores_from_config_data(config)
