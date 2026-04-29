from methodblock.loader import load_yaml
from methodblock.search import score_methodblock, search_methodblocks


def test_score_methodblock_prefers_matching_keywords():
    block = load_yaml("methodblocks/coding/excel_processor.yaml")

    score = score_methodblock(block, "clean duplicate SKUs in an Excel xlsx file")

    assert 0.5 <= score <= 1.0


def test_search_methodblocks_returns_sorted_matches():
    excel = load_yaml("methodblocks/coding/excel_processor.yaml")
    cli = load_yaml("methodblocks/coding/cli_tool.yaml")

    results = search_methodblocks(
        [
            ("methodblocks/coding/cli_tool.yaml", cli),
            ("methodblocks/coding/excel_processor.yaml", excel),
        ],
        "build an xlsx duplicate cleanup utility",
    )

    assert results[0][2]["id"] == "excel_processor_basic"
