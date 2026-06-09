"""Tests for principal models."""

import pytest

from mxm.secrets.models import Principal


def test_principal_can_be_created() -> None:
    """Test that a valid Principal can be created."""
    principal = Principal(name="marketdata")

    assert principal.name == "marketdata"


def test_principal_rejects_invalid_name() -> None:
    with pytest.raises(ValueError, match="name must match pattern"):
        Principal(name="market-data")
