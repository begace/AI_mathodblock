"""Build LLM prompts from a task and a compact MethodBlock."""

from __future__ import annotations


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
