"""Tests for the mxm-secrets command-line interface (CLI).

These tests validate the integration between the click-based CLI
and the `mxm.secrets.api.get_secret` function. We do not test click
itself, only our wiring, fallback logic, error handling, and output.

Run via:
    poetry run pytest tests/test_cli.py -v
"""

import pytest
from click.testing import CliRunner

from mxm.secrets.__main__ import cli


def test_cli_get_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that CLI prints a secret when get_secret succeeds."""

    def mock_get_secret(key: str, default: str | None = None) -> str:
        assert key == "prod/smtp-password"
        _ = default
        return "mocked-secret"

    monkeypatch.setattr("mxm.secrets.api.get_secret", mock_get_secret)

    runner = CliRunner()
    result = runner.invoke(cli, ["get", "prod/smtp-password"])

    assert result.exit_code == 0
    assert "mocked-secret" in result.output


def test_cli_get_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that CLI falls back to --default if secret is missing."""

    def mock_get_secret(key: str, default: str | None = None) -> str | None:
        _ = key
        return default

    monkeypatch.setattr("mxm.secrets.api.get_secret", mock_get_secret)

    runner = CliRunner()
    result = runner.invoke(cli, ["get", "missing/key", "--default", "fallback"])

    assert result.exit_code == 0
    assert "fallback" in result.output


def test_cli_get_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that CLI exits with error if secret is None and no default is set."""

    def mock_get_secret(key: str, default: str | None = None) -> None:
        _ = key
        _ = default
        return None

    monkeypatch.setattr("mxm.secrets.api.get_secret", mock_get_secret)

    runner = CliRunner()
    result = runner.invoke(cli, ["get", "missing/key"])

    assert result.exit_code == 1
    assert "[NOT FOUND]" in result.output


def test_cli_get_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that CLI exits with error message if get_secret raises."""

    def mock_get_secret(key: str, default: str | None = None) -> str:
        _ = key
        _ = default
        raise RuntimeError("gopass failed")

    monkeypatch.setattr("mxm.secrets.api.get_secret", mock_get_secret)

    runner = CliRunner()
    result = runner.invoke(cli, ["get", "prod/smtp-password"])

    assert result.exit_code == 1
    assert "Error: gopass failed" in result.output
