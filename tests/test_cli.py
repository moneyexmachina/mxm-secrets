"""Tests for the mxm-secrets command-line interface."""

import pytest
from click.testing import CliRunner

from mxm.secrets.__main__ import cli


def test_cli_check_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that check exits successfully when the backend is ready."""

    def mock_check_ready(self: object) -> bool:
        _ = self
        return True

    monkeypatch.setattr("mxm.secrets.api.SecretsApi.check_ready", mock_check_ready)

    runner = CliRunner()
    result = runner.invoke(cli, ["check"])

    assert result.exit_code == 0
    assert "[OK] gopass backend available" in result.output


def test_cli_check_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that check exits with an error when the backend is unavailable."""

    def mock_check_ready(self: object) -> bool:
        _ = self
        return False

    monkeypatch.setattr("mxm.secrets.api.SecretsApi.check_ready", mock_check_ready)

    runner = CliRunner()
    result = runner.invoke(cli, ["check"])

    assert result.exit_code == 1
    assert "[ERROR] gopass backend unavailable" in result.output
