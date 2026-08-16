"""Pure text helpers used by the Instagram delivery layer."""

from __future__ import annotations

import re


def split_message(text: str, limit: int = 900) -> list[str]:
    """Split text at paragraph, sentence, or whitespace boundaries without empty chunks."""
    text = (text or "").strip()
    if not text:
        return []
    if limit < 80:
        raise ValueError("limit must be at least 80 characters")

    chunks: list[str] = []
    while len(text) > limit:
        window = text[: limit + 1]
        candidates = [window.rfind("\n\n"), window.rfind("\n")]
        sentence_matches = list(re.finditer(r"[.!?。！？](?:\s|$)", window))
        if sentence_matches:
            candidates.append(sentence_matches[-1].end())
        candidates.append(window.rfind(" "))
        cut = max((value for value in candidates if value > 0), default=limit)
        if cut < max(40, limit // 3):
            cut = limit
        part = text[:cut].strip()
        if not part:
            cut = limit
            part = text[:cut].strip()
        chunks.append(part)
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks
