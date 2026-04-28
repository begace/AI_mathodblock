"""Compile source MethodBlocks into AI-optimized artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json
import re


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_text_list(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if str(item).strip()]


def _compact_join(items: list[str], fallback: str = "none") -> str:
    return ", ".join(items) if items else fallback


def step_id(step: str, index: int) -> str:
    """Create a stable graph node id from a procedure step."""

    normalized = step.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = normalized.strip("_")
    if not normalized:
        normalized = f"step_{index}"
    if normalized[0].isdigit():
        normalized = f"step_{normalized}"
    return normalized[:64].strip("_") or f"step_{index}"


def infer_node_type(step: str) -> str:
    """Infer a compact node type from a human procedure step."""

    lowered = step.lower()
    if any(token in lowered for token in ("test", "sample", "테스트")):
        return "test"
    if any(token in lowered for token in ("validate", "verify", "check", "검증", "확인")):
        return "verify"
    if any(token in lowered for token in ("load", "read", "inspect", "입력", "읽")):
        return "inspect"
    if any(token in lowered for token in ("define", "schema", "contract", "정의")):
        return "schema"
    if any(token in lowered for token in ("save", "export", "write", "저장", "출력")):
        return "output"
    return "transform"


def _format_params(params: Any) -> str:
    if isinstance(params, dict):
        return ", ".join(f"{name}: {kind}" for name, kind in params.items())
    if params is None:
        return ""
    return str(params)


def _format_output(output: Any) -> str:
    if isinstance(output, dict):
        if len(output) == 1:
            return str(next(iter(output.values())))
        return "{" + ", ".join(f"{name}: {kind}" for name, kind in output.items()) + "}"
    if output is None:
        return "void"
    return str(output)


def _contract_lines(block: dict[str, Any]) -> list[str]:
    functions = block.get("contract_pattern", {}).get("functions", [])
    if not isinstance(functions, list):
        return []

    lines: list[str] = []
    for function in functions:
        if not isinstance(function, dict) or not function.get("name"):
            continue
        name = function["name"]
        params = _format_params(function.get("input"))
        output = _format_output(function.get("output"))
        lines.append(f"{name}({params}) -> {output}")
    return lines


def build_compact_markdown(block: dict[str, Any]) -> str:
    """Build the compact Markdown representation for one MethodBlock."""

    procedure = _as_text_list(block.get("procedure"))
    flow = " -> ".join(step_id(step, index) for index, step in enumerate(procedure, 1))
    contracts = _contract_lines(block)
    lines = [
        f"# MB: {block['id']}",
        "",
        f"TITLE: {block.get('title', block['id'])}",
        f"USE WHEN: {_compact_join(_as_text_list(block.get('good_for') or block.get('keywords')))}.",
        f"AVOID: {_compact_join(_as_text_list(block.get('bad_for')))}.",
        f"FORBID: {_compact_join(_as_text_list(block.get('forbidden_for')))}.",
        "",
        "FLOW:",
        flow or "none",
        "",
        "CONTRACTS:",
    ]
    lines.extend(contracts or ["none"])
    lines.extend(
        [
            "",
            "FAIL:",
            " | ".join(_as_text_list(block.get("failure_modes"))) or "none",
            "",
            "VERIFY:",
            " | ".join(_as_text_list(block.get("verification"))) or "none",
            "",
        ]
    )
    return "\n".join(lines)


def build_graph(block: dict[str, Any]) -> dict[str, Any]:
    """Build the graph JSON representation for one MethodBlock."""

    procedure = _as_text_list(block.get("procedure"))
    nodes = [
        {
            "id": step_id(step, index),
            "type": infer_node_type(step),
            "label": step,
        }
        for index, step in enumerate(procedure, 1)
    ]
    edges = [[nodes[index]["id"], nodes[index + 1]["id"]] for index in range(len(nodes) - 1)]
    functions = block.get("contract_pattern", {}).get("functions", [])
    if not isinstance(functions, list):
        functions = []

    return {
        "id": block["id"],
        "nodes": nodes,
        "edges": edges,
        "contracts": [function for function in functions if isinstance(function, dict)],
        "failure_modes": _as_text_list(block.get("failure_modes")),
        "verification": _as_text_list(block.get("verification")),
    }


def summary_compact(summary: str, max_chars: int = 220) -> str:
    """Return a single-line compact summary."""

    one_line = " ".join(summary.split())
    if len(one_line) <= max_chars:
        return one_line
    return one_line[: max_chars - 3].rstrip() + "..."


def compiled_paths(source_path: str | Path, methodblocks_root: str | Path = "methodblocks") -> dict[str, Path]:
    """Return output paths for the compiled artifacts of a source file."""

    source = Path(source_path)
    root = Path(methodblocks_root)
    try:
        relative = source.relative_to(root)
    except ValueError:
        relative = Path(source.name)

    output_dir = Path("compiled") / relative.parent
    stem = source.stem
    return {
        "compact": output_dir / f"{stem}.compact.md",
        "graph": output_dir / f"{stem}.graph.json",
        "index": output_dir / f"{stem}.index.json",
    }


def build_index(
    block: dict[str, Any],
    source_path: str | Path,
    paths: dict[str, Path],
) -> dict[str, Any]:
    """Build the index JSON representation for one MethodBlock."""

    return {
        "id": block["id"],
        "title": block.get("title", block["id"]),
        "keywords": _as_text_list(block.get("keywords")),
        "task_type": _as_text_list(block.get("task_type")),
        "summary_compact": summary_compact(str(block.get("summary", ""))),
        "paths": {
            "source": Path(source_path).as_posix(),
            "compact": paths["compact"].as_posix(),
            "graph": paths["graph"].as_posix(),
        },
        "version": str(block.get("version", "")),
    }


def compile_methodblock(
    block: dict[str, Any],
    source_path: str | Path,
    methodblocks_root: str | Path = "methodblocks",
) -> dict[str, Any]:
    """Compile one source MethodBlock into compact, graph, and index data."""

    paths = compiled_paths(source_path, methodblocks_root)
    graph = build_graph(block)
    return {
        "compact": build_compact_markdown(block),
        "graph": graph,
        "index": build_index(block, source_path, paths),
        "paths": paths,
    }


def write_compiled(
    block: dict[str, Any],
    source_path: str | Path,
    methodblocks_root: str | Path = "methodblocks",
) -> dict[str, Path]:
    """Compile one MethodBlock and write artifacts to compiled/."""

    artifact = compile_methodblock(block, source_path, methodblocks_root)
    paths: dict[str, Path] = artifact["paths"]
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    paths["compact"].write_text(artifact["compact"], encoding="utf-8")
    paths["graph"].write_text(json.dumps(artifact["graph"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["index"].write_text(json.dumps(artifact["index"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return paths
