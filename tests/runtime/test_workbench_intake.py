"""Black-box acceptance tests for natural-language Workbench intake."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from conftest import (
    WorkbenchCLI,
    assert_rejected,
    assert_schema_valid,
    assert_succeeded,
    find_event_store,
    persisted_bytes,
)


WORK_ID = "WB-INTAKE-001"
REQUEST = (
    "Workbench I want to implement a new feature. Currently there's an issue "
    "with manual validation. I want it like the test validation HTML docs at "
    "C:/examples/test-validation.html, with column separators and a row selector. "
    "We also need to pull data from multiple pages that append to a single table."
)
REFERENCES = (
    "C:/examples/test-validation.html",
    "docs/manual-validation.md",
)


def capture(
    cli: WorkbenchCLI,
    repo: Path,
    *,
    request: str = REQUEST,
    key: str = "runtime-test:capture-intake:001",
) -> object:
    args = [
        "--work-id", WORK_ID,
        "--request", request,
        "--idempotency-key", key,
        "--owner", "human:runtime-test",
        "--json",
    ]
    for reference in REFERENCES:
        args.extend(("--reference", reference))
    return cli.invoke("capture-intake", repo, args)


def start_from_intake(
    cli: WorkbenchCLI,
    repo: Path,
    *,
    from_intake: bool,
) -> object:
    args = [
        "--work-id", WORK_ID,
        "--title", "Improve manual validation table",
        "--outcome", "Users can select rows and combine paginated data in one clear table.",
        "--route", "brownfield-feature",
        "--destination", "locally-verified-implementation",
        "--idempotency-key", "runtime-test:start-from-intake:001",
        "--owner", "human:runtime-test",
        "--json",
    ]
    if from_intake:
        args.append("--from-intake")
    return cli.invoke("start", repo, args)


def read_json(result: object) -> dict:
    return json.loads(result.stdout)


def test_capture_preserves_free_form_request_and_references_exactly(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "free-form-intake"
    repo.mkdir()

    result = capture(workbench_cli, repo)

    assert_succeeded(result)
    intake_path = repo / ".workbench" / "work" / WORK_ID / "intake.json"
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    assert intake["raw_request"] == REQUEST
    assert intake["source_references"] == list(REFERENCES)
    assert intake["status"] == "captured"
    assert intake["route"] is None
    assert intake["planning_destination"] is None
    assert_schema_valid(intake, "workbench-intake.schema.json")
    projection = read_json(result)
    assert projection["status"] == "intake-draft"
    assert projection["route"] == "undetermined"
    assert projection["planning_destination"] == "undetermined"
    assert projection["frontier"]["agent_ready"]
    assert "inspect" in projection["next_action"]["description"].lower()


def test_intake_status_resume_and_next_survive_separate_processes(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "durable-intake"
    repo.mkdir()
    assert_succeeded(capture(workbench_cli, repo))
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()

    results = [
        workbench_cli.invoke(command, repo, ("--json",), cwd=unrelated)
        for command in ("status", "resume", "next")
    ]

    for result in results:
        assert_succeeded(result)
        projection = read_json(result)
        assert projection["work_id"] == WORK_ID
        assert projection["state_revision"] == 0
        assert projection["current_stage"] == "intake"
    assert read_json(results[1])["result"] == "resumed"


def test_capture_exact_retry_is_idempotent_and_conflict_is_atomic(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "intake-idempotency"
    repo.mkdir()
    first = capture(workbench_cli, repo)
    assert_succeeded(first)
    before = persisted_bytes(repo)

    retry = capture(workbench_cli, repo)
    assert_succeeded(retry)
    assert read_json(retry)["result"] == "idempotent"
    assert persisted_bytes(repo) == before

    conflict = capture(workbench_cli, repo, request=REQUEST + " Changed.")
    assert_rejected(conflict)
    assert persisted_bytes(repo) == before


def test_captured_intake_requires_explicit_bound_start_and_provenance(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "bound-intake"
    repo.mkdir()
    assert_succeeded(capture(workbench_cli, repo))
    before = persisted_bytes(repo)

    unbound = start_from_intake(workbench_cli, repo, from_intake=False)
    assert_rejected(unbound)
    assert persisted_bytes(repo) == before

    started = start_from_intake(workbench_cli, repo, from_intake=True)
    assert_succeeded(started)
    event = find_event_store(repo).read()[0]
    intake_path = repo / ".workbench" / "work" / WORK_ID / "intake.json"
    intake_reference = {
        "record_type": "external",
        "record_id": f"INTAKE-{WORK_ID}",
        "uri": "intake.json",
    }
    assert event["inputs"] == [intake_reference]
    assert event["cause"]["references"] == [intake_reference]
    assert event["payload"]["fingerprint_input"]["intake_sha256"] == hashlib.sha256(
        intake_path.read_bytes()
    ).hexdigest()
    replayed = workbench_cli.invoke("replay", repo, ("--json",))
    assert_succeeded(replayed)


def test_tampered_intake_blocks_projection_and_start(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "tampered-intake"
    repo.mkdir()
    assert_succeeded(capture(workbench_cli, repo))
    intake_path = repo / ".workbench" / "work" / WORK_ID / "intake.json"
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    intake["raw_request"] += " Hidden mutation."
    intake_path.write_text(json.dumps(intake, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(repo)

    status = workbench_cli.invoke("status", repo, ("--json",))
    started = start_from_intake(workbench_cli, repo, from_intake=True)

    assert_rejected(status)
    assert_rejected(started)
    assert persisted_bytes(repo) == before
