import subprocess
from collections.abc import Sequence

import pytest

from mxm.secrets.backends import gopass_backend


def test_gopass_access_secret_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_check_output(
        cmd: Sequence[str],
        *,
        text: bool,
        stderr: int | None,
    ) -> str:
        assert list(cmd) == ["gopass", "show", "prod/email-password"]
        assert text is True
        assert stderr in {subprocess.DEVNULL, None}

        return "gopass-secret\n"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)

    secret = gopass_backend.access_secret("prod/email-password")

    assert secret == "gopass-secret"


def test_gopass_access_secret_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(
        cmd: Sequence[str],
        *,
        text: bool,
        stderr: int | None,
    ) -> str:
        assert list(cmd) == ["gopass", "show", "missing/secret"]
        assert text is True
        assert stderr in {subprocess.DEVNULL, None}

        raise subprocess.CalledProcessError(1, list(cmd))

    monkeypatch.setattr(subprocess, "check_output", raise_error)

    secret = gopass_backend.access_secret("missing/secret", default="default")

    assert secret == "default"
