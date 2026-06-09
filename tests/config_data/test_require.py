"""Tests for config-data requirement helpers."""

from __future__ import annotations

import pytest

from mxm.secrets.config_data.require import (
    require_mapping,
    require_string_field,
    require_string_sequence_field,
)
from mxm.types import JSONValue


def test_require_mapping_returns_mapping() -> None:
    """A mapping value should be returned unchanged."""
    value: JSONValue = {
        "backend": "gopass",
        "root": "mxm/red",
    }

    result = require_mapping(
        value=value,
        description="Test mapping",
    )

    assert result["backend"] == "gopass"
    assert result["root"] == "mxm/red"


@pytest.mark.parametrize(
    "value",
    [
        "not-a-mapping",
        123,
        1.23,
        True,
        None,
        ["a", "b"],
    ],
)
def test_require_mapping_rejects_non_mapping(
    value: JSONValue,
) -> None:
    """Non-mapping values should raise TypeError."""
    with pytest.raises(TypeError, match="must be a mapping"):
        require_mapping(
            value=value,
            description="Test mapping",
        )


def test_require_string_field_returns_string() -> None:
    """A string field should be returned unchanged."""
    config: dict[str, JSONValue] = {
        "backend": "gopass",
    }

    result = require_string_field(
        config=config,
        field_name="backend",
        description="Test config",
    )

    assert result == "gopass"


def test_require_string_field_rejects_missing_field() -> None:
    """Missing fields should raise TypeError."""
    config: dict[str, JSONValue] = {}

    with pytest.raises(TypeError, match="backend"):
        require_string_field(
            config=config,
            field_name="backend",
            description="Test config",
        )


@pytest.mark.parametrize(
    "value",
    [
        123,
        1.23,
        True,
        None,
        ["gopass"],
        {"name": "gopass"},
    ],
)
def test_require_string_field_rejects_non_string_field(
    value: JSONValue,
) -> None:
    """Non-string fields should raise TypeError."""
    config: dict[str, JSONValue] = {
        "backend": value,
    }

    with pytest.raises(TypeError, match="backend"):
        require_string_field(
            config=config,
            field_name="backend",
            description="Test config",
        )


def test_require_string_sequence_field_returns_tuple_of_strings() -> None:
    """A string-list field should be returned as a tuple."""
    config: dict[str, JSONValue] = {
        "allowed_principals": ["marketdata", "research"],
    }

    result = require_string_sequence_field(
        config=config,
        field_name="allowed_principals",
        description="Test config",
    )

    assert result == ("marketdata", "research")


def test_require_string_sequence_field_rejects_missing_field() -> None:
    """Missing sequence fields should raise TypeError."""
    config: dict[str, JSONValue] = {}

    with pytest.raises(TypeError, match="allowed_principals"):
        require_string_sequence_field(
            config=config,
            field_name="allowed_principals",
            description="Test config",
        )


@pytest.mark.parametrize(
    "value",
    [
        "marketdata",
        123,
        1.23,
        True,
        None,
        {"principal": "marketdata"},
    ],
)
def test_require_string_sequence_field_rejects_non_sequence_field(
    value: JSONValue,
) -> None:
    """Non-list fields should raise TypeError."""
    config: dict[str, JSONValue] = {
        "allowed_principals": value,
    }

    with pytest.raises(TypeError, match="allowed_principals"):
        require_string_sequence_field(
            config=config,
            field_name="allowed_principals",
            description="Test config",
        )


@pytest.mark.parametrize(
    "value",
    [
        [123],
        ["marketdata", 123],
        ["marketdata", None],
        ["marketdata", {"name": "research"}],
    ],
)
def test_require_string_sequence_field_rejects_non_string_items(
    value: JSONValue,
) -> None:
    """String-list fields should reject non-string items."""
    config: dict[str, JSONValue] = {
        "allowed_principals": value,
    }

    with pytest.raises(TypeError, match="only strings"):
        require_string_sequence_field(
            config=config,
            field_name="allowed_principals",
            description="Test config",
        )
