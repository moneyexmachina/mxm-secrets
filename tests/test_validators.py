"""Tests for mxm-secrets validators."""

import pytest

from mxm.secrets.validators import validate_identifier, validate_non_empty_clean


@pytest.mark.parametrize(
    "value",
    [
        "marketdata",
        "execution",
        "research",
        "prefect_worker",
        "human_admin",
        "marketdata_v2",
        "a",
        "a1",
    ],
)
def test_validate_identifier_accepts_valid_identifiers(value: str) -> None:
    """Test that valid registry identifiers are accepted."""
    validate_identifier("name", value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        " marketdata",
        "marketdata ",
        "MarketData",
        "market-data",
        "market data",
        "marketdata!",
        "-marketdata",
        "1marketdata",
    ],
)
def test_validate_identifier_rejects_invalid_identifiers(value: str) -> None:
    """Test that invalid registry identifiers are rejected."""
    with pytest.raises(ValueError):
        validate_identifier("name", value)


def test_validate_identifier_reports_pattern_mismatch() -> None:
    """Test that identifier pattern failures report the expected pattern."""
    with pytest.raises(
        ValueError,
        match=r"name must match pattern: \^\[a-z\]\[a-z0-9_\]\*\$",
    ):
        validate_identifier("name", "market-data")


def test_validate_non_empty_clean_accepts_clean_value() -> None:
    """Test that a clean non-empty string is accepted."""
    validate_non_empty_clean("field", "clean value")


def test_validate_non_empty_clean_rejects_empty_value() -> None:
    """Test that an empty string is rejected."""
    with pytest.raises(ValueError, match="field must not be empty"):
        validate_non_empty_clean("field", "")


def test_validate_non_empty_clean_rejects_surrounding_whitespace() -> None:
    """Test that surrounding whitespace is rejected."""
    with pytest.raises(
        ValueError,
        match="field must not contain surrounding whitespace",
    ):
        validate_non_empty_clean("field", " clean value ")


def test_validate_non_empty_clean_rejects_whitespace_only_value() -> None:
    """Test that whitespace-only strings are rejected."""
    with pytest.raises(
        ValueError,
        match="field must not contain surrounding whitespace",
    ):
        validate_non_empty_clean("field", "   ")
