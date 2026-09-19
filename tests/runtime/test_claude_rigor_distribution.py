"""Distribution contract for the direct-GitHub Claude rigor harness."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
PLUGIN = ROOT / "skills" / "claude-rigor"


def test_skill_is_a_self_contained_claude_skills_directory_plugin() -> None:
    skill = (PLUGIN / "SKILL.md").read_text(encoding="utf-8")
    manifest = json.loads(
        (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    settings = json.loads((PLUGIN / "settings.json").read_text(encoding="utf-8"))

    assert "name: claude-rigor" in skill
    assert "disable-model-invocation: true" in skill
    assert manifest["name"] == "claude-rigor"
    assert settings == {"agent": "rigorous-engineer"}


def test_plugin_registers_narrow_read_only_guard_and_completion_guard() -> None:
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    stop = hooks["hooks"]["Stop"]
    command = stop[0]["hooks"][0]["command"]

    assert "${CLAUDE_PLUGIN_ROOT}" in command
    assert "completion_guard.js" in command
    assert (PLUGIN / "hooks" / "completion_guard.js").is_file()

    pre = hooks["hooks"]["PreToolUse"]
    assert "workbench_new_item_guard.js" in pre[0]["hooks"][0]["command"]
    assert pre[1]["matcher"] == "Bash"
    assert "read_only_network_guard.js" in pre[1]["hooks"][0]["command"]
    assert "performance_budget_guard.js" in pre[2]["hooks"][0]["command"]
    submit = hooks["hooks"]["UserPromptSubmit"]
    assert "workbench_prompt_router.js" in submit[0]["hooks"][0]["command"]
    assert (PLUGIN / "hooks" / "read_only_network_guard.js").is_file()
    assert (PLUGIN / "hooks" / "workbench_new_item_guard.js").is_file()
    assert (PLUGIN / "hooks" / "workbench_prompt_router.js").is_file()
    assert (PLUGIN / "hooks" / "performance_budget_guard.js").is_file()
    assert not (PLUGIN / "hooks" / "diagnosis_preflight.js").exists()


def test_default_agent_carries_the_validated_operating_contract() -> None:
    agent = (PLUGIN / "agents" / "rigorous-engineer.md").read_text(encoding="utf-8")

    assert "name: rigorous-engineer" in agent
    assert "## Orient" in agent
    assert "## Act" in agent
    assert "## Verify" in agent
    assert "## Completion" in agent
    assert "valid, boundary, malformed, wrong-type" in agent
    assert "structured answer returned by an interactive question tool" in agent
    assert "active worktree, deployed revision, runtime configuration" in agent
    assert "service-wide aggregates as service-wide" in agent
    assert "populate caches" in agent
    assert "request-level identity or a controlled intervention" in agent
    assert '"Clean" and "unchanged by this task" are different claims' in agent
    assert "Use removes, eliminates, guarantees" in agent
    assert "Reuse does not transfer validity" in agent
    assert "Cross-check option numbers" in agent
    assert "detaches work from a request" in agent


def test_plugin_has_no_repository_relative_runtime_dependencies() -> None:
    runtime_files = [
        PLUGIN / "settings.json",
        PLUGIN / "agents" / "rigorous-engineer.md",
        PLUGIN / "hooks" / "hooks.json",
        PLUGIN / "hooks" / "completion_guard.js",
        PLUGIN / "hooks" / "read_only_network_guard.js",
        PLUGIN / "hooks" / "workbench_new_item_guard.js",
        PLUGIN / "hooks" / "workbench_prompt_router.js",
        PLUGIN / "hooks" / "performance_budget_guard.js",
    ]

    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        assert "claude_harness_eval" not in text
        assert "..\\" not in text
        assert "../" not in text
