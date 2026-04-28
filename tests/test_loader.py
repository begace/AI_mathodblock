from methodblock.loader import discover_methodblocks, load_yaml


def test_discover_methodblocks_finds_samples():
    paths = discover_methodblocks("methodblocks")

    assert len(paths) >= 5
    assert any(path.name == "excel_processor.yaml" for path in paths)


def test_load_yaml_returns_mapping():
    block = load_yaml("methodblocks/coding/excel_processor.yaml")

    assert block["id"] == "excel_processor_basic"
    assert block["procedure"]
