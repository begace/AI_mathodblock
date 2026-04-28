from methodblock.prompt_builder import build_prompt


def test_build_prompt_combines_task_methodblock_and_instruction():
    prompt = build_prompt("Build a CLI.", "# MB: cli_tool_basic\nFLOW:\nparse -> run")

    assert "TASK:\nBuild a CLI." in prompt
    assert "METHODBLOCK:\n# MB: cli_tool_basic" in prompt
    assert "INSTRUCTION:" in prompt
