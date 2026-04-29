"""Typer command line interface for MethodBlock Registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json
import os
import typer
import yaml
from rich.console import Console
from rich.table import Table

from .compiler import build_compact_markdown, build_graph, compiled_complete, write_compiled
from .drafter import write_draft_from_file, write_new_methodblock
from .errors import DuplicateMethodBlockIdError
from .loader import MethodBlockLoadError, discover_methodblocks, ensure_unique_ids, find_by_id, load_all_with_paths, load_yaml
from .paths import category_for_source, ensure_repository_layout
from .prompt_builder import build_prompt_formatted
from .search import search_methodblocks
from .validator import DEFAULT_SCHEMA_PATH, format_error, load_schema, iter_errors, validate_all


console = Console(markup=False)
err_console = Console(stderr=True, markup=False)
app = typer.Typer(help="MethodBlock Registry CLI")


@dataclass
class CliConfig:
    """Runtime CLI configuration."""

    root: Path
    methodblocks_root: Path
    schema: Path


def _config(ctx: typer.Context) -> CliConfig:
    if not isinstance(ctx.obj, CliConfig):
        raise typer.BadParameter("CLI context was not initialized.")
    return ctx.obj


@app.callback()
def callback(
    ctx: typer.Context,
    root: Path = typer.Option(Path("."), "--root", help="Project root directory."),
    methodblocks_root: Path = typer.Option(Path("methodblocks"), "--methodblocks-root", help="MethodBlock source root."),
    schema: Path = typer.Option(DEFAULT_SCHEMA_PATH, "--schema", help="MethodBlock JSON Schema path."),
) -> None:
    """Local-first procedural memory toolkit for AI agents."""

    root = root.resolve()
    if not root.exists():
        raise typer.BadParameter(f"Project root not found: {root}")
    os.chdir(root)
    ctx.obj = CliConfig(root=root, methodblocks_root=methodblocks_root, schema=schema)


def _load_validated(path: Path, schema: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        block = load_yaml(path)
    except MethodBlockLoadError as exc:
        return None, [str(exc)]

    errors = [format_error(error) for error in iter_errors(block, schema)]
    return block, errors


def _print_errors(path: Path | str, errors: list[str]) -> None:
    for error in errors:
        err_console.print(f"ERROR: {path}: {error}")


@app.command("init")
def init_command(ctx: typer.Context) -> None:
    """Create the v1.0 repository directory layout without overwriting files."""

    config = _config(ctx)
    created, existing = ensure_repository_layout(config.root)
    if created:
        console.print(f"Created {len(created)} paths:")
        for path in created:
            console.print(f"  {path.relative_to(config.root)}")
    if existing:
        console.print(f"Already present: {len(existing)} paths")


@app.command("list")
def list_command(ctx: typer.Context) -> None:
    """List all source MethodBlocks."""

    config = _config(ctx)
    paths = discover_methodblocks(config.methodblocks_root)
    if not paths:
        console.print("No MethodBlocks found.")
        return

    table = Table("id", "title", "version", "category", "task_type", "source path", "compiled")
    for path in paths:
        block = load_yaml(path)
        category = category_for_source(path, config.methodblocks_root)
        table.add_row(
            str(block.get("id", "<missing id>")),
            str(block.get("title", "")),
            str(block.get("version", "")),
            category,
            ", ".join(str(item) for item in block.get("task_type", []) or []),
            path.as_posix(),
            "yes" if compiled_complete(path, config.methodblocks_root) else "no",
        )
    console.print(table)


@app.command("show")
def show_command(
    ctx: typer.Context,
    method_id: str = typer.Argument(..., help="MethodBlock id."),
    source: bool = typer.Option(False, "--source", help="Show source YAML."),
    compact: bool = typer.Option(False, "--compact", help="Show compact compiled form."),
    graph: bool = typer.Option(False, "--graph", help="Show graph JSON."),
) -> None:
    """Show a MethodBlock summary, source, compact form, or graph."""

    config = _config(ctx)
    try:
        path, block = find_by_id(config.methodblocks_root, method_id)
    except (MethodBlockLoadError, DuplicateMethodBlockIdError) as exc:
        err_console.print(f"ERROR: {exc}")
        raise typer.Exit(1) from exc

    selected = sum(1 for value in (source, compact, graph) if value)
    if selected > 1:
        err_console.print("ERROR: choose only one of --source, --compact, or --graph")
        raise typer.Exit(2)

    if source:
        typer.echo(yaml.safe_dump(block, allow_unicode=True, sort_keys=False).strip())
        return
    if compact:
        typer.echo(build_compact_markdown(block))
        return
    if graph:
        typer.echo(json.dumps(build_graph(block), ensure_ascii=False, indent=2))
        return

    console.print(f"id: {block.get('id')}")
    console.print(f"title: {block.get('title')}")
    console.print(f"version: {block.get('version')}")
    console.print(f"category: {category_for_source(path, config.methodblocks_root)}")
    console.print(f"task_type: {', '.join(block.get('task_type', []) or [])}")
    console.print(f"source: {path.as_posix()}")
    console.print(f"summary: {block.get('summary')}")


@app.command("validate")
def validate_command(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Source YAML path."),
) -> None:
    """Validate one source MethodBlock YAML file."""

    config = _config(ctx)
    schema = load_schema(config.schema)
    block, errors = _load_validated(path, schema)
    if block is None or errors:
        _print_errors(path, errors)
        raise typer.Exit(1)
    console.print(f"OK: {path.as_posix()} is valid.")


@app.command("validate-all")
def validate_all_command(ctx: typer.Context) -> None:
    """Validate all MethodBlocks under methodblocks/."""

    config = _config(ctx)
    reports = validate_all(config.methodblocks_root, config.schema)
    if not reports:
        console.print("No MethodBlocks found.")
        return

    failed = 0
    for report in reports:
        if report.valid:
            console.print(f"OK: {report.path} is valid.")
            continue
        failed += 1
        _print_errors(report.path, report.errors)

    console.print(f"Validated: {len(reports) - failed}")
    console.print(f"Failed: {failed}")
    if failed:
        raise typer.Exit(1)


@app.command("compile")
def compile_command(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Source YAML path."),
) -> None:
    """Compile one source MethodBlock into compact, graph, and index artifacts."""

    config = _config(ctx)
    schema = load_schema(config.schema)
    block, errors = _load_validated(path, schema)
    if block is None or errors:
        _print_errors(path, errors)
        raise typer.Exit(1)

    output_paths = write_compiled(block, path, config.methodblocks_root)
    for artifact_path in output_paths.values():
        console.print(artifact_path.as_posix())


@app.command("compile-all")
def compile_all_command(ctx: typer.Context) -> None:
    """Compile all valid MethodBlocks."""

    config = _config(ctx)
    schema = load_schema(config.schema)
    paths = discover_methodblocks(config.methodblocks_root)
    if not paths:
        console.print("No MethodBlocks found.")
        return

    try:
        ensure_unique_ids(config.methodblocks_root)
        blocks = load_all_with_paths(config.methodblocks_root)
    except DuplicateMethodBlockIdError as exc:
        err_console.print(f"ERROR: {exc}")
        raise typer.Exit(1) from exc

    compiled = 0
    failed = 0
    skipped = 0
    for path, block in blocks:
        errors = [format_error(error) for error in iter_errors(block, schema)]
        if errors:
            failed += 1
            skipped += 1
            _print_errors(path, errors)
            continue
        output_paths = write_compiled(block, path, config.methodblocks_root)
        compiled += 1
        console.print(f"compiled: {path.as_posix()} -> {output_paths['compact'].as_posix()}")

    console.print(f"Compiled: {compiled}")
    console.print(f"Skipped: {skipped}")
    console.print(f"Failed: {failed}")
    if failed:
        raise typer.Exit(1)


@app.command("search")
def search_command(
    ctx: typer.Context,
    query: list[str] = typer.Argument(..., help="Search query."),
) -> None:
    """Search MethodBlocks with local keyword scoring."""

    config = _config(ctx)
    task = " ".join(query)
    blocks = [(path.as_posix(), block) for path, block in load_all_with_paths(config.methodblocks_root)]
    results = search_methodblocks(blocks, task)
    if not results:
        console.print("No matching MethodBlocks found.")
        return

    console.print(f"Found {len(results)} MethodBlocks:\n")
    for index, (score, path, block) in enumerate(results, 1):
        console.print(f"{index}. {block.get('id')}")
        console.print(f"   score: {score:.2f}")
        console.print(f"   title: {block.get('title', '')}")
        console.print(f"   good_for: {', '.join(block.get('good_for', []) or [])}")
        console.print(f"   source: {path}")


@app.command("prompt")
def prompt_command(
    ctx: typer.Context,
    method_id: str = typer.Argument(..., help="MethodBlock id."),
    task: str = typer.Option(..., "--task", help="User task to combine with the MethodBlock."),
    output_format: str = typer.Option("markdown", "--format", help="markdown, plain, or json."),
    output: Path | None = typer.Option(None, "--output", help="Optional output file."),
) -> None:
    """Build an LLM-ready prompt from a task and one MethodBlock."""

    config = _config(ctx)
    if output_format not in {"markdown", "plain", "json"}:
        err_console.print("ERROR: --format must be markdown, plain, or json")
        raise typer.Exit(2)
    try:
        _, block = find_by_id(config.methodblocks_root, method_id)
    except (MethodBlockLoadError, DuplicateMethodBlockIdError) as exc:
        err_console.print(f"ERROR: {exc}")
        raise typer.Exit(1) from exc

    compact = build_compact_markdown(block)
    prompt = build_prompt_formatted(task, compact, output_format=output_format)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(prompt + "\n", encoding="utf-8")
        console.print(output.as_posix())
        return
    typer.echo(prompt)


@app.command("draft")
def draft_command(
    from_text: Path = typer.Option(..., "--from-text", help="Text file to draft from."),
    method_id: str | None = typer.Option(None, "--id", help="Optional MethodBlock id."),
) -> None:
    """Create a template-based MethodBlock draft from a text file."""

    try:
        output_path = write_draft_from_file(from_text, method_id=method_id)
    except (OSError, ValueError) as exc:
        err_console.print(f"ERROR: {exc}")
        raise typer.Exit(1) from exc
    console.print(output_path.as_posix())


@app.command("new")
def new_command(
    ctx: typer.Context,
    method_id: str = typer.Argument(..., help="New MethodBlock id."),
) -> None:
    """Create a new uncategorized MethodBlock YAML template."""

    config = _config(ctx)
    try:
        output_path = write_new_methodblock(method_id, config.methodblocks_root)
    except (OSError, ValueError) as exc:
        err_console.print(f"ERROR: {exc}")
        raise typer.Exit(1) from exc
    console.print(output_path.as_posix())


def main() -> None:
    """Entrypoint for python -m methodblock.cli."""

    app()


if __name__ == "__main__":
    main()
