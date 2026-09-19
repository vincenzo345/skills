"""Tool-budget backstop for bounded Workbench performance investigations."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "performance_budget_guard.js"


def run_hook(tmp_path: Path, calls: int, tool: str, tool_input: dict) -> dict:
    transcript = tmp_path / "transcript.jsonl"
    entries = [{"type": "user", "message": {"content": "/workbench investigate slow preview latency; start new"}}]
    entries.extend(
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}}
        for _ in range(calls)
    )
    transcript.write_text("".join(json.dumps(item) + "\n" for item in entries), encoding="utf-8")
    result = subprocess.run(
        ["node", str(HOOK)],
        input=json.dumps({
            "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input, "transcript_path": str(transcript), "cwd": str(tmp_path),
        }),
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert result.returncode == 0 and result.stderr == ""
    return json.loads(result.stdout) if result.stdout.strip() else {}


def test_allows_discovery_below_budget_and_stops_it_at_budget(tmp_path: Path) -> None:
    assert run_hook(tmp_path, 29, "Read", {"file_path": "app.py"}) == {}
    stopped = run_hook(tmp_path, 30, "Read", {"file_path": "app.py"})
    assert stopped["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "Stop repository discovery" in stopped["hookSpecificOutput"]["permissionDecisionReason"]


def test_allows_artifact_writes_and_lifecycle_helpers_at_budget(tmp_path: Path) -> None:
    assert run_hook(tmp_path, 30, "Write", {"file_path": "proposal.md"}) == {}
    assert run_hook(
        tmp_path, 30, "Bash", {"command": "python prepare-handoff.py --accept-to-proposal"},
    ) == {}


def test_does_not_affect_nonperformance_workbench_request(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"type": "user", "message": {"content": "/workbench plan a new form; start new"}}) + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["node", str(HOOK)], input=json.dumps({
            "hook_event_name": "PreToolUse", "tool_name": "Read",
            "tool_input": {"file_path": "app.py"}, "transcript_path": str(transcript), "cwd": str(tmp_path),
        }), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert result.returncode == 0 and result.stdout.strip() == ""
