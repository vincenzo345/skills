#!/usr/bin/env python3
"""Request one skeptical completion review after Claude edits code.

This is a Claude Code Stop hook. It fails open on malformed input and honors
``stop_hook_active`` so the review can happen at most once per turn.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


EDIT_TOOLS = {"edit", "multiedit", "notebookedit", "write"}
REVIEW = (
    "Before finishing, challenge the implementation once as a skeptical reviewer. "
    "Re-read the request and inspect the final changes. Build explicit input partitions "
    "for valid, boundary, malformed, wrong-type, and failure cases; compare every partition "
    "with the required public contract and existing behavior. Resolve any stated judgment calls "
    "from repository evidence instead of narrowing the contract or asking the user. Check for "
    "missed callers, unintended files, weakened tests, silent fallbacks, and error-path regressions. "
    "Run the narrowest meaningful verification available, fix any discovered gap, then report only "
    "claims supported by executed evidence."
)


def _read_entries(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, str) or not value:
        return []
    path = Path(value)
    if not path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if isinstance(item, dict):
                entries.append(item)
    except (OSError, json.JSONDecodeError):
        return []
    return entries


def _is_human_request(entry: dict[str, Any]) -> bool:
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list) and any(
        isinstance(item, dict) and item.get("type") == "tool_result"
        for item in content
    ):
        return False
    return True


def _edited_since_latest_request(entries: list[dict[str, Any]]) -> bool:
    start = 0
    for index, entry in enumerate(entries):
        if _is_human_request(entry):
            start = index + 1
    for entry in entries[start:]:
        if entry.get("type") != "assistant":
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            tool = str(item.get("name") or "").rsplit(".", 1)[-1].lower()
            if tool in EDIT_TOOLS:
                return True
    return False


def _is_task_workspace(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return (Path(value) / "TASK.md").is_file()
    except OSError:
        return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "Stop":
        return 0
    if payload.get("stop_hook_active") is True:
        return 0
    edited = _edited_since_latest_request(_read_entries(payload.get("transcript_path")))
    if not edited and not _is_task_workspace(payload.get("cwd")):
        return 0
    print(json.dumps({"decision": "block", "reason": REVIEW}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
