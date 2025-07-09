"""mxm-secrets CLI entrypoint.

Provides a minimal, extensible command-line interface for interacting with
the MXM secrets layer. Supports retrieving secrets from gopass or environment
backends with options for fallback and verbose output.

Usage:
    poetry run python -m mxm_secrets get <key> [--default <val>] [--verbose]
"""

import sys
import click
from mxm_secrets import api
import mxm_secrets.backends.gopass_backend as gopass_backend


@click.group()
def cli() -> None:
    """mxm-secrets command-line interface."""
    pass


@cli.command()
@click.argument("key")
@click.option(
    "--default",
    default=None,
    help="Default value to return if the secret is not found.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose error output from backend (e.g. gopass).",
)
def get(key: str, default: str | None, verbose: bool) -> None:
    """Retrieve a secret using the given KEY."""
    if verbose:
        gopass_backend.VERBOSE = True

    try:
        secret = api.get_secret(key, default=default)
        if secret is None:
            click.secho("[NOT FOUND]", err=True, fg="red")
            sys.exit(1)
        click.echo(secret)
    except Exception as exc:
        click.secho(f"Error: {exc}", err=True, fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()

