import json

from methodblock.compiler import compile_methodblock, step_id, write_compiled
from methodblock.loader import load_yaml


def test_step_id_falls_back_for_non_ascii_text():
    assert step_id("열 이름을 정규화한다", 3) == "step_3"


def test_compile_methodblock_builds_all_artifacts():
    source = "methodblocks/coding/excel_processor.yaml"
    block = load_yaml(source)

    artifact = compile_methodblock(block, source)

    assert "# MB: excel_processor_basic" in artifact["compact"]
    assert artifact["graph"]["nodes"][0]["id"] == "inspect_the_input_file_format_and_sheet_names"
    assert artifact["index"]["paths"]["compact"] == "compiled/coding/excel_processor.compact.md"


def test_write_compiled_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    block = {
        "id": "mini_block",
        "title": "Mini Block",
        "summary": "Tiny test MethodBlock.",
        "procedure": ["Inspect input.", "Export output."],
    }

    paths = write_compiled(block, "methodblocks/coding/mini.yaml")

    assert paths["compact"].exists()
    assert paths["graph"].exists()
    assert paths["index"].exists()
    graph = json.loads(paths["graph"].read_text(encoding="utf-8"))
    assert graph["edges"] == [["inspect_input", "export_output"]]
