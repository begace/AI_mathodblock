"""Path helpers and repository bootstrap support."""

from __future__ import annotations

from pathlib import Path


DEFAULT_DIRECTORIES = [
    "methodblocks/coding",
    "methodblocks/automation",
    "methodblocks/writing",
    "methodblocks/uncategorized",
    "compiled",
    "schema",
    "examples/tasks",
    "examples/prompts",
    "examples/outputs",
    "drafts",
    "src/methodblock",
    "tests",
    ".github/workflows",
]


def ensure_repository_layout(root: str | Path = ".") -> tuple[list[Path], list[Path]]:
    """Create the v1.0 repository directory layout without overwriting files."""

    root_path = Path(root)
    created: list[Path] = []
    existing: list[Path] = []
    for directory in DEFAULT_DIRECTORIES:
        path = root_path / directory
        if path.exists():
            existing.append(path)
            continue
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)

    gitkeep = root_path / "drafts" / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
        created.append(gitkeep)
    else:
        existing.append(gitkeep)

    return created, existing


def category_for_source(path: str | Path, methodblocks_root: str | Path = "methodblocks") -> str:
    """Return the category directory for a source MethodBlock."""

    source = Path(path)
    root = Path(methodblocks_root)
    try:
        relative = source.relative_to(root)
    except ValueError:
        return "uncategorized"
    if relative.parent == Path("."):
        return "uncategorized"
    return relative.parts[0]
