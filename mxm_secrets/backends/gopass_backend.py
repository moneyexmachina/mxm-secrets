"""mxm_secrets.backends.gopass_backend

Backend implementation for accessing secrets via the `gopass` CLI.

This module provides a single function, `access_secret(key, default)`, which attempts to
resolve the given secret key using `gopass show`. It is designed to be consumed via
the public API in `mxm_secrets.api`, not used directly.

Behavior:
- Fails silently (returns default) if `gopass` returns a non-zero exit code
- Strips trailing whitespace from output
- Assumes `gopass` is installed and a GPG key is unlocked or passphrase-less

Example:
    from mxm_secrets.backends.gopass_backend import access_secret

    secret = access_secret("prod/db-password")

Note:
This module avoids naming conflicts by using `access_secret` instead of `get_secret`.
"""

import shutil
import subprocess
import sys
from typing import Optional


VERBOSE = False


def is_gopass_available() -> bool:
    """Check whether gopass is installed and the store is initialized."""
    if shutil.which("gopass") is None:
        return False
    try:
        subprocess.run(
            ["gopass", "ls"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def access_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret using the gopass CLI.

    Attempts to resolve the given key using `gopass show <key>`. If the key is
    not found or gopass fails for any reason, returns the provided `default`.

    Args:
        key (str): The key to resolve, e.g., "prod/smtp-password".
        default (Optional[str]): Value to return if the secret is not found.

    Returns:
        Optional[str]: The retrieved secret, or `default` if unavailable.

    Notes:
        - Output is stripped of leading/trailing whitespace.
        - If VERBOSE is True, errors from gopass are printed to stderr.
        - Requires `gopass` to be installed and properly initialized.
    """
    try:
        result = subprocess.check_output(
            ["gopass", "show", key],
            text=True,
            stderr=None if VERBOSE else subprocess.DEVNULL,
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        if VERBOSE:
            print(f"[gopass error] {e}", file=sys.stderr)
        return default
