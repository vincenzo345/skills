"""Executable contract for explicit Workbench start-new precedence."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "workbench_new_item_guard.js"


def run_hook(tmp_path: Path, entries: list[dict], tool: str, tool_input: dict) -> dict:
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("".join(json.dumps(item) + "\n" for item in entries), encoding="utf-8")
    result = subprocess.run(
        ["node", str(HOOK)], input=json.dumps({
            "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input, "transcript_path": str(transcript),
            "cwd": str(tmp_path),
        }), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert result.returncode == 0 and result.stderr == ""
    return json.loads(result.stdout) if result.stdout.strip() else {}


def request_entry(text: str) -> dict:
    return {"type": "user", "message": {"content": text}}


def test_blocks_old_item_inspection_before_explicit_new_item_exists(tmp_path: Path) -> None:
    output = run_hook(
        tmp_path,
        [request_entry("/workbench investigate latency; ignore active work and start new")],
        "Read", {"file_path": ".workbench/active-work.json"},
    )

    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "prepare-routing.py --capture-and-start now" in output["hookSpecificOutput"]["permissionDecisionReason"]


def test_allows_compact_input_then_atomic_start(tmp_path: Path) -> None:
    entries = [request_entry("/workbench investigate latency; ignore active work and start new")]

    write = run_hook(
        tmp_path, entries, "Write",
        {"file_path": str(tmp_path / ".wb-routing.json"), "content": "{}"},
    )
    route = run_hook(
        tmp_path, entries, "Bash",
        {"command": "python prepare-routing.py --input .wb-routing.json --output .wb-prepared.json --capture-and-start"},
    )

    assert write == {}
    assert route == {}


def test_allows_bundled_method_read_before_start(tmp_path: Path) -> None:
    method = tmp_path / ".claude" / "skills" / "workbench" / "references" / "performance-investigation.md"
    method.parent.mkdir(parents=True)
    method.write_text("# Method\n", encoding="utf-8")

    output = run_hook(
        tmp_path,
        [request_entry("/workbench investigate latency; ignore active work and start new")],
        "Read", {"file_path": str(method)},
    )

    assert output == {}


def test_allows_workbench_skill_invocation_before_start(tmp_path: Path) -> None:
    output = run_hook(
        tmp_path,
        [request_entry("/workbench investigate latency; ignore active work and start new")],
        "Skill", {"skill": "workbench", "args": "investigate latency"},
    )

    assert output == {}


def test_allows_bash_cat_of_bundled_method_before_start(tmp_path: Path) -> None:
    output = run_hook(
        tmp_path,
        [request_entry("/workbench investigate latency; ignore active work and start new")],
        "Bash", {"command": 'cat "C:/Users/test/.claude/skills/workbench/references/performance-investigation.md"'},
    )

    assert output == {}


def test_blocks_compact_input_outside_workspace(tmp_path: Path) -> None:
    outside = tmp_path.parent / "routing-input.json"
    output = run_hook(
        tmp_path,
        [request_entry("/workbench investigate latency; ignore active work and start new")],
        "Write", {"file_path": str(outside), "content": "{}"},
    )

    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_allows_normal_work_after_start_succeeds(tmp_path: Path) -> None:
    entries = [
        request_entry("/workbench investigate latency; ignore active work and start new"),
        {"type": "user", "isMeta": True, "message": {"content": "result: captured-and-started"}},
    ]

    output = run_hook(tmp_path, entries, "Read", {"file_path": "backend/app.py"})

    assert output == {}


def test_does_not_affect_workbench_resume_or_non_workbench_tasks(tmp_path: Path) -> None:
    resume = run_hook(
        tmp_path, [request_entry("/workbench resume WB-123")],
        "Read", {"file_path": ".workbench/active-work.json"},
    )
    ordinary = run_hook(
        tmp_path, [request_entry("Investigate latency and start new tests")],
        "Read", {"file_path": "app.py"},
    )

    assert resume == {}
    assert ordinary == {}
