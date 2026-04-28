from methodblock.loader import load_yaml
from methodblock.validator import iter_errors, load_schema


def test_sample_methodblock_is_valid():
    schema = load_schema("schema/methodblock.schema.json")
    block = load_yaml("methodblocks/coding/excel_processor.yaml")

    assert iter_errors(block, schema) == []


def test_missing_required_field_is_invalid():
    schema = load_schema("schema/methodblock.schema.json")
    block = {
        "id": "missing_summary",
        "title": "Missing Summary",
        "procedure": ["Do one thing."],
    }

    errors = iter_errors(block, schema)

    assert any(error.validator == "required" for error in errors)
