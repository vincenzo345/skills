"""Safety checks for the global v2 installer."""

from __future__ import annotations

import os
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


if __name__ == "__main__":
    unittest.main()
