"""Adversarial acceptance tests for the file-backed Workbench runtime."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from conftest import (
    EventStore,
    WorkbenchCLI,
    assert_rejected,
    assert_succeeded,
    find_event_store,
    load_state,
    persisted_bytes,
    write_gate_receipt,
)


def test_fresh_brownfield_start_targets_locally_verified_implementation(
    started_repo: Path,
) -> None:
    _, state = load_state(started_repo)

    assert state["route_selection"]["route"] == "brownfield-feature"
    assert state["planning_destination"] == "locally-verified-implementation"
    assert state["current_stage"] == "intake"
    stage_ids = [stage["stage_id"] for stage in state["stages"]]
    assert "brownfield-reconnaissance" in stage_ids
    assert "implementation" in stage_ids
    assert "local-verification" in stage_ids


def test_fresh_start_and_replay_produce_equivalent_state(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    _, before = load_state(started_repo)

    result = workbench_cli.invoke("replay", started_repo)

    assert_succeeded(result)
    _, after = load_state(started_repo)
    assert after == before


def test_start_rejects_orphaned_work_directory_without_overwrite(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "orphaned-start"
    orphan = repo / ".workbench" / "work" / "WB-RUNTIME-001"
    orphan.mkdir(parents=True)
    (repo / ".workbench" / ".lock").write_bytes(b"\0")
    snapshot = orphan / "state.json"
    snapshot.write_text('{"orphaned":true}\n', encoding="utf-8")
    before = persisted_bytes(repo)

    result = workbench_cli.start(repo)

    assert_rejected(result)
    assert persisted_bytes(repo) == before


def test_status_resume_and_next_use_persisted_state_from_separate_processes(
    started_repo: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    _, state = load_state(started_repo)
    before = persisted_bytes(started_repo)
    unrelated_cwd = tmp_path / "unrelated-process-cwd"
    unrelated_cwd.mkdir()

    results = [
        workbench_cli.invoke(command, started_repo, cwd=unrelated_cwd)
        for command in ("status", "resume", "next")
    ]

    for result in results:
        assert_succeeded(result)
        assert result.output
    assert state["work_id"] in results[0].output
    assert state["current_stage"] in results[0].output
    assert state["work_id"] in results[1].output
    assert persisted_bytes(started_repo) == before


def test_matching_passed_gate_receipt_allows_legal_stage_advance(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
) -> None:
    repo, _, _ = advanced_repo
    _, state = load_state(repo)
    events = find_event_store(repo).read()

    assert state["current_stage"] == "outcome-framing"
    assert state["state_revision"] >= 2
    assert len(events) >= 2
    assert events[-1]["state_revision_after"] == state["state_revision"]
    assert events[-1]["state_revision_before"] + 1 == events[-1]["state_revision_after"]


@pytest.mark.parametrize(
    ("stage_id", "gate_id", "status"),
    [
        ("intake", "intake-recorded", "failed"),
        ("outcome-framing", "intake-recorded", "passed"),
        ("intake", "outcome-frame-recorded", "passed"),
    ],
    ids=("failed", "wrong-stage", "wrong-gate"),
)
def test_invalid_gate_receipts_are_rejected_without_partial_state(
    started_repo: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    stage_id: str,
    gate_id: str,
    status: str,
) -> None:
    _, state = load_state(started_repo)
    receipt = write_gate_receipt(
        tmp_path / f"{status}-{stage_id}-{gate_id}.json",
        state,
        stage_id=stage_id,
        gate_id=gate_id,
        status=status,
    )
    before = persisted_bytes(started_repo)

    result = workbench_cli.advance(
        started_repo,
        receipt=receipt,
        idempotency_key=f"runtime-test:invalid:{stage_id}:{gate_id}:{status}",
    )

    assert_rejected(result)
    assert persisted_bytes(started_repo) == before


def test_missing_gate_receipt_is_rejected_without_partial_state(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    before = persisted_bytes(started_repo)

    result = workbench_cli.advance(
        started_repo,
        receipt=None,
        idempotency_key="runtime-test:missing-gate-receipt",
    )

    assert_rejected(result)
    assert persisted_bytes(started_repo) == before


@pytest.mark.parametrize("invalid_field", ["evidence", "checked-by"])
def test_gate_receipt_rejects_invalid_reference_or_actor_atomically(
    started_repo: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    invalid_field: str,
) -> None:
    _, state = load_state(started_repo)
    receipt = write_gate_receipt(
        tmp_path / f"invalid-{invalid_field}.json",
        state,
        stage_id="intake",
        gate_id="intake-recorded",
    )
    value = json.loads(receipt.read_text(encoding="utf-8"))
    if invalid_field == "evidence":
        value["evidence"] = [{"record_type": "banana", "record_id": ""}]
    else:
        value["checked_by"] = "?"
    receipt.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(started_repo)

    result = workbench_cli.advance(
        started_repo,
        receipt=receipt,
        idempotency_key=f"runtime-test:invalid-{invalid_field}",
    )

    assert_rejected(result)
    assert persisted_bytes(started_repo) == before


def test_exact_operation_retry_is_idempotent(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
    workbench_cli: WorkbenchCLI,
) -> None:
    repo, receipt, _ = advanced_repo
    before = persisted_bytes(repo)

    retry = workbench_cli.advance(
        repo,
        receipt=receipt,
        idempotency_key="runtime-test:intake-to-outcome-framing",
    )

    assert_succeeded(retry)
    assert persisted_bytes(repo) == before


def test_conflicting_reuse_of_idempotency_key_is_rejected(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
    workbench_cli: WorkbenchCLI,
) -> None:
    repo, receipt, _ = advanced_repo
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["exit_gate"] = "outcome-frame-recorded"
    receipt.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(repo)

    conflict = workbench_cli.advance(
        repo,
        receipt=receipt,
        idempotency_key="runtime-test:intake-to-outcome-framing",
    )

    assert_rejected(conflict)
    assert persisted_bytes(repo) == before


def _mutate_sequence_gap(events: list[dict]) -> None:
    events[1]["sequence"] = events[0]["sequence"] + 2


def _mutate_sequence_duplicate(events: list[dict]) -> None:
    events[1]["sequence"] = events[0]["sequence"]


def _mutate_sequence_reorder(events: list[dict]) -> None:
    events[0], events[1] = events[1], events[0]


def _mutate_event_body(events: list[dict]) -> None:
    changes = events[0].get("changes", [])
    assert changes, "test setup requires replayable event changes"
    after = changes[0].get("after", {})
    assert after.get("present") is True, "test setup requires a present after-value"
    after["value"] = "adversarial-tamper"


def _mutate_change_target_id(events: list[dict]) -> None:
    changes = events[1].get("changes", [])
    assert changes, "test setup requires replayable transition changes"
    changes[0]["target"]["record_id"] = "WB-OTHER-001"


def _mutate_add_unsupported_event_field(events: list[dict]) -> None:
    events[0]["schema-invalid-extra"] = True


def _mutate_event_actor(events: list[dict]) -> None:
    events[0]["actor"] = {"actor_id": "agent:attacker", "kind": "agent"}


def _mutate_duplicate_gate_receipt(events: list[dict]) -> None:
    events[1]["payload"]["gate_receipt"]["result"] = "failed"


def _mutate_event_inputs(events: list[dict]) -> None:
    events[0]["inputs"] = [{"record_type": "work", "record_id": "WB-FALSE-INPUT"}]


@pytest.mark.parametrize(
    "mutator",
    [
        _mutate_sequence_gap,
        _mutate_sequence_duplicate,
        _mutate_sequence_reorder,
        _mutate_event_body,
        _mutate_change_target_id,
        _mutate_add_unsupported_event_field,
        _mutate_event_actor,
        _mutate_duplicate_gate_receipt,
        _mutate_event_inputs,
    ],
    ids=("gap", "duplicate", "reorder", "tamper", "wrong-target-id", "schema-invalid", "actor", "receipt-copy", "inputs"),
)
def test_replay_rejects_corrupt_event_stream(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
    workbench_cli: WorkbenchCLI,
    mutator,
) -> None:
    repo, _, _ = advanced_repo
    store = find_event_store(repo)
    events = store.read()
    assert len(events) >= 2, "test setup requires at least two persisted events"
    mutator(events)
    store.write(events)
    _, snapshot_before = load_state(repo)

    result = workbench_cli.invoke("replay", repo)

    assert_rejected(result)
    _, snapshot_after = load_state(repo)
    assert snapshot_after == snapshot_before


def _mutate_event_revision(events: list[dict]) -> None:
    events[1]["state_revision_before"] += 1


def _mutate_change_before_value(events: list[dict]) -> None:
    for event in events[1:]:
        for change in event.get("changes", []):
            before = change.get("before", {})
            if before.get("present") is True:
                before["value"] = "adversarial-wrong-before-value"
                return
    raise AssertionError("test setup requires a transition with a present before-value")


@pytest.mark.parametrize(
    "mutator",
    [_mutate_event_revision, _mutate_change_before_value],
    ids=("revision", "before-value"),
)
def test_replay_rejects_revision_or_before_value_mismatch(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
    workbench_cli: WorkbenchCLI,
    mutator,
) -> None:
    repo, _, _ = advanced_repo
    store = find_event_store(repo)
    events = store.read()
    assert len(events) >= 2
    mutator(events)
    store.write(events)
    _, snapshot_before = load_state(repo)

    result = workbench_cli.invoke("replay", repo)

    assert_rejected(result)
    _, snapshot_after = load_state(repo)
    assert snapshot_after == snapshot_before


@pytest.mark.parametrize("tamper_kind", ["stale-revision", "wrong-stage"])
def test_resume_rejects_stale_or_tampered_snapshot(
    advanced_repo: tuple[Path, Path, tuple[str, ...]],
    workbench_cli: WorkbenchCLI,
    tamper_kind: str,
) -> None:
    repo, _, _ = advanced_repo
    state_path, state = load_state(repo)
    if tamper_kind == "stale-revision":
        state["state_revision"] -= 1
    else:
        state["current_stage"] = "implementation"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    tampered_bytes = persisted_bytes(repo)

    result = workbench_cli.invoke("resume", repo)

    assert_rejected(result)
    assert persisted_bytes(repo) == tampered_bytes
