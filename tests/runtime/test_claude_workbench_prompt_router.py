"""Prompt-time routing contract for explicit Workbench start-new requests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "workbench_prompt_router.js"


def run_hook(prompt: str) -> dict:
    result = subprocess.run(
        ["node", str(HOOK)],
        input=json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": prompt}),
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert result.returncode == 0 and result.stderr == ""
    return json.loads(result.stdout) if result.stdout.strip() else {}


def test_routes_explicit_workbench_start_new_before_first_tool() -> None:
    output = run_hook("/workbench investigate latency; ignore active work and start new")

    context = output["hookSpecificOutput"]["additionalContext"]
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "first tool call must be Skill(workbench)" in context
    assert "Do not inspect the repository" in context
    assert "one batched pass" in context
    assert "execution-environment reuse" in context
    assert "both inert and helpful" in context


def test_does_not_inject_for_resume_or_ordinary_request() -> None:
    assert run_hook("/workbench resume WB-123") == {}
    assert run_hook("Investigate latency and start new tests") == {}
