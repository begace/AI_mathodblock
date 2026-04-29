"""Simple keyword scoring search for MethodBlocks."""

from __future__ import annotations

from typing import Any

import re


def tokenize(text: str) -> set[str]:
    """Tokenize search text into lowercase terms, including Korean words."""

    return set(re.findall(r"[a-z0-9가-힣_+-]+", text.lower()))


def _contains_phrase(query: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    return bool(phrase and phrase in query)


def _field_items(block: dict[str, Any], field: str) -> list[str]:
    value = block.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def raw_score_methodblock(block: dict[str, Any], task: str) -> int:
    """Return an explainable local-search score for one MethodBlock."""

    query = task.lower()
    query_tokens = tokenize(task)
    score = 0

    if _contains_phrase(query, str(block.get("id", ""))):
        score += 4

    for keyword in _field_items(block, "keywords"):
        if _contains_phrase(query, str(keyword)):
            score += 3

    for task_type in _field_items(block, "task_type"):
        if _contains_phrase(query, str(task_type)):
            score += 2

    for good_for in _field_items(block, "good_for"):
        if tokenize(good_for) & query_tokens or _contains_phrase(query, good_for):
            score += 2

    for step in _field_items(block, "procedure"):
        if tokenize(step) & query_tokens:
            score += 1

    title_tokens = tokenize(str(block.get("title", "")))
    summary_tokens = tokenize(str(block.get("summary", "")))
    score += len(query_tokens & title_tokens)
    score += len(query_tokens & summary_tokens)

    return score


def score_methodblock(block: dict[str, Any], task: str) -> float:
    """Score one MethodBlock as a normalized 0..1 value."""

    raw = raw_score_methodblock(block, task)
    if raw <= 0:
        return 0.0
    # A score of 12 already represents several strong field matches.
    return min(raw / 12, 1.0)


def search_methodblocks(blocks: list[tuple[str, dict[str, Any]]], task: str) -> list[tuple[float, str, dict[str, Any]]]:
    """Return MethodBlocks sorted by descending score."""

    scored = [(score_methodblock(block, task), path, block) for path, block in blocks]
    scored = [item for item in scored if item[0] > 0]
    return sorted(scored, key=lambda item: (-item[0], item[2].get("id", "")))
