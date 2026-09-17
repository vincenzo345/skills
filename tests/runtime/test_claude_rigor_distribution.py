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


def test_plugin_registers_portable_one_shot_completion_guard() -> None:
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    stop = hooks["hooks"]["Stop"]
    command = stop[0]["hooks"][0]["command"]

    assert "${CLAUDE_PLUGIN_ROOT}" in command
    assert "completion_guard.js" in command
    assert (PLUGIN / "hooks" / "completion_guard.js").is_file()


def test_default_agent_carries_the_validated_operating_contract() -> None:
    agent = (PLUGIN / "agents" / "rigorous-engineer.md").read_text(encoding="utf-8")

    assert "name: rigorous-engineer" in agent
    assert "Orient before editing" in agent
    assert "Act coherently" in agent
    assert "Falsify the solution" in agent
    assert "Close honestly" in agent
    assert "valid inputs, boundary values, malformed values, wrong-type values" in agent
    assert "wrong input type" in agent


def test_plugin_has_no_repository_relative_runtime_dependencies() -> None:
    runtime_files = [
        PLUGIN / "settings.json",
        PLUGIN / "agents" / "rigorous-engineer.md",
        PLUGIN / "hooks" / "hooks.json",
        PLUGIN / "hooks" / "completion_guard.js",
    ]

    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        assert "claude_harness_eval" not in text
        assert "..\\" not in text
        assert "../" not in text
