#!/usr/bin/env python3
"""Require diagnosing-bugs before a Workbench diagnosis starts investigating.

Claude Code PreToolUse hook: JSON on stdin, optional deny JSON on stdout.
Malformed or incomplete hook input fails open so this narrow guard cannot disable
unrelated tool use.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


INVESTIGATIVE_TOOLS = {
    "bash",
    "glob",
    "grep",
    "read",
    "task",
    "webfetch",
    "websearch",
}
WORKBENCH_PATTERN = re.compile(r"(?:^|[\s/])workbench\b", re.IGNORECASE)
DIAGNOSIS_PATTERN = re.compile(
    r"\b(?:diagnos(?:e|is|ing)|debug|slow(?:ly)?|broken|failing|fails?|performance\s+regression)\b",
    re.IGNORECASE,
)


def text_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(item) for item in value)
    if isinstance(value, dict):
        return "\n".join(
            text_content(value.get(key))
            for key in ("message", "text", "content", "name", "skill", "command", "args")
            if key in value
        )
    return ""


def read_transcript(path_value: Any) -> list[dict[str, Any]]:
    if not isinstance(path_value, str) or not path_value:
        return []
    path = Path(path_value)
    if not path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                entries.append(value)
    except (OSError, json.JSONDecodeError):
        return []
    return entries


def latest_human_prompt(entries: list[dict[str, Any]]) -> tuple[int, str] | None:
    for index in range(len(entries) - 1, -1, -1):
        entry = entries[index]
        if entry.get("type") != "user" or entry.get("isMeta"):
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, list) and any(
            isinstance(item, dict) and item.get("type") == "tool_result"
            for item in content
        ):
            continue
        prompt = text_content(content).strip()
        if prompt:
            return index, prompt
    return None


def workbench_is_active(prompt: str, cwd_value: Any) -> bool:
    if WORKBENCH_PATTERN.search(prompt):
        return True
    if not isinstance(cwd_value, str) or not cwd_value:
        return False
    try:
        current = Path(cwd_value).resolve()
    except OSError:
        return False
    for directory in (current, *current.parents):
        if (directory / ".workbench" / "active-work.json").is_file():
            return True
    return False


def diagnosing_bugs_loaded(entries: list[dict[str, Any]], prompt_index: int) -> bool:
    for entry in entries[prompt_index + 1 :]:
        text = text_content(entry).lower()
        if "diagnosing-bugs" not in text:
            continue
        if (
            entry.get("isMeta")
            or "base directory for this skill" in text
            or "<command-name>" in text
            or '"name":"skill"' in text.replace(" ", "")
        ):
            return True
    return False


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, separators=(",", ":")))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PreToolUse":
        return 0
    tool_name = str(payload.get("tool_name") or "").rsplit(".", 1)[-1].lower()
    if tool_name not in INVESTIGATIVE_TOOLS:
        return 0
    entries = read_transcript(payload.get("transcript_path"))
    current = latest_human_prompt(entries)
    if current is None:
        return 0
    prompt_index, prompt = current
    if not workbench_is_active(prompt, payload.get("cwd")):
        return 0
    if not DIAGNOSIS_PATTERN.search(prompt):
        return 0
    if diagnosing_bugs_loaded(entries, prompt_index):
        return 0
    deny(
        "This Workbench request reports a bug or performance problem. "
        "Invoke the diagnosing-bugs skill before investigative tool use, "
        "then retry this tool call."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
