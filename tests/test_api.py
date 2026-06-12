"""Tests for the public mxm-secrets API."""

import pytest

from mxm.secrets.api import SecretsApi
from mxm.secrets.models import SecretPolicy, SecretRef, SecretStore
from mxm.secrets.registries import (
    SecretPolicyRegistry,
    SecretRefRegistry,
    SecretStoreRegistry,
)
from mxm.types import JSONValue
from mxm.types.runtime_identity import (
    RuntimeIdentity,
)


def make_runtime_identity(
    *,
    app: str = "mxm_secrets_test",
    environment: str = "dev",
    machine: str = "bridge",
    substrate: str = "local_process",
    role: str = "marketdata",
) -> RuntimeIdentity:
    """Create a RuntimeIdentity for API tests."""
    return RuntimeIdentity(
        app=app,
        environment=environment,
        machine=machine,
        substrate=substrate,
        role=role,
    )


def make_secret_ref(
    *,
    name: str = "test_api_key",
    store: str = "red",
    path: str = "opaque/test_api_key",
    policy: str = "test_policy",
) -> SecretRef:
    """Create a valid SecretRef for API tests."""
    return SecretRef(
        name=name,
        store=store,
        path=path,
        policy=policy,
    )


def make_secret_store(
    *,
    name: str = "red",
    backend: str = "gopass",
    root: str = "mxm/red",
) -> SecretStore:
    """Create a valid SecretStore for API tests."""
    return SecretStore(
        name=name,
        backend=backend,
        root=root,
    )


def make_secret_policy(
    *,
    name: str = "test_policy",
    allowed_principals: tuple[str, ...] = ("marketdata",),
) -> SecretPolicy:
    """Create a valid SecretPolicy for API tests."""
    return SecretPolicy(
        name=name,
        allowed_principals=allowed_principals,
    )


def make_secrets_api(
    *,
    secret_ref: SecretRef | None = None,
    secret_store: SecretStore | None = None,
    secret_policy: SecretPolicy | None = None,
) -> SecretsApi:
    """Create a SecretsApi with in-memory test registries."""
    return SecretsApi(
        secret_ref_registry=SecretRefRegistry(
            [secret_ref if secret_ref is not None else make_secret_ref()]
        ),
        secret_store_registry=SecretStoreRegistry(
            [secret_store if secret_store is not None else make_secret_store()]
        ),
        secret_policy_registry=SecretPolicyRegistry(
            [secret_policy if secret_policy is not None else make_secret_policy()]
        ),
    )


def test_get_secret_retrieves_configured_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that SecretsApi authorizes, resolves, and retrieves via gopass."""
    api = make_secrets_api()
    identity = make_runtime_identity(role="marketdata")
    observed_key = ""
    observed_default: str | None = None

    def mock_is_gopass_available() -> bool:
        return True

    def mock_access_secret(key: str, default: str | None = None) -> str:
        nonlocal observed_key
        nonlocal observed_default

        observed_key = key
        observed_default = default
        return "secret_value"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    result = api.get_secret(
        "test_api_key",
        identity=identity,
        default="fallback",
    )

    assert result == "secret_value"
    assert observed_key == "mxm/red/opaque/test_api_key"
    assert observed_default == "fallback"


def test_get_secret_returns_default_when_gopass_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that SecretsApi returns default when gopass is unavailable."""
    api = make_secrets_api()
    identity = make_runtime_identity(role="marketdata")
    access_called = False

    def mock_is_gopass_available() -> bool:
        return False

    def mock_access_secret(key: str, default: str | None = None) -> str | None:
        nonlocal access_called
        _ = key
        _ = default

        access_called = True
        return "should_not_be_used"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.is_gopass_available",
        mock_is_gopass_available,
    )
    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    result = api.get_secret(
        "test_api_key",
        identity=identity,
        default="fallback",
    )

    assert result == "fallback"
    assert access_called is False


def test_get_secret_raises_for_unknown_secret_name() -> None:
    """Test that unknown secret names fail at the API boundary."""
    api = make_secrets_api()
    identity = make_runtime_identity(role="marketdata")

    with pytest.raises(KeyError, match="Unknown secret name: missing_secret"):
        api.get_secret("missing_secret", identity=identity)


def test_get_secret_raises_for_unknown_policy_name() -> None:
    """Test that SecretRefs referencing unknown policies fail."""
    api = make_secrets_api(secret_ref=make_secret_ref(policy="missing_policy"))
    identity = make_runtime_identity(role="marketdata")

    with pytest.raises(KeyError, match="Unknown secret policy: missing_policy"):
        api.get_secret("test_api_key", identity=identity)


