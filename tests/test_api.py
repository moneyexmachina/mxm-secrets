"""Tests for the mxm_secrets public API layer."""

import os
import pytest
from mxm_secrets import api


def test_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment backend returns a matching value."""
    monkeypatch.setenv("PROD_EMAIL_PASSWORD", "supersecret")
    assert api.get_secret("prod/email-password") == "supersecret"


def test_return_default_on_missing() -> None:
    """Test that default is returned when no backend finds a secret."""
    assert api.get_secret("nonexistent/secret", default="fallback") == "fallback"


def test_gopass_skipped_if_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_secret skips gopass if it is not available."""
    monkeypatch.setattr("mxm_secrets.backends.gopass_backend.is_gopass_available", lambda: False)
    monkeypatch.setenv("PROD_SKIP_TEST", "yes")
    assert api.get_secret("prod/skip-test") == "yes"


def test_unknown_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an unknown backend in priority list raises ValueError."""
    monkeypatch.setattr("mxm_secrets.api._BACKEND_PRIORITY", ["unknown"])
    with pytest.raises(ValueError, match="Unknown backend: unknown"):
        api.get_secret("prod/should-fail")


def test_check_backend_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the backend availability checker."""
    monkeypatch.setattr("mxm_secrets.backends.gopass_backend.is_gopass_available", lambda: False)
    monkeypatch.setenv("PROD_READY_CHECK", "ok")
    assert api.check_backend_ready() is True
