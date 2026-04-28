"""Simple keyword scoring search for MethodBlocks."""

from __future__ import annotations

from typing import Any

import re


def tokenize(text: str) -> set[str]:
    """Tokenize ASCII-ish search text into lowercase terms."""

    return set(re.findall(r"[a-z0-9_+-]+", text.lower()))


def _contains_phrase(query: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    return bool(phrase and phrase in query)


def score_methodblock(block: dict[str, Any], task: str) -> int:
    """Score one MethodBlock against a task string."""

    query = task.lower()
    query_tokens = tokenize(task)
    score = 0

    for keyword in block.get("keywords", []) or []:
        if _contains_phrase(query, str(keyword)):
            score += 3

    for task_type in block.get("task_type", []) or []:
        if _contains_phrase(query, str(task_type)):
            score += 2

    title_tokens = tokenize(str(block.get("title", "")))
    summary_tokens = tokenize(str(block.get("summary", "")))
    score += len(query_tokens & title_tokens)
    score += len(query_tokens & summary_tokens)

    return score


def search_methodblocks(blocks: list[tuple[str, dict[str, Any]]], task: str) -> list[tuple[int, str, dict[str, Any]]]:
    """Return MethodBlocks sorted by descending score."""

    scored = [(score_methodblock(block, task), path, block) for path, block in blocks]
    scored = [item for item in scored if item[0] > 0]
    return sorted(scored, key=lambda item: (-item[0], item[2].get("id", "")))
