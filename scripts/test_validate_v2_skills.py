"""Mutation controls for the v2 skill package validator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_v2_skills import validate


class SkillPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skill = self.root / "skills" / "productivity" / "show-me"
        (self.root / "skills" / "engineering").mkdir(parents=True)
        (self.skill / "agents").mkdir(parents=True)
        (self.root / "docs" / "productivity").mkdir(parents=True)
        (self.root / ".claude-plugin").mkdir()
        (self.root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"skills": ["./skills/productivity/show-me"]}), encoding="utf-8"
        )
        (self.root / "README.md").write_text(
            "[show-me](./skills/productivity/show-me/SKILL.md)", encoding="utf-8"
        )
        (self.root / "skills" / "productivity" / "README.md").write_text(
            "[show-me](./show-me/SKILL.md)", encoding="utf-8"
        )
        (self.root / "docs" / "productivity" / "show-me.md").write_text(
            "## What it does\n", encoding="utf-8"
        )
        (self.skill / "SKILL.md").write_text(
            "---\nname: show-me\ndescription: Show the topic visually.\n"
            "disable-model-invocation: true\n---\n\nShow the topic.\n",
            encoding="utf-8",
        )
        (self.skill / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: Show Me\n"
            "  short_description: Visualize the topic\n"
            "policy:\n  allow_implicit_invocation: false\n",
            encoding="utf-8",
        )

    def test_valid_package(self) -> None:
        self.assertEqual(validate(self.root), [])

    def test_missing_manifest_membership_is_rejected(self) -> None:
        (self.root / ".claude-plugin" / "plugin.json").write_text(
            '{"skills": []}', encoding="utf-8"
        )
        self.assertIn("promoted skill missing", "\n".join(validate(self.root)))

    def test_cross_host_invocation_mismatch_is_rejected(self) -> None:
        (self.skill / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: Show Me\n"
            "  short_description: Visualize the topic\n",
            encoding="utf-8",
        )
        self.assertIn("invocation policy disagrees", "\n".join(validate(self.root)))

    def test_duplicate_frontmatter_key_is_rejected(self) -> None:
        original = (self.skill / "SKILL.md").read_text(encoding="utf-8")
        (self.skill / "SKILL.md").write_text(
            original.replace("name: show-me", "name: show-me\nname: duplicate"),
            encoding="utf-8",
        )
        self.assertIn("duplicate YAML key", "\n".join(validate(self.root)))


if __name__ == "__main__":
    unittest.main()
