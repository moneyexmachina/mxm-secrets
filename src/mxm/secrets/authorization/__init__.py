"""Authorization helpers for mxm-secrets.

This package contains stateless authorization logic used to evaluate whether a
principal may access a configured secret reference under a configured policy.
"""

from mxm.secrets.authorization.policy_evaluation import (
    is_secret_access_allowed,
)

__all__ = [
    "is_secret_access_allowed",
]
