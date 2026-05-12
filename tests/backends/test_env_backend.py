from pytest import MonkeyPatch

from mxm.secrets.backends import env_backend


def test_env_access(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("MY_SECRET_KEY", "value123")
    assert env_backend.access_secret("my/secret-key") == "value123"


def test_env_returns_default(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("NOT_SET", raising=False)
    assert env_backend.access_secret("not/set", default="fallback") == "fallback"
