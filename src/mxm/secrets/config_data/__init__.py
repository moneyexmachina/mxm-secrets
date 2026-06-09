from collections.abc import Mapping

from mxm.secrets.config_data.secret_policy import (
    SecretPoliciesConfigData,
    load_secret_policies_from_config_data,
)
from mxm.secrets.config_data.secret_ref import (
    SecretRefsConfigData,
    load_secret_refs_from_config_data,
)
from mxm.secrets.config_data.secret_store import (
    SecretStoresConfigData,
    load_secret_stores_from_config_data,
)
from mxm.types import JSONValue

type SecretsConfigData = Mapping[str, JSONValue]
__all__ = [
    "SecretPoliciesConfigData",
    "SecretRefsConfigData",
    "SecretStoresConfigData",
    "SecretsConfigData",
    "load_secret_policies_from_config_data",
    "load_secret_refs_from_config_data",
    "load_secret_stores_from_config_data",
]
