"""Validate MethodBlock source data with JSON Schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .loader import load_yaml


DEFAULT_SCHEMA_PATH = Path("schema/methodblock.schema.json")


def load_schema(path: str | Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    """Load a JSON Schema document."""

    schema_path = Path(path)
    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if not isinstance(schema, dict):
        raise ValueError(f"{schema_path} must contain a JSON object.")
    return schema


def iter_errors(data: dict[str, Any], schema: dict[str, Any]) -> list[ValidationError]:
    """Return validation errors sorted by field path."""

    validator = Draft202012Validator(schema)
    return sorted(validator.iter_errors(data), key=lambda error: list(error.path))


def validate_data(data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate MethodBlock data or raise the first validation error."""

    errors = iter_errors(data, schema)
    if errors:
        raise errors[0]


def validate_file(
    path: str | Path,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> tuple[dict[str, Any], list[ValidationError]]:
    """Load and validate a MethodBlock source file."""

    data = load_yaml(path)
    schema = load_schema(schema_path)
    return data, iter_errors(data, schema)


def format_error(error: ValidationError) -> str:
    """Format a JSON Schema error for CLI output."""

    field = ".".join(str(part) for part in error.path) or "<root>"
    return f"{field}: {error.message}"
