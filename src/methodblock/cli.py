"""Command line interface for MethodBlock Registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import argparse
import os
import sys
import yaml

from .compiler import build_compact_markdown, write_compiled
from .loader import MethodBlockLoadError, discover_methodblocks, find_by_id, load_yaml
from .prompt_builder import build_prompt
from .search import search_methodblocks
from .validator import DEFAULT_SCHEMA_PATH, format_error, load_schema, iter_errors


def _load_validated(path: Path, schema: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        block = load_yaml(path)
    except MethodBlockLoadError as exc:
        return None, [str(exc)]

    errors = iter_errors(block, schema)
    if errors:
        return block, [format_error(error) for error in errors]
    return block, []


def _load_all(methodblocks_root: Path) -> list[tuple[str, dict[str, Any]]]:
    blocks: list[tuple[str, dict[str, Any]]] = []
    for path in discover_methodblocks(methodblocks_root):
        blocks.append((path.as_posix(), load_yaml(path)))
    return blocks


def cmd_list(args: argparse.Namespace) -> int:
    paths = discover_methodblocks(args.methodblocks_root)
    if not paths:
        print("No MethodBlocks found.")
        return 0

    for path in paths:
        block = load_yaml(path)
        version = block.get("version", "")
        print(f"{block.get('id', '<missing id>')}\t{version}\t{block.get('title', '')}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    try:
        _, block = find_by_id(args.methodblocks_root, args.id)
    except MethodBlockLoadError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(yaml.safe_dump(block, allow_unicode=True, sort_keys=False).strip())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    task = " ".join(args.task)
    results = search_methodblocks(_load_all(args.methodblocks_root), task)
    if not results:
        print("No matching MethodBlocks found.")
        return 0

    for score, path, block in results:
        print(f"{score}\t{block.get('id')}\t{block.get('title', '')}\t{path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    block, errors = _load_validated(Path(args.path), schema)
    if block is None or errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"valid: {args.path}")
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    path = Path(args.path)
    block, errors = _load_validated(path, schema)
    if block is None or errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    output_paths = write_compiled(block, path, args.methodblocks_root)
    for artifact_path in output_paths.values():
        print(artifact_path.as_posix())
    return 0


def cmd_compile_all(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    paths = discover_methodblocks(args.methodblocks_root)
    if not paths:
        print("No MethodBlocks found.")
        return 0

    had_error = False
    for path in paths:
        block, errors = _load_validated(path, schema)
        if block is None or errors:
            had_error = True
            for error in errors:
                print(f"{path}: {error}", file=sys.stderr)
            continue

        output_paths = write_compiled(block, path, args.methodblocks_root)
        print(f"compiled: {path.as_posix()} -> {output_paths['compact'].as_posix()}")

    return 1 if had_error else 0


def cmd_prompt(args: argparse.Namespace) -> int:
    try:
        path, block = find_by_id(args.methodblocks_root, args.id)
    except MethodBlockLoadError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    compact = build_compact_markdown(block)
    print(build_prompt(args.task, compact))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="methodblock", description="MethodBlock Registry CLI")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--methodblocks-root", default=Path("methodblocks"), type=Path)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA_PATH, type=Path)

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List MethodBlocks")
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Show a MethodBlock source YAML")
    show_parser.add_argument("id")
    show_parser.set_defaults(func=cmd_show)

    search_parser = subparsers.add_parser("search", help="Search MethodBlocks for a task")
    search_parser.add_argument("task", nargs="+")
    search_parser.set_defaults(func=cmd_search)

    validate_parser = subparsers.add_parser("validate", help="Validate a MethodBlock YAML file")
    validate_parser.add_argument("path")
    validate_parser.set_defaults(func=cmd_validate)

    compile_parser = subparsers.add_parser("compile", help="Compile one MethodBlock")
    compile_parser.add_argument("path")
    compile_parser.set_defaults(func=cmd_compile)

    compile_all_parser = subparsers.add_parser("compile-all", help="Compile all MethodBlocks")
    compile_all_parser.set_defaults(func=cmd_compile_all)

    prompt_parser = subparsers.add_parser("prompt", help="Build a task prompt from a MethodBlock")
    prompt_parser.add_argument("id")
    prompt_parser.add_argument("--task", required=True)
    prompt_parser.set_defaults(func=cmd_prompt)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Project root not found: {root}", file=sys.stderr)
        return 1

    os.chdir(root)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