def test_get_secret_denies_unauthorized_principal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that unauthorized principals are denied before retrieval."""
    api = make_secrets_api(
        secret_policy=make_secret_policy(allowed_principals=("execution",))
    )
    identity = make_runtime_identity(role="marketdata")
    access_called = False

    def mock_access_secret(key: str, default: str | None = None) -> str:
        nonlocal access_called
        _ = key
        _ = default

        access_called = True
        return "should_not_be_used"

    monkeypatch.setattr(
        "mxm.secrets.backends.gopass_backend.access_secret",
        mock_access_secret,
    )

    with pytest.raises(
        PermissionError,
        match="Secret access denied: red:test_api_key for principal marketdata",
    ):
        api.get_secret("test_api_key", identity=identity)

    assert access_called is False


def test_get_secret_raises_for_unknown_store_name() -> None:
    """Test that SecretRefs referencing unknown stores fail after authorization."""
    api = make_secrets_api(secret_ref=make_secret_ref(store="missing_store"))
    identity = make_runtime_identity(role="marketdata")

    with pytest.raises(KeyError, match="Unknown secret store: missing_store"):
        api.get_secret("test_api_key", identity=identity)


def test_get_secret_raises_for_unsupported_backend() -> None:
    """Test that non-gopass backends are rejected after authorization."""
    api = make_secrets_api(secret_store=make_secret_store(backend="vault"))
    identity = make_runtime_identity(role="marketdata")

    with pytest.raises(ValueError, match="Unsupported secret backend: vault"):
        api.get_secret("test_api_key", identity=identity)


def test_get_secret_rejects_invalid_runtime_role() -> None:
    """Test that invalid RuntimeIdentity roles fail principal construction."""
    api = make_secrets_api()
    identity = make_runtime_identity(role="market-data")

    with pytest.raises(ValueError, match="name must match pattern"):
        api.get_secret("test_api_key", identity=identity)


def test_from_config_data_constructs_configured_api() -> None:
    """from_config_data should construct an API with configured registries."""
    config: dict[str, JSONValue] = {
        "stores": {
            "red": {
                "backend": "gopass",
                "root": "mxm/red",
            },
        },
        "refs": {
            "databento_api_key": {
                "store": "red",
                "path": "marketdata/databento/api_key",
                "policy": "marketdata_access",
            },
        },
        "policies": {
            "marketdata_access": {
                "allowed_principals": ["marketdata", "research"],
            },
        },
    }

    api = SecretsApi.from_config_data(config)

    assert api.secret_store_registry.contains("red")
    assert api.secret_ref_registry.contains("databento_api_key")
    assert api.secret_policy_registry.contains("marketdata_access")


def test_from_config_data_rejects_missing_stores_section() -> None:
    """from_config_data should require a stores section."""
    config: dict[str, JSONValue] = {
        "refs": {},
        "policies": {},
    }

    with pytest.raises(TypeError, match="stores"):
        SecretsApi.from_config_data(config)


def test_from_config_data_rejects_missing_refs_section() -> None:
    """from_config_data should require a refs section."""
    config: dict[str, JSONValue] = {
        "stores": {},
        "policies": {},
    }

    with pytest.raises(TypeError, match="refs"):
        SecretsApi.from_config_data(config)


def test_from_config_data_rejects_missing_policies_section() -> None:
    """from_config_data should require a policies section."""
    config: dict[str, JSONValue] = {
        "stores": {},
        "refs": {},
    }

    with pytest.raises(TypeError, match="policies"):
        SecretsApi.from_config_data(config)


def test_from_config_data_rejects_non_mapping_stores_section() -> None:
    """from_config_data should require stores to be a mapping."""
    config: dict[str, JSONValue] = {
        "stores": "not-a-mapping",
        "refs": {},
        "policies": {},
    }

    with pytest.raises(TypeError, match="stores"):
        SecretsApi.from_config_data(config)


def test_from_config_data_rejects_non_mapping_refs_section() -> None:
    """from_config_data should require refs to be a mapping."""
    config: dict[str, JSONValue] = {
        "stores": {},
        "refs": "not-a-mapping",
        "policies": {},
    }

    with pytest.raises(TypeError, match="refs"):
        SecretsApi.from_config_data(config)


def test_from_config_data_rejects_non_mapping_policies_section() -> None:
    """from_config_data should require policies to be a mapping."""
    config: dict[str, JSONValue] = {
        "stores": {},
        "refs": {},
        "policies": "not-a-mapping",
    }

    with pytest.raises(TypeError, match="policies"):
        SecretsApi.from_config_data(config)


def test_from_config_data_propagates_nested_config_errors() -> None:
    """from_config_data should propagate validation errors from registries."""
    config: dict[str, JSONValue] = {
        "stores": {
            "red": "not-a-mapping",
        },
        "refs": {},
        "policies": {},
    }

    with pytest.raises(TypeError, match="Secret store config"):
        SecretsApi.from_config_data(config)
