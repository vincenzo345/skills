"""Black-box contract for the Claude-rigor diagnosis preflight."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "diagnosis_preflight.js"


def human(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def skill(name: str) -> dict:
    return {
        "type": "user",
        "isMeta": True,
        "message": {"role": "user", "content": f"Base directory for this skill: C:/skills/{name}\n# {name}"},
    }


def invoke(tmp_path: Path, entries: list[dict], payload: dict | None = None) -> subprocess.CompletedProcess[str]:
    transcript = tmp_path / "session.jsonl"
    transcript.write_text("".join(json.dumps(item) + "\n" for item in entries), encoding="utf-8")
    body = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Read",
        "transcript_path": str(transcript),
        "cwd": str(tmp_path),
        **(payload or {}),
    }
    return subprocess.run(
        ["node", str(HOOK)], input=json.dumps(body), capture_output=True, text=True, check=False
    )


def test_first_workbench_diagnosis_tool_call_gets_composed_preflight(tmp_path: Path) -> None:
    result = invoke(tmp_path, [human("/workbench the PDF preview is slow; investigate and give options")])
    output = json.loads(result.stdout)["hookSpecificOutput"]

    assert result.returncode == 0
    assert output["permissionDecision"] == "deny"
    assert "load Workbench" not in output["permissionDecisionReason"]
    assert "load diagnosing-bugs" in output["permissionDecisionReason"]
    assert "observed environment is user-owned and missing" in output["permissionDecisionReason"]
    assert "Do not invoke another tool" in output["permissionDecisionReason"]


def test_preflight_blocks_once_then_allows_retry(tmp_path: Path) -> None:
    entries = [
        human("/workbench the PDF preview is slow in the deployed test environment; investigate"),
        skill("workbench"),
        skill("diagnosing-bugs"),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: disposition environment"}},
    ]
    result = invoke(tmp_path, entries)

    assert result.returncode == 0
    assert result.stdout == ""


def test_complete_user_supplied_coordinates_allow_first_repo_tool(tmp_path: Path) -> None:
    entries = [
        human(
            "/workbench investigate page-preview latency in the deployed test environment. "
            "Use source snapshot commit abc123; the customer fixture is unavailable and "
            "cold/warm cache state is unknown for this journey."
        ),
        skill("diagnosing-bugs"),
    ]

    result = invoke(tmp_path, entries)

    assert result.returncode == 0
    assert result.stdout == ""


def test_incomplete_coordinates_still_get_one_shot_disposition(tmp_path: Path) -> None:
    entries = [
        human("/workbench diagnose the slow deployed test page-preview journey"),
        skill("diagnosing-bugs"),
    ]

    result = invoke(tmp_path, entries)

    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "disposition environment" in output["permissionDecisionReason"]


def test_missing_environment_remains_blocked_after_skill_load(tmp_path: Path) -> None:
    entries = [
        human("/workbench the PDF preview is slow; investigate"),
        skill("workbench"),
        skill("diagnosing-bugs"),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: prior denial"}},
    ]
    result = invoke(tmp_path, entries)

    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "Ask only whether" in output["permissionDecisionReason"]


def test_unrelated_request_and_malformed_input_fail_open(tmp_path: Path) -> None:
    result = invoke(tmp_path, [human("Explain this parser")])
    malformed = subprocess.run(
        ["node", str(HOOK)], input="{", capture_output=True, text=True, check=False
    )

    assert result.returncode == 0 and result.stdout == ""
    assert malformed.returncode == 0 and malformed.stdout == ""


def test_denies_unbounded_diagnostic_benchmark_after_preflight(tmp_path: Path) -> None:
    entries = [
        human("Diagnose slow PDF loading in the deployed test environment."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    result = invoke(
        tmp_path, entries,
        {"tool_name": "Bash", "tool_input": {"command": "python bench.py", "description": "Run benchmark"}},
    )

    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert result.returncode == 0
    assert output["permissionDecision"] == "deny"
    assert "two representative fixtures" in output["permissionDecisionReason"]
    assert "timeout 120s" in output["permissionDecisionReason"]


def test_allows_explicitly_bounded_diagnostic_benchmark(tmp_path: Path) -> None:
    entries = [
        human("Diagnose slow PDF loading in the deployed test environment."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    result = invoke(
        tmp_path, entries,
        {"tool_name": "Bash", "tool_input": {
            "command": "BENCHMARK_BUDGET_SECONDS=120 timeout 120s python bench.py"
        }},
    )

    assert result.returncode == 0
    assert result.stdout == ""


def test_benchmark_words_inside_heredoc_data_do_not_trigger_guard(tmp_path: Path) -> None:
    entries = [
        human("Diagnose slow PDF loading in the deployed test environment."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    result = invoke(
        tmp_path, entries,
        {"tool_name": "Bash", "tool_input": {"command": "cat > phase.json <<'JSON'\n{\"finding\":\"bounded benchmark evidence\"}\nJSON"}},
    )

    assert result.returncode == 0
    assert result.stdout == ""


def test_denies_delegation_for_a_single_journey_diagnosis(tmp_path: Path) -> None:
    entries = [
        human("Diagnose the deployed page-preview journey and give options."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    result = invoke(
        tmp_path, entries,
        {"tool_name": "Agent", "tool_input": {"description": "Trace deployment configuration"}},
    )

    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "current agent" in output["permissionDecisionReason"]


def test_denies_direct_lifecycle_mutation_and_allows_compact_helper(tmp_path: Path) -> None:
    entries = [
        human("/workbench diagnose the deployed page-preview journey and give options."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    payload = {"tool_name": "Bash", "tool_input": {
        "command": "python workbench.py accept-handoff --handoff-bundle bundle-proposal.json"
    }}
    denied = invoke(tmp_path, entries, payload)
    reason = json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "compact lifecycle helpers" in reason
    assert "--accept-and-advance" in reason

    allowed = invoke(tmp_path, entries, {"tool_name": "Bash", "tool_input": {
        "command": "python prepare-handoff.py --input proposal.json --output bundle.json --accept-and-advance"
    }})
    assert allowed.stdout == ""


def test_blocks_workbench_internal_schema_read_but_allows_helper_invocation(tmp_path: Path) -> None:
    entries = [
        human("/workbench diagnose the deployed page-preview journey."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    denied = invoke(tmp_path, entries, {
        "tool_name": "Read", "tool_input": {"file_path": "skills/workbench/references/schemas/workbench-handoff.schema.json"},
    })
    reason = json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "WORKBENCH_ABSTRACTION_V1" in reason

    entries.append({"type": "user", "isMeta": True, "message": {"content": reason}})
    denied_again = invoke(tmp_path, entries, {
        "tool_name": "Read", "tool_input": {"file_path": ".claude/skills/workbench/references/routing.md"},
    })
    assert json.loads(denied_again.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"

    allowed = invoke(tmp_path, entries, {
        "tool_name": "Bash", "tool_input": {
            "command": "python prepare-handoff.py --input phase.json --output bundle.json"
        },
    })
    assert allowed.stdout == ""


def test_blocks_workbench_schema_discovery_and_help_probes(tmp_path: Path) -> None:
    entries = [
        human("/workbench diagnose the deployed page-preview journey."),
        {"type": "user", "isMeta": True, "message": {"content": "DIAGNOSIS_PREFLIGHT_V1: coordinates checked"}},
    ]
    for command in (
        "find .claude/skills/workbench -name '*.json'",
        "python .claude/skills/workbench/scripts/workbench.py capture-intake --help",
    ):
        denied = invoke(tmp_path, entries, {"tool_name": "Bash", "tool_input": {"command": command}})
        assert json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
