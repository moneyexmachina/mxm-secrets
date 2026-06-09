"""
MXM Secrets

Unified secrets access layer for the Money Ex Machina infrastructure.

Exposes:
- SecretsApi: Primary interface for all secret resolution
"""

from .api import SecretsApi

__all__ = ["SecretsApi"]
