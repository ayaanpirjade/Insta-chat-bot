"""Command parsing helpers shared by routing and tests."""

from __future__ import annotations


def parse_command(text: str, prefix: str = "!") -> tuple[str | None, str]:
    value = (text or "").strip()
    if not value.startswith(prefix):
        return None, value
    command_text = value[len(prefix):].strip()
    if not command_text:
        return "", ""
    parts = command_text.split(maxsplit=1)
    return parts[0].lower(), parts[1].strip() if len(parts) > 1 else ""
