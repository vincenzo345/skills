"""Public-seam acceptance tests for the local coding-agent evaluation suite."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from claude_harness_eval import (
    apply_reference,
    get_task,
    list_tasks,
    stage_task,
    validate_tasks,
    verify_task,
)


TRACER_TASK = "inclusive-range-partition"
EXPECTED_TASKS = {
    "inclusive-range-partition",
    "unicode-username-match",
    "one-shot-iterator",
    "pagination-cursor",
    "cache-key-completeness",
    "config-precedence",
    "backward-compatible-api",
    "error-contract",
    "cross-file-symbol-rename",
    "serialization-extensions",
    "cli-stream-semantics",
    "atomic-settings-write",
    "path-containment",
    "secret-safe-diagnostics",
    "sqlite-transaction",
    "concurrent-memoization",
    "shared-validator-refactor",
    "implementation-not-tests",
    "two-cause-regression",
    "preserve-dirty-file",
    "resource-cleanup-contract",
    "retry-attempt-semantics",
    "atomic-batch-update",
    "single-pass-first-match",
}


def test_tracer_task_is_staged_red_and_reference_green(tmp_path: Path) -> None:
    task = get_task(TRACER_TASK)
    workspace = tmp_path / "workspace"

    staged = stage_task(task.id, workspace)

    assert staged["task_id"] == TRACER_TASK
    assert (workspace / "TASK.md").read_text(encoding="utf-8") == task.instruction
    assert json.loads((workspace / ".harness-eval.json").read_text(encoding="utf-8"))["task_id"] == task.id

    baseline = verify_task(task.id, workspace)
    assert baseline["passed"] is False
    assert baseline["status"] == "failed"

    apply_reference(task.id, workspace)
    reference = verify_task(task.id, workspace)
    assert reference["passed"] is True, reference
    assert reference["status"] == "passed"


def test_staging_exposes_only_instruction_marker_and_seed(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    stage_task(TRACER_TASK, workspace)

    assert sorted(path.name for path in workspace.iterdir()) == [
        ".harness-eval.json",
        "TASK.md",
        "ranges.py",
    ]
    exposed = "\n".join(
        path.read_text(encoding="utf-8") for path in workspace.iterdir() if path.is_file()
    )
    assert "flattened =" not in exposed
    assert "while cursor <= end:" not in exposed


def test_stage_rejects_nonempty_destination_and_verify_rejects_wrong_marker(tmp_path: Path) -> None:
    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "owned.txt").write_text("preserve me", encoding="utf-8")
    with pytest.raises(ValueError, match="must be empty"):
        stage_task(TRACER_TASK, nonempty)
    assert (nonempty / "owned.txt").read_text(encoding="utf-8") == "preserve me"

    workspace = tmp_path / "workspace"
    stage_task(TRACER_TASK, workspace)
    marker_path = workspace / ".harness-eval.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker["task_id"] = "different-task"
    marker_path.write_text(json.dumps(marker), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        verify_task(TRACER_TASK, workspace)


def test_cli_lists_and_verifies_with_machine_readable_results(tmp_path: Path) -> None:
    listed = subprocess.run(
        [sys.executable, "-m", "claude_harness_eval", "list", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert listed.returncode == 0, listed.stderr
    assert json.loads(listed.stdout)["tasks"][0]["id"] == TRACER_TASK

    workspace = tmp_path / "workspace"
    stage_task(TRACER_TASK, workspace)
    verified = subprocess.run(
        [sys.executable, "-m", "claude_harness_eval", "verify", TRACER_TASK, str(workspace), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    result = json.loads(verified.stdout)
    assert verified.returncode == 1
    assert result["command"] == "verify"
    assert result["task_id"] == TRACER_TASK
    assert result["passed"] is False
    assert result["timed_out"] is False


def test_catalog_has_fixed_representative_coverage() -> None:
    tasks = list_tasks()

    assert {task.id for task in tasks} == EXPECTED_TASKS
    assert len(tasks) == len(EXPECTED_TASKS) == 24
    assert {task.category for task in tasks} == {
        "algorithmic",
        "integration",
        "robustness",
        "work-discipline",
    }
    for task in tasks:
        assert task.title.strip()
        assert task.tags
        assert "Completion criteria:" in task.instruction
        assert task.seed_files
        assert task.reference_files
        assert task.acceptance_program.strip()
        assert task.timeout_seconds > 0


def test_every_staged_workspace_contains_only_public_seed_material(tmp_path: Path) -> None:
    for task in list_tasks():
        workspace = tmp_path / task.id
        stage_task(task.id, workspace)
        actual_files = {
            path.relative_to(workspace).as_posix()
            for path in workspace.rglob("*")
            if path.is_file()
        }
        expected_files = {"TASK.md", ".harness-eval.json"} | {
            file.path for file in task.seed_files
        }
        assert actual_files == expected_files, task.id


def test_author_validation_proves_red_baseline_and_green_reference() -> None:
    result = validate_tasks([TRACER_TASK], repeat=2)

    assert result["passed"] is True
    assert result["repeat"] == 2
    task_result = result["tasks"][0]
    assert task_result["task_id"] == TRACER_TASK
    assert len(task_result["attempts"]) == 2
    assert all(attempt["baseline_passed"] is False for attempt in task_result["attempts"])
    assert all(attempt["reference_passed"] is True for attempt in task_result["attempts"])


def test_full_catalog_author_validation_passes() -> None:
    result = validate_tasks(repeat=1)

    assert result["passed"] is True
    assert {task["task_id"] for task in result["tasks"]} == EXPECTED_TASKS


def test_cli_validate_emits_aggregate_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "claude_harness_eval",
            "validate",
            TRACER_TASK,
            "--repeat",
            "1",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["command"] == "validate"
    assert result["passed"] is True
