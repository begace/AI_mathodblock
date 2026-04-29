"""Load MethodBlock source YAML files from disk."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .errors import DuplicateMethodBlockIdError


class MethodBlockLoadError(ValueError):
    """Raised when a MethodBlock source file cannot be loaded."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a MethodBlock YAML file as a dictionary."""

    source_path = Path(path)
    try:
        with source_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise MethodBlockLoadError(f"Could not read {source_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise MethodBlockLoadError(f"Invalid YAML in {source_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise MethodBlockLoadError(f"{source_path} must contain a YAML mapping.")

    return data


def discover_methodblocks(root: str | Path = "methodblocks") -> list[Path]:
    """Return all source MethodBlock YAML files under a root directory."""

    root_path = Path(root)
    if not root_path.exists():
        return []

    paths: list[Path] = []
    for pattern in ("*.yaml", "*.yml"):
        paths.extend(root_path.rglob(pattern))
    return sorted(path for path in paths if path.is_file())


def load_many(paths: list[str | Path]) -> list[dict[str, Any]]:
    """Load multiple MethodBlock files."""

    return [load_yaml(path) for path in paths]


def load_all_with_paths(root: str | Path = "methodblocks") -> list[tuple[Path, dict[str, Any]]]:
    """Load all MethodBlocks under a root with their source paths."""

    return [(path, load_yaml(path)) for path in discover_methodblocks(root)]


def duplicate_ids(root: str | Path = "methodblocks") -> dict[str, list[str]]:
    """Return duplicate MethodBlock ids and their source paths."""

    seen: dict[str, list[str]] = {}
    for path, data in load_all_with_paths(root):
        method_id = data.get("id")
        if not isinstance(method_id, str) or not method_id:
            continue
        seen.setdefault(method_id, []).append(path.as_posix())
    return {method_id: paths for method_id, paths in seen.items() if len(paths) > 1}


def ensure_unique_ids(root: str | Path = "methodblocks") -> None:
    """Raise when duplicate MethodBlock ids are present."""

    duplicates = duplicate_ids(root)
    if duplicates:
        raise DuplicateMethodBlockIdError(duplicates)


def find_by_id(methodblocks_root: str | Path, methodblock_id: str) -> tuple[Path, dict[str, Any]]:
    """Find and load a MethodBlock by id."""

    ensure_unique_ids(methodblocks_root)
    for path in discover_methodblocks(methodblocks_root):
        data = load_yaml(path)
        if data.get("id") == methodblock_id:
            return path, data

    raise MethodBlockLoadError(f"MethodBlock not found: {methodblock_id}")
