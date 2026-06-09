"""mxm-secrets CLI entry point.

This module currently provides only lightweight diagnostics for the mxm-secrets
package.

The previous `get` command has been removed during the Session 47C refactor
because secret retrieval now requires configured registries and, soon,
RuntimeIdentity-based authorization. Production CLI secret retrieval should be
reintroduced after RuntimeContext construction exists in mxm-runtime.

TODO:
    Reintroduce a secret retrieval CLI once mxm-runtime can construct a fully
    configured SecretsApi from RuntimeContext.
"""

from __future__ import annotations

import sys

import click

from mxm.secrets.api import SecretsApi
from mxm.secrets.registries import (
    SecretPolicyRegistry,
    SecretRefRegistry,
    SecretStoreRegistry,
)


@click.group()
def cli() -> None:
    """mxm-secrets command-line interface."""
    pass


@cli.command()
def check() -> None:
    """Check whether the currently supported secret backend is available."""
    api = SecretsApi(
        secret_ref_registry=SecretRefRegistry([]),
        secret_store_registry=SecretStoreRegistry([]),
        secret_policy_registry=SecretPolicyRegistry([]),
    )

    if api.check_ready():
        click.secho("[OK] gopass backend available", fg="green")
        return

    click.secho("[ERROR] gopass backend unavailable", err=True, fg="red")
    sys.exit(1)


if __name__ == "__main__":
    cli()
