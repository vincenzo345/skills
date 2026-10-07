"""Safety checks for the global v2 installer."""

from __future__ import annotations

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import install_global_v2 as installer


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_retire_rejects_path_outside_install_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside"):
            installer.retire(self.root / "elsewhere" / "skill", self.root / "skills")

    def test_real_directory_is_preserved_in_backup(self) -> None:
        base = self.root / "skills"
        skill = base / "example"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("original", encoding="utf-8")
        backup = self.root / "backup"
        with patch.object(installer, "BACKUP", backup):
            installer.retire(skill, base)
        self.assertFalse(skill.exists())
        self.assertEqual((backup / self.root.name / "skills" / "example" / "SKILL.md").read_text(), "original")

    @unittest.skipUnless(os.name == "nt", "junctions require Windows")
    def test_retiring_junction_preserves_target(self) -> None:
        base = self.root / "skills"
        source = self.root / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("source", encoding="utf-8")
        path = base / "example"
        installer.junction(path, source)
        self.assertTrue(os.path.isjunction(path))
        installer.retire(path, base)
        self.assertFalse(os.path.lexists(path))
        self.assertEqual((source / "SKILL.md").read_text(), "source")

    def test_workbench_hooks_are_removed_without_touching_other_guards(self) -> None:
        claude = self.root / "claude" / "skills"
        config = claude / "claude-rigor" / "hooks" / "hooks.json"
        config.parent.mkdir(parents=True)
        original = {"hooks": {"PreToolUse": [{"hooks": [
            {"command": "node workbench_new_item_guard.js"},
            {"command": "node read_only_network_guard.js"},
        ]}]}}
        config.write_text(json.dumps(original), encoding="utf-8")
        backup = self.root / "backup"
        with patch.object(installer, "CLAUDE", claude), patch.object(installer, "BACKUP", backup):
            installer.retire_workbench_hooks()
        self.assertTrue((backup / "claude-rigor-hooks.json").is_file())
        commands = [
            hook["command"] for group in json.loads(config.read_text())["hooks"]["PreToolUse"]
            for hook in group["hooks"]
        ]
        self.assertEqual(commands, ["node read_only_network_guard.js"])


if __name__ == "__main__":
    unittest.main()
