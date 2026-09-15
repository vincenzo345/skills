from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "show-workbench-status.py"
RECORDS = ROOT / "tests" / "records" / "proposal-only-checkpoint"
LIFECYCLE = ROOT / "schemas" / "workbench-lifecycle.schema.json"


def run_status(*extra: str, record_dir: Path = RECORDS) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            str(record_dir),
            "--lifecycle",
            str(LIFECYCLE),
            *extra,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ShowWorkbenchStatusTests(unittest.TestCase):
    def test_markdown_answers_control_questions_and_marks_projection_limit(self) -> None:
        result = run_status()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("**Read-only projection.**", result.stdout)
        self.assertIn("not event replay, transition proof", result.stdout)
        for heading in (
            "## Where am I?",
            "## What have we learned?",
            "## What did we decide, and which alternatives were rejected?",
            "## Why is this next?",
            "## What is still uncertain?",
            "## Ready frontier",
            "## Authorization and claim boundaries",
        ):
            self.assertIn(heading, result.stdout)
        self.assertIn("Agent-ready: none", result.stdout)
        self.assertIn("User decisions: `D-PROP-001`", result.stdout)
        self.assertIn("No option has been confirmed", result.stdout)
        self.assertIn("External blockers: none", result.stdout)
        self.assertIn("Active granted actions: none", result.stdout)
        self.assertIn("Does not authorize implementation, deployment", result.stdout)

    def test_json_is_deterministic_and_exposes_frontier_and_boundaries(self) -> None:
        first = run_status("--json")
        second = run_status("--json")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        view = json.loads(first.stdout)
        self.assertEqual(view["projection"]["kind"], "read-only-status")
        self.assertEqual(view["projection"]["event_replay"], "not-performed")
        self.assertEqual(view["work"]["work_id"], "WB-PROP-001")
        self.assertEqual(view["where"]["current_stage"], "proposal")
        self.assertEqual(view["frontier"]["agent_ready"], [])
        self.assertEqual(
            [item["node_id"] for item in view["frontier"]["user_decisions"]],
            ["D-PROP-001"],
        )
        self.assertEqual(view["authorization_boundary"]["active_grants"], [])

    def test_rejects_a_dangling_state_pointer_instead_of_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "checkpoint"
            shutil.copytree(RECORDS, checkpoint)
            state_path = checkpoint / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["decision_ids"] = ["DEC-MISSING-001"]
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_status("--json", record_dir=checkpoint)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("dangling ID: DEC-MISSING-001", result.stderr)

    def test_rejects_schema_invalid_proof_before_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "checkpoint"
            shutil.copytree(RECORDS, checkpoint)
            proof_path = checkpoint / "proof.json"
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
            proof["applicability"] = "not-applicable"
            proof_path.write_text(json.dumps(proof), encoding="utf-8")

            result = run_status("--json", record_dir=checkpoint)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("fails workbench-proof.schema.json", result.stderr)

    def test_rejects_nested_dangling_record_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "checkpoint"
            shutil.copytree(RECORDS, checkpoint)
            proof_path = checkpoint / "proof.json"
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
            proof["achieved_proof"][0]["evidence"][0]["record_id"] = "ART-MISSING-001"
            proof_path.write_text(json.dumps(proof), encoding="utf-8")

            result = run_status("--json", record_dir=checkpoint)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("dangling artifact reference: ART-MISSING-001", result.stderr)

    def test_projection_does_not_mutate_checkpoint_or_lifecycle(self) -> None:
        inputs = sorted(RECORDS.glob("*.json")) + [LIFECYCLE]
        before = {path: digest(path) for path in inputs}

        result = run_status()

        after = {path: digest(path) for path in inputs}
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
