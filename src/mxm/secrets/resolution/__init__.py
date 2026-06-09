"""Resolution helpers for mxm-secrets."""

from mxm.secrets.resolution.principal_resolution import principal_from_runtime_identity
from mxm.secrets.resolution.secret_location_resolution import resolve_secret_location
from mxm.secrets.resolution.secret_retriever import retrieve_resolved_secret

__all__ = [
    "principal_from_runtime_identity",
    "resolve_secret_location",
    "retrieve_resolved_secret",
]
