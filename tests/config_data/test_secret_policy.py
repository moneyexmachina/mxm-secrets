"""Secret-policy config-data ingestion for mxm-secrets.

This module converts plain, resolved secret-policy configuration data into
validated ``SecretPolicy`` model objects.

It deliberately does not depend on mxm-config, OmegaConf, or RuntimeContext.
Configuration loading and slicing belong to mxm-config and mxm-runtime. This
module only understands the inner ``policies`` configuration shape passed across
that boundary.

Expected policy config shape:

```yaml
marketdata_access:
  allowed_principals:
    - marketdata
    - research
```
"""

from __future__ import annotations

from collections.abc import Mapping

from mxm.secrets.config_data.require import (
    require_mapping,
    require_string_sequence_field,
)
from mxm.secrets.models import SecretPolicy
from mxm.types import JSONValue

type SecretPoliciesConfigData = Mapping[str, JSONValue]


def load_secret_policies_from_config_data(
    config: SecretPoliciesConfigData,
) -> tuple[SecretPolicy, ...]:
    """Construct configured secret policies from plain config data.

    Parameters
    ----------
    config
        Mapping from logical policy name to secret-policy configuration. Each
        policy configuration must be a mapping with field:

        - ``allowed_principals``: sequence of principal names allowed by this
          policy.

    Returns
    -------
    tuple[SecretPolicy, ...]
        Immutable tuple of validated ``SecretPolicy`` objects.

    Raises
    ------
    TypeError
        If a policy entry is not a mapping, or if required fields have the
        wrong structural type.
    ValueError
        If the resulting ``SecretPolicy`` fails model validation.
    """
    policies: list[SecretPolicy] = []

    for name, value in config.items():
        policy_config = require_mapping(
            value=value,
            description=f"Secret policy config for {name!r}",
        )

        allowed_principals = require_string_sequence_field(
            config=policy_config,
            field_name="allowed_principals",
            description=f"Secret policy config for {name!r}",
        )

        policies.append(
            SecretPolicy(
                name=name,
                allowed_principals=allowed_principals,
            )
        )

    return tuple(policies)
