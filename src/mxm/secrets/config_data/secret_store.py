"""Config-data ingestion helpers for mxm-secrets.

This module converts plain, resolved configuration data into mxm-secrets model
objects.

It deliberately does not depend on mxm-config, OmegaConf, or RuntimeContext.
Configuration loading and slicing belong to mxm-config and mxm-runtime. This
module only understands the inner secrets configuration shape passed across that
boundary.

Expected store config shape:

```yaml
red:
  backend: gopass
  root: mxm/red
```
"""

from __future__ import annotations

from collections.abc import Mapping

from mxm.secrets.config_data.require import require_mapping, require_string_field
from mxm.secrets.models import SecretStore
from mxm.types import JSONValue

type SecretStoresConfigData = Mapping[str, JSONValue]


def load_secret_stores_from_config_data(
    config: SecretStoresConfigData,
) -> tuple[SecretStore, ...]:
    """Construct configured secret stores from plain config data.

    Parameters
    ----------
    config
        Mapping from logical store name to store configuration. Each store
        configuration must be a mapping with string fields:

        - ``backend``: backend implementation name, for example ``"gopass"``.
        - ``root``: backend-specific root path or namespace.

    Returns
    -------
    tuple[SecretStore, ...]
        Immutable tuple of validated ``SecretStore`` objects.

    Raises
    ------
    TypeError
        If a store entry is not a mapping, or if required fields are not
        strings.
    ValueError
        If the resulting ``SecretStore`` fails model validation.
    """
    stores: list[SecretStore] = []

    for name, value in config.items():
        store_config = require_mapping(
            value=value,
            description=f"Secret store config for {name!r}",
        )

        backend = require_string_field(
            config=store_config,
            field_name="backend",
            description=f"Secret store config for {name!r}",
        )
        root = require_string_field(
            config=store_config,
            field_name="root",
            description=f"Secret store config for {name!r}",
        )

        stores.append(
            SecretStore(
                name=name,
                backend=backend,
                root=root,
            )
        )

    return tuple(stores)
