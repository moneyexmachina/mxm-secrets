"""Tests for the gopass backend of mxm-secrets."""

import subprocess
import pytest
from mxm_secrets.backends import gopass_backend


def test_gopass_access_secret_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_check_output(cmd: list[str], **kwargs) -> str:
        assert cmd == ["gopass", "show", "prod/email-password"]
        return "gopass-secret\n"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    secret = gopass_backend.access_secret("prod/email-password")
    assert secret == "gopass-secret"


def test_gopass_access_secret_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(*args, **kwargs) -> None:
        raise subprocess.CalledProcessError(1, "gopass show")

    monkeypatch.setattr(subprocess, "check_output", raise_error)
    secret = gopass_backend.access_secret("missing/secret", default="default")
    assert secret == "default"
