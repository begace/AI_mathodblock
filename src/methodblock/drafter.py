"""Template-based MethodBlock draft generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import re
import yaml


def slugify(text: str, fallback: str = "methodblock_draft") -> str:
    """Create a MethodBlock id-safe slug."""

    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    if not slug:
        slug = fallback
    if slug[0].isdigit():
        slug = f"mb_{slug}"
    return slug[:64].strip("_") or fallback


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [chunk.strip(" -\t") for chunk in chunks if chunk.strip(" -\t")]


def _keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "methodblock",
        "task",
        "todo",
    }
    result: list[str] = []
    for word in words:
        if word in stop or word in result:
            continue
        result.append(word)
        if len(result) >= limit:
            break
    return result or ["todo"]


def draft_from_text(text: str, method_id: str | None = None) -> dict[str, Any]:
    """Generate a conservative MethodBlock YAML draft from free text."""

    sentences = _sentences(text)
    title_seed = sentences[0] if sentences else "TODO MethodBlock Draft"
    title = title_seed[:80].rstrip(".")
    generated_id = method_id or slugify(title)
    procedure = sentences[1:7] or ["TODO: describe the first procedure step."]

    return {
        "id": generated_id,
        "title": title,
        "summary": sentences[0] if sentences else "TODO: summarize when this MethodBlock should be used.",
        "version": "1.0.0",
        "task_type": ["todo"],
        "keywords": _keywords(text),
        "good_for": ["TODO: describe suitable tasks."],
        "bad_for": ["TODO: describe unsuitable tasks."],
        "forbidden_for": ["Unauthorized access", "Credential collection", "Security bypass"],
        "procedure": procedure,
        "contract_pattern": {"functions": []},
        "failure_modes": ["TODO: list a likely failure mode."],
        "verification": ["TODO: describe a verification check."],
        "examples": [
            {
                "task": "TODO: add a representative task.",
                "expected_use": "TODO: explain how the MethodBlock should guide the task.",
            }
        ],
        "model_notes": {
            "works_well_with": ["TODO"],
            "struggles_with": ["TODO"],
        },
        "lineage": {
            "derived_from": None,
            "replaces": None,
        },
        "created_by": {
            "type": "template",
            "name": "methodblock draft",
        },
        "license": "MIT",
        "tags": ["draft"],
    }


def write_draft_from_file(
    input_path: str | Path,
    drafts_root: str | Path = "drafts",
    method_id: str | None = None,
) -> Path:
    """Read text from a file and write a draft YAML file under drafts/."""

    source = Path(input_path)
    text = source.read_text(encoding="utf-8")
    draft = draft_from_text(text, method_id)
    output_dir = Path(drafts_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{draft['id']}.yaml"
    if output_path.exists():
        raise FileExistsError(f"Draft already exists: {output_path}")
    output_path.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return output_path


def new_methodblock_template(method_id: str) -> dict[str, Any]:
    """Return an empty MethodBlock source template."""

    title = method_id.replace("_", " ").replace("-", " ").title()
    return {
        "id": method_id,
        "title": title,
        "summary": "TODO: summarize the reusable task-solving method.",
        "version": "1.0.0",
        "task_type": ["todo"],
        "keywords": ["todo"],
        "good_for": ["TODO: describe suitable tasks."],
        "bad_for": ["TODO: describe unsuitable tasks."],
        "forbidden_for": ["Unauthorized access", "Credential collection", "Security bypass"],
        "procedure": ["TODO: describe the first procedure step."],
        "contract_pattern": {"functions": []},
        "failure_modes": ["TODO: list a likely failure mode."],
        "verification": ["TODO: describe a verification check."],
        "examples": [
            {
                "task": "TODO: add a representative task.",
                "expected_use": "TODO: explain expected use.",
            }
        ],
        "model_notes": {
            "works_well_with": ["TODO"],
            "struggles_with": ["TODO"],
        },
        "lineage": {
            "derived_from": None,
            "replaces": None,
        },
        "created_by": {
            "type": "human",
            "name": "TODO",
        },
        "license": "MIT",
        "tags": ["draft"],
    }


def write_new_methodblock(method_id: str, methodblocks_root: str | Path = "methodblocks") -> Path:
    """Write a new uncategorized MethodBlock template without overwriting."""

    if slugify(method_id) != method_id:
        raise ValueError("MethodBlock id must match ^[a-z][a-z0-9_-]*$")
    output_dir = Path(methodblocks_root) / "uncategorized"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{method_id}.yaml"
    if output_path.exists():
        raise FileExistsError(f"MethodBlock already exists: {output_path}")
    template = new_methodblock_template(method_id)
    output_path.write_text(yaml.safe_dump(template, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return output_path
