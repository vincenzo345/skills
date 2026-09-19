"""Contract tests for the idempotent Claude-rigor global installer."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).parents[2]
INSTALLER = ROOT / "scripts" / "install-claude-rigor.ps1"


def run_installer(home: Path) -> dict:
    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-File", str(INSTALLER),
            "-ClaudeHome", str(home), "-SourceRoot", str(ROOT / "skills" / "claude-rigor"),
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_installer_preserves_unknown_settings_and_removes_only_known_legacy_hooks(tmp_path: Path) -> None:
    home = tmp_path / ".claude"
    home.mkdir()
    settings = {
        "model": "opus[1m]",
        "unknown": {"keep": True},
        "hooks": {
            "PreToolUse": [
                {"matcher": "Read", "hooks": [{"type": "command", "command": "python C:/x/workbench_diagnosis_hook.py"}]},
                {"matcher": "Bash", "hooks": [{"type": "command", "command": "keep-pre"}]},
            ],
            "Stop": [
                {"hooks": [{"type": "command", "command": "python C:/Users/test/.claude/hooks/completion_guard.py"}]},
                {"hooks": [{"type": "command", "command": "keep-stop"}]},
            ],
        },
    }
    (home / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    (home / "CLAUDE.md").write_text("# graphify\nkeep me\n\n# Operating contract\nold duplicate\n", encoding="utf-8")

    report = run_installer(home)
    installed_settings = json.loads((home / "settings.json").read_text(encoding="utf-8-sig"))

    assert installed_settings["unknown"] == {"keep": True}
    serialized = json.dumps(installed_settings)
    assert "keep-pre" in serialized and "keep-stop" in serialized
    assert "workbench_diagnosis_hook.py" not in serialized
    assert "completion_guard.py" not in serialized
    installed_claude = (home / "CLAUDE.md").read_text(encoding="utf-8-sig")
    assert "# graphify\nkeep me" in installed_claude
    assert "old duplicate" not in installed_claude
    assert installed_claude.count("# Claude Rigor (managed)") == 1
    assert "@~/.claude/skills/claude-rigor/agents/rigorous-engineer.md" in installed_claude
    assert report["pre_tool_use"] == 3 and report["user_prompt_submit"] == 1 and report["stop"] == 1
    assert report["global_prompt_import"] == "~/.claude/skills/claude-rigor/agents/rigorous-engineer.md"
    assert set(report["hook_file_sha256"]) == {
        "hooks.json", "completion_guard.js", "read_only_network_guard.js", "workbench_new_item_guard.js",
        "workbench_prompt_router.js", "performance_budget_guard.js",
    }
    assert not (home / "skills" / "claude-rigor" / "hooks" / "diagnosis_preflight.js").exists()


def test_installer_is_effectively_idempotent(tmp_path: Path) -> None:
    home = tmp_path / ".claude"
    home.mkdir()
    (home / "settings.json").write_text('{"hooks":{},"custom":1}', encoding="utf-8")
    (home / "CLAUDE.md").write_text("# personal\nvalue\n", encoding="utf-8")

    first = run_installer(home)
    settings_once = (home / "settings.json").read_bytes()
    claude_once = (home / "CLAUDE.md").read_bytes()
    second = run_installer(home)

    assert (home / "settings.json").read_bytes() == settings_once
    assert (home / "CLAUDE.md").read_bytes() == claude_once
    assert first["prompt_sha256"] == second["prompt_sha256"]
    assert first["hooks_sha256"] == second["hooks_sha256"]
