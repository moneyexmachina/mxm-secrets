"""Validation helpers for mxm-secrets.

This module contains shared validation functions for security-relevant
configuration identifiers.

Identifiers are used as registry keys and policy vocabulary. They are kept
intentionally conservative: lowercase ASCII letters, digits, and hyphens only,
with a leading lowercase letter.
"""

from __future__ import annotations

import re

IDENTIFIER_PATTERN = re.compile("^[a-z][a-z0-9_]*$")


def validate_non_empty_clean(field_name: str, value: str) -> None:
    """Validate that a string field is non-empty and whitespace-clean.

    Args:
        field_name: Name of the field being validated.
        value: Field value to validate.

    Raises:
        ValueError: If value is empty, whitespace-only, or has leading or
            trailing whitespace.
    """
    if not value:
        raise ValueError(f"{field_name} must not be empty")

    if value.strip() != value:
        raise ValueError(f"{field_name} must not contain surrounding whitespace")

    if not value.strip():
        raise ValueError(f"{field_name} must not be whitespace-only")


def validate_identifier(field_name: str, value: str) -> None:
    """Validate a security-relevant registry identifier.

    Valid identifiers must match:

    ```text
    ^[a-z][a-z0-9_]*$
    ```

    This permits lowercase ASCII letters, digits, and underscore, with a leading
    lowercase letter.

    Args:
        field_name: Name of the field being validated.
        value: Identifier value to validate.

    Raises:
        ValueError: If value is empty, whitespace-only, has surrounding
            whitespace, or does not match the identifier pattern.
    """
    validate_non_empty_clean(field_name, value)

    if IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValueError(
            f"{field_name} must match pattern: {IDENTIFIER_PATTERN.pattern}"
        )
