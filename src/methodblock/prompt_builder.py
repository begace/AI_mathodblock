"""Build LLM prompts from a task and a compact MethodBlock."""

from __future__ import annotations

import json


DEFAULT_INSTRUCTION = """Use the MethodBlock as procedural guidance.
First produce a function contract plan.
Then implement each function according to the contracts.
Do not add unrelated features.
Include tests for the listed failure modes.
If the MethodBlock does not fit the task, explicitly state what is being ignored."""


def build_prompt(task: str, compact_methodblock: str, instruction: str = DEFAULT_INSTRUCTION) -> str:
    """Combine a task and compact MethodBlock into a prompt."""

    return "\n\n".join(
        [
            "TASK:\n" + task.strip(),
            "METHODBLOCK:\n" + compact_methodblock.strip(),
            "INSTRUCTION:\n" + instruction.strip(),
        ]
    )


def build_plain_prompt(task: str, compact_methodblock: str, instruction: str = DEFAULT_INSTRUCTION) -> str:
    """Build a plain text prompt without Markdown heading syntax."""

    return build_prompt(task, compact_methodblock, instruction)


def build_json_prompt(task: str, compact_methodblock: str, instruction: str = DEFAULT_INSTRUCTION) -> str:
    """Build a JSON prompt payload."""

    payload = {
        "task": task.strip(),
        "methodblock": compact_methodblock.strip(),
        "instruction": instruction.strip(),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_prompt_formatted(
    task: str,
    compact_methodblock: str,
    output_format: str = "markdown",
    instruction: str = DEFAULT_INSTRUCTION,
) -> str:
    """Build a prompt in markdown, plain, or json format."""

    if output_format == "markdown":
        return build_prompt(task, compact_methodblock, instruction)
    if output_format == "plain":
        return build_plain_prompt(task, compact_methodblock, instruction)
    if output_format == "json":
        return build_json_prompt(task, compact_methodblock, instruction)
    raise ValueError(f"Unsupported prompt format: {output_format}")
