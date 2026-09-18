"""Workspace staging and evaluator-owned acceptance execution."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from .catalog import FileSpec, get_task, list_tasks


SCHEMA_VERSION = 1
SUITE_CANARY = "CLAUDE-HARNESS-EVAL-ORIGINAL-SYNTHETIC-V1"


def _write_files(workspace: Path, files: tuple[FileSpec, ...]) -> None:
    for file_spec in files:
        destination = workspace.joinpath(*file_spec.path.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(file_spec.content, encoding="utf-8", newline="\n")


def stage_task(task_id: str, workspace: Path | str) -> dict:
    task = get_task(task_id)
    destination = Path(workspace)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"workspace must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "TASK.md").write_text(task.instruction, encoding="utf-8", newline="\n")
    marker = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task.id,
        "title": task.title,
        "category": task.category,
        "tags": list(task.tags),
        "suite_canary": SUITE_CANARY,
    }
    (destination / ".harness-eval.json").write_text(
        json.dumps(marker, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _write_files(destination, task.seed_files)
    return {"schema_version": SCHEMA_VERSION, "command": "stage", "task_id": task.id, "workspace": str(destination)}


def _require_matching_workspace(task_id: str, workspace: Path) -> None:
    marker_path = workspace / ".harness-eval.json"
    if not marker_path.is_file():
        raise ValueError(f"workspace is not staged: {workspace}")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("task_id") != task_id or marker.get("suite_canary") != SUITE_CANARY:
        raise ValueError(f"workspace marker does not match task {task_id}")


def verify_task(task_id: str, workspace: Path | str) -> dict:
    task = get_task(task_id)
    root = Path(workspace).resolve()
    _require_matching_workspace(task.id, root)
    started = time.perf_counter()
    verifier_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as verifier:
            verifier.write(task.acceptance_program)
            verifier_path = Path(verifier.name)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(verifier_path), str(root)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=task.timeout_seconds,
            env=environment,
            check=False,
        )
        passed = completed.returncode == 0
        return {
            "schema_version": SCHEMA_VERSION,
            "command": "verify",
            "task_id": task.id,
            "status": "passed" if passed else "failed",
            "passed": passed,
            "exit_code": completed.returncode,
            "timed_out": False,
            "duration_seconds": round(time.perf_counter() - started, 6),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "command": "verify",
            "task_id": task.id,
            "status": "timed-out",
            "passed": False,
            "exit_code": None,
            "timed_out": True,
            "duration_seconds": round(time.perf_counter() - started, 6),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }
    finally:
        if verifier_path is not None:
            verifier_path.unlink(missing_ok=True)


def apply_reference(task_id: str, workspace: Path | str) -> dict:
    task = get_task(task_id)
    root = Path(workspace).resolve()
    _require_matching_workspace(task.id, root)
    _write_files(root, task.reference_files)
    return {"schema_version": SCHEMA_VERSION, "command": "apply-reference", "task_id": task.id}


def validate_tasks(task_ids: list[str] | tuple[str, ...] | None = None, *, repeat: int = 1) -> dict:
    if repeat < 1:
        raise ValueError("repeat must be at least 1")
    selected = list(list_tasks()) if task_ids is None else [get_task(task_id) for task_id in task_ids]
    task_results = []
    passed = True
    for task in selected:
        attempts = []
        for attempt_number in range(1, repeat + 1):
            with tempfile.TemporaryDirectory(prefix=f"harness-eval-{task.id}-") as temp:
                workspace = Path(temp) / "workspace"
                stage_task(task.id, workspace)
                baseline = verify_task(task.id, workspace)
                apply_reference(task.id, workspace)
                reference = verify_task(task.id, workspace)
            attempt_passed = not baseline["passed"] and reference["passed"]
            passed = passed and attempt_passed
            attempts.append(
                {
                    "attempt": attempt_number,
                    "passed": attempt_passed,
                    "baseline_passed": baseline["passed"],
                    "baseline_status": baseline["status"],
                    "baseline_result": baseline,
                    "reference_passed": reference["passed"],
                    "reference_status": reference["status"],
                    "reference_result": reference,
                }
            )
        task_results.append({"task_id": task.id, "passed": all(item["passed"] for item in attempts), "attempts": attempts})
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "validate",
        "passed": passed,
        "repeat": repeat,
        "tasks": task_results,
    }
