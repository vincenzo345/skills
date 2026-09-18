"""Executable contract for the distributed Claude completion-review Stop hook."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "completion_guard.js"


def run_hook(tmp_path: Path, entries: list[dict], **overrides: object) -> tuple[int, dict, str]:
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")
    payload = {
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "transcript_path": str(transcript),
        "last_assistant_message": "Implemented the requested change.",
        **overrides,
    }
    result = subprocess.run(
        ["node", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, json.loads(result.stdout) if result.stdout.strip() else {}, result.stderr


def test_blocks_first_stop_after_edit_with_contract_review_guidance(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "Fix the public parser contract"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {}}]}},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output["decision"] == "block"
    assert "input partitions" in output["reason"]
    assert "existing behavior" in output["reason"]
    assert "judgment calls" in output["reason"]
    assert stderr == ""


def test_allows_second_stop_to_prevent_an_infinite_loop(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "Fix it"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {}}]}},
    ]

    code, output, stderr = run_hook(tmp_path, entries, stop_hook_active=True)

    assert code == 0
    assert output == {}
    assert stderr == ""


def test_does_not_interrupt_read_only_answers(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "Explain this code"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output == {}
    assert stderr == ""


def test_blocks_first_stop_after_read_only_performance_investigation(
    tmp_path: Path,
) -> None:
    entries = [
        {
            "type": "user",
            "message": {
                "content": "The PDF preview is slow. Investigate and give me options."
            },
        },
        {
            "type": "assistant",
            "message": {
                "content": [{"type": "tool_use", "name": "Read", "input": {}}]
            },
        },
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output["decision"] == "block"
    assert "cache/path frequency" in output["reason"]
    assert "aggregate service metrics" in output["reason"]
    assert "discriminating end-to-end intervention" in output["reason"]
    assert "active worktree" in output["reason"]
    assert "unresolved environment" in output["reason"]
    assert "durable Workbench artifact and state" in output["reason"]
    assert "do not broaden" in output["reason"]
    assert "input partitions" not in output["reason"]
    assert stderr == ""


def test_diagnostic_prompt_without_investigative_tool_use_does_not_block(
    tmp_path: Path,
) -> None:
    entries = [
        {
            "type": "user",
            "message": {"content": "Why can software sometimes feel slow?"},
        },
        {"type": "assistant", "message": {"content": "Several factors can contribute."}},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output == {}
    assert stderr == ""


def test_waiting_for_missing_environment_does_not_trigger_final_review(tmp_path: Path) -> None:
    entries = [
        {
            "type": "user",
            "message": {"content": "The PDF preview is slow. Investigate and give options."},
        },
        {
            "type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {}}]},
        },
        {
            "type": "user",
            "message": {
                "content": [{"type": "tool_result", "content": "DIAGNOSIS_PREFLIGHT_V1: ask environment"}]
            },
        },
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output == {}
    assert stderr == ""


def test_diagnostic_stop_review_runs_even_after_legacy_proposal_marker(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "/workbench diagnose the deployed preview journey"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
        {"type": "user", "isMeta": True, "message": {
            "content": "DIAGNOSIS_PROPOSAL_REVIEW_V1: reviewed before acceptance"
        }},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output["decision"] == "block"
    assert "narrow final backstop" in output["reason"]
    assert stderr == ""


def test_diagnostic_stop_review_is_skipped_after_terminal_review_marker(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "/workbench diagnose the deployed preview journey"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
        {"type": "user", "isMeta": True, "message": {
            "content": "{\"review_marker\":\"DIAGNOSIS_PROPOSAL_REVIEW_V2\"}"
        }},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output == {}
    assert stderr == ""


def test_diagnostic_review_takes_precedence_when_investigation_also_edits(
    tmp_path: Path,
) -> None:
    entries = [
        {
            "type": "user",
            "message": {"content": "Diagnose the slow API and record the findings."},
        },
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {}},
                    {"type": "tool_use", "name": "Write", "input": {}},
                ]
            },
        },
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output["decision"] == "block"
    assert "discriminating end-to-end intervention" in output["reason"]
    assert "input partitions" not in output["reason"]
    assert stderr == ""


def test_task_workspace_blocks_even_when_transcript_omits_edit_events(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "TASK.md").write_text("Fix the parser", encoding="utf-8")

    code, output, stderr = run_hook(tmp_path, [], cwd=str(workspace))

    assert code == 0
    assert output["decision"] == "block"
    assert stderr == ""


def test_only_considers_edits_after_latest_user_request(tmp_path: Path) -> None:
    entries = [
        {"type": "user", "message": {"content": "Fix it"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {}}]}},
        {"type": "user", "message": {"content": "Now explain why"}},
        {"type": "assistant", "message": {"content": "Explanation"}},
    ]

    code, output, stderr = run_hook(tmp_path, entries)

    assert code == 0
    assert output == {}
    assert stderr == ""
