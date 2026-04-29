import os
from pathlib import Path

from typer.testing import CliRunner

from methodblock.cli import app


runner = CliRunner()


def test_cli_validate_all_smoke():
    result = runner.invoke(app, ["validate-all"])

    assert result.exit_code == 0
    assert "Failed: 0" in result.output


def test_cli_prompt_json_smoke():
    result = runner.invoke(
        app,
        [
            "prompt",
            "excel_processor_basic",
            "--task",
            "Build a Python tool that merges duplicate SKUs in an Excel file",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"task"' in result.output
    assert "excel_processor_basic" in result.output


def test_cli_new_creates_template(tmp_path):
    cwd = Path.cwd()
    try:
        result = runner.invoke(app, ["--root", str(tmp_path), "init"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["--root", str(tmp_path), "new", "payment_system_basic"])

        assert result.exit_code == 0
        assert (Path(tmp_path) / "methodblocks" / "uncategorized" / "payment_system_basic.yaml").exists()
    finally:
        os.chdir(cwd)


def test_cli_draft_creates_yaml(tmp_path):
    cwd = Path.cwd()
    try:
        source = Path(tmp_path) / "notes.txt"
        source.write_text(
            "Excel cleanup workflow. Inspect input sheets. Normalize columns. Validate duplicate rows.",
            encoding="utf-8",
        )
        result = runner.invoke(app, ["--root", str(tmp_path), "init"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["--root", str(tmp_path), "draft", "--from-text", str(source), "--id", "excel_cleanup_draft"])

        assert result.exit_code == 0
        assert (Path(tmp_path) / "drafts" / "excel_cleanup_draft.yaml").exists()
    finally:
        os.chdir(cwd)
