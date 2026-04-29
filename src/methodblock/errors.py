"""Shared exceptions for MethodBlock Registry."""

from __future__ import annotations


class MethodBlockError(Exception):
    """Base error for MethodBlock operations."""


class DuplicateMethodBlockIdError(MethodBlockError):
    """Raised when multiple source files declare the same MethodBlock id."""

    def __init__(self, duplicates: dict[str, list[str]]) -> None:
        self.duplicates = duplicates
        details = "; ".join(f"{method_id}: {', '.join(paths)}" for method_id, paths in duplicates.items())
        super().__init__(f"Duplicate MethodBlock ids found: {details}")
