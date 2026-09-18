"""Black-box contract for the narrow Claude Workbench diagnosis hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "skills" / "workbench" / "scripts" / "workbench_diagnosis_hook.py"


def write_transcript(path: Path, entries: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(entry) for entry in entries) + "\n",
        encoding="utf-8",
    )
    return path


def human_prompt(text: str) -> dict:
    return {
        "type": "user",
        "origin": {"kind": "human"},
        "message": {"role": "user", "content": text},
    }


def invoke_hook(tmp_path: Path, entries: list[dict], *, tool_name: str = "Read"):
    transcript = write_transcript(tmp_path / "session.jsonl", entries)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"file_path": "src/pdf.py"},
        "transcript_path": str(transcript),
        "cwd": str(tmp_path),
    }
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
    )


def test_hook_blocks_workbench_diagnosis_before_diagnosing_bugs_is_loaded(
    tmp_path: Path,
) -> None:
    result = invoke_hook(
        tmp_path,
        [human_prompt("/workbench the PDF preview loads slowly; diagnose why")],
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    decision = output["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert "diagnosing-bugs" in decision["permissionDecisionReason"]


def test_hook_allows_investigation_after_diagnosing_bugs_is_loaded(tmp_path: Path) -> None:
    result = invoke_hook(
        tmp_path,
        [
            human_prompt("/workbench the PDF preview loads slowly; diagnose why"),
            {
                "type": "user",
                "isMeta": True,
                "message": {
                    "role": "user",
                    "content": (
                        "Base directory for this skill: C:/Users/vince/.claude/skills/"
                        "diagnosing-bugs\n\n# Diagnosing Bugs"
                    ),
                },
            },
        ],
    )

    assert result.returncode == 0
    assert result.stdout == ""


def test_hook_ignores_non_diagnostic_workbench_requests(tmp_path: Path) -> None:
    result = invoke_hook(
        tmp_path,
        [human_prompt("/workbench implement the approved thumbnail controls")],
    )

    assert result.returncode == 0
    assert result.stdout == ""
