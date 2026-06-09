"""Resolution helpers for mxm-secrets."""

from mxm.secrets.resolution.secret_location_resolver import resolve_secret_location
from mxm.secrets.resolution.secret_retriever import retrieve_resolved_secret

__all__ = [
    "resolve_secret_location",
    "retrieve_resolved_secret",
]
