"""Validate MethodBlock source data with JSON Schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .loader import discover_methodblocks, duplicate_ids, load_yaml
from .models import ValidationReport


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


def validate_all(
    methodblocks_root: str | Path = "methodblocks",
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> list[ValidationReport]:
    """Validate every MethodBlock source file and include duplicate-id errors."""

    schema = load_schema(schema_path)
    reports: list[ValidationReport] = []
    for path in discover_methodblocks(methodblocks_root):
        try:
            data = load_yaml(path)
            errors = [format_error(error) for error in iter_errors(data, schema)]
        except Exception as exc:
            errors = [str(exc)]
        reports.append(ValidationReport(path=path.as_posix(), valid=not errors, errors=errors))

    duplicates = duplicate_ids(methodblocks_root)
    if duplicates:
        duplicate_paths = {path for paths in duplicates.values() for path in paths}
        for report in reports:
            if report.path in duplicate_paths:
                ids = [method_id for method_id, paths in duplicates.items() if report.path in paths]
                report.errors.append(f"duplicate id: {', '.join(ids)}")
                object.__setattr__(report, "valid", False)
    return reports


def format_error(error: ValidationError) -> str:
    """Format a JSON Schema error for CLI output."""

    field = ".".join(str(part) for part in error.path) or "<root>"
    return f"{field}: {error.message}"
