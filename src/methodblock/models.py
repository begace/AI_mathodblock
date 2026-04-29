"""Dataclass models for MethodBlock Registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MethodBlock:
    """A normalized view of a source MethodBlock."""

    id: str
    title: str
    summary: str
    version: str
    task_type: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    good_for: list[str] = field(default_factory=list)
    bad_for: list[str] = field(default_factory=list)
    forbidden_for: list[str] = field(default_factory=list)
    procedure: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    verification: list[str] = field(default_factory=list)
    contract_pattern: dict[str, Any] = field(default_factory=dict)
    examples: list[dict[str, Any]] = field(default_factory=list)
    model_notes: dict[str, Any] = field(default_factory=dict)
    lineage: dict[str, Any] = field(default_factory=dict)
    author: str | None = None
    created_by: dict[str, Any] | None = None
    license: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MethodBlock":
        """Build a MethodBlock dataclass from raw YAML data."""

        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            version=str(data["version"]),
            task_type=_text_list(data.get("task_type")),
            keywords=_text_list(data.get("keywords")),
            good_for=_text_list(data.get("good_for")),
            bad_for=_text_list(data.get("bad_for")),
            forbidden_for=_text_list(data.get("forbidden_for")),
            procedure=_text_list(data.get("procedure")),
            failure_modes=_text_list(data.get("failure_modes")),
            verification=_text_list(data.get("verification")),
            contract_pattern=_dict(data.get("contract_pattern")),
            examples=_dict_list(data.get("examples")),
            model_notes=_dict(data.get("model_notes")),
            lineage=_dict(data.get("lineage")),
            author=data.get("author"),
            created_by=data.get("created_by") if isinstance(data.get("created_by"), dict) else None,
            license=data.get("license"),
            tags=_text_list(data.get("tags")),
        )


@dataclass(frozen=True)
class ValidationReport:
    """Validation result for one source file."""

    path: str
    valid: bool
    errors: list[str] = field(default_factory=list)


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
