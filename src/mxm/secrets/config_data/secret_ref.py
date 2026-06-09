"""Secret-reference config-data ingestion for mxm-secrets.

This module converts plain, resolved secret-reference configuration data into
validated ``SecretRef`` model objects.

It deliberately does not depend on mxm-config, OmegaConf, or RuntimeContext.
Configuration loading and slicing belong to mxm-config and mxm-runtime. This
module only understands the inner ``refs`` configuration shape passed across
that boundary.

Expected ref config shape:

```yaml
databento_api_key:
  store: red
  path: marketdata/databento/api_key
  policy: marketdata_access
```
"""

from __future__ import annotations

from collections.abc import Mapping

from mxm.secrets.config_data.require import require_mapping, require_string_field
from mxm.secrets.models import SecretRef
from mxm.types import JSONValue

type SecretRefsConfigData = Mapping[str, JSONValue]


def load_secret_refs_from_config_data(
    config: SecretRefsConfigData,
) -> tuple[SecretRef, ...]:
    """Construct configured secret references from plain config data.

    Parameters
    ----------
    config
        Mapping from public secret name to secret-reference configuration. Each
        reference configuration must be a mapping with string fields:

        - ``store``: logical secret store name.
        - ``path``: store-relative secret path.
        - ``policy``: logical secret policy name.

    Returns
    -------
    tuple[SecretRef, ...]
        Immutable tuple of validated ``SecretRef`` objects.

    Raises
    ------
    TypeError
        If a reference entry is not a mapping, or if required fields are not
        strings.
    ValueError
        If the resulting ``SecretRef`` fails model validation.
    """
    refs: list[SecretRef] = []

    for name, value in config.items():
        ref_config = require_mapping(
            value=value,
            description=f"Secret reference config for {name!r}",
        )

        store = require_string_field(
            config=ref_config,
            field_name="store",
            description=f"Secret reference config for {name!r}",
        )
        path = require_string_field(
            config=ref_config,
            field_name="path",
            description=f"Secret reference config for {name!r}",
        )
        policy = require_string_field(
            config=ref_config,
            field_name="policy",
            description=f"Secret reference config for {name!r}",
        )

        refs.append(
            SecretRef(
                name=name,
                store=store,
                path=path,
                policy=policy,
            )
        )

    return tuple(refs)
