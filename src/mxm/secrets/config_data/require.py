"""Requirement helpers for mxm-secrets config-data ingestion.

This module contains small validation helpers shared by the config-data
ingestion modules. The helpers validate plain JSON-shaped configuration values
before model objects are constructed.

They deliberately perform only structural checks. Semantic validation remains
the responsibility of the mxm-secrets model objects.
"""

from __future__ import annotations

from collections.abc import Mapping

from mxm.types import JSONValue


def require_mapping(
    *,
    value: JSONValue,
    description: str,
) -> Mapping[str, JSONValue]:
    """Return value as a JSON mapping, or raise TypeError.

    Parameters
    ----------
    value
        JSON value to validate.
    description
        Human-readable description used in error messages.

    Returns
    -------
    Mapping[str, JSONValue]
        The validated mapping value.

    Raises
    ------
    TypeError
        If value is not a mapping.
    """
    if not isinstance(value, Mapping):
        raise TypeError(f"{description} must be a mapping")

    return value


def require_string_field(
    *,
    config: Mapping[str, JSONValue],
    field_name: str,
    description: str,
) -> str:
    """Return a required string field from config, or raise TypeError.

    Parameters
    ----------
    config
        Mapping to read from.
    field_name
        Required field name.
    description
        Human-readable description used in error messages.

    Returns
    -------
    str
        The validated string field.

    Raises
    ------
    TypeError
        If the field is absent or is not a string.
    """
    value = config.get(field_name)

    if not isinstance(value, str):
        raise TypeError(f"{description} field {field_name!r} must be a string")

    return value


def require_string_sequence_field(
    *,
    config: Mapping[str, JSONValue],
    field_name: str,
    description: str,
) -> tuple[str, ...]:
    """Return a required sequence of strings from config.

    Parameters
    ----------
    config
        Mapping to read from.
    field_name
        Required field name.
    description
        Human-readable description used in error messages.

    Returns
    -------
    tuple[str, ...]
        The validated string sequence converted to an immutable tuple.

    Raises
    ------
    TypeError
        If the field is absent, is not a sequence, is a string, or contains
        non-string elements.
    """
    value = config.get(field_name)

    if value is None:
        raise TypeError(
            f"{description} field {field_name!r} must be a sequence of strings"
        )

    if isinstance(value, str):
        raise TypeError(
            f"{description} field {field_name!r} must be a sequence of strings"
        )

    if not isinstance(value, list):
        raise TypeError(
            f"{description} field {field_name!r} must be a sequence of strings"
        )

    result: list[str] = []

    for item in value:
        if not isinstance(item, str):
            raise TypeError(
                f"{description} field {field_name!r} must contain only strings"
            )

        result.append(item)

    return tuple(result)
