"""
MXM Secrets

Unified secrets access layer for the Money Ex Machina infrastructure.

Exposes:
- get_secret: Primary interface for all secret resolution
"""

from .api import get_secret

__all__ = ["get_secret"]

