"""Black-box safety tests for recovery, capability gates, and completion."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from conftest import (
    WorkbenchCLI,
    assert_rejected,
    assert_repo_records_schema_valid,
    assert_schema_valid,
    assert_succeeded,
    find_event_store,
    load_state,
    persisted_bytes,
    write_gate_receipt,
)


EXIT_GATES = {
    "intake": "intake-recorded",
    "outcome-framing": "outcome-frame-recorded",
    "brownfield-reconnaissance": "current-state-and-blast-radius-evidenced",
    "standards-resolution": "applicable-profile-recorded",
    "implementation": "scoped-change-registered",
    "local-verification": "local-proof-disposition-recorded",
}


def utc_time(delta: timedelta = timedelta()) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


def advance_current_stage(
    cli: WorkbenchCLI,
    repo: Path,
    receipt_dir: Path,
    operation: str,
    *,
    proof_records: list[dict[str, Any]] | None = None,
    authorization_records: list[dict[str, Any]] | None = None,
):
    _, state = load_state(repo)
    stage = state["current_stage"]
    assert stage in EXIT_GATES, f"test fixture has no independent gate oracle for {stage}"
    receipt = write_gate_receipt(
        receipt_dir / f"{operation}.json",
        state,
        stage_id=stage,
        gate_id=EXIT_GATES[stage],
        proof_records=proof_records,
        authorization_records=authorization_records,
    )
    return cli.advance(
        repo,
        receipt=receipt,
        idempotency_key=f"runtime-safety:{operation}:{state['state_revision']}",
    )


def implementation_authorization(
    state: dict[str, Any],
    *,
    authorization_id: str = "AUTH-IMPLEMENT-001",
    work_id: str | None = None,
    target_stage: str = "implementation",
    expires: timedelta = timedelta(hours=1),
) -> dict[str, Any]:
    record_work_id = work_id or state["work_id"]
    record = {
        "record_type": "workbench-authorization",
        "schema_version": "0.1.0",
        "authorization_id": authorization_id,
        "work_id": record_work_id,
        "action": "implementation",
        "status": "granted",
        "scope": {
            "targets": [
                {
                    "kind": "stage",
                    "target_id": target_stage,
                    "stage_id": target_stage,
                }
            ],
            "constraints": [
                "Applies only to this work item and the named implementation stage."
            ],
        },
        "requested_by": {
            "actor_id": "agent:runtime-test",
            "kind": "agent",
        },
        "authority": {
            "actor_id": "human:runtime-test",
            "kind": "human",
        },
        "requested_at": utc_time(timedelta(minutes=-3)),
        "grant": {
            "granted_by": {
                "actor_id": "human:runtime-test",
                "kind": "human",
            },
            "granted_at": utc_time(timedelta(minutes=-2)),
            "expires_at": utc_time(expires),
        },
    }
    assert_schema_valid(record, "workbench-authorization.schema.json")
    return record


def closure_authorization(
    state: dict[str, Any],
    *,
    destination: str | None = None,
) -> dict[str, Any]:
    record = {
        "record_type": "workbench-authorization",
        "schema_version": "0.1.0",
        "authorization_id": "AUTH-CLOSE-001",
        "work_id": state["work_id"],
        "action": "closure",
        "status": "granted",
        "scope": {
            "targets": [
                {
                    "kind": "work",
                    "target_id": state["work_id"],
                    "planning_destination": destination or state["planning_destination"],
                }
            ],
            "constraints": [
                "Closes only the named planning destination; it does not claim release or business outcome."
            ],
        },
        "requested_by": {
            "actor_id": "agent:runtime-test",
            "kind": "agent",
        },
        "authority": {
            "actor_id": "human:runtime-test",
            "kind": "human",
        },
        "requested_at": utc_time(timedelta(minutes=-3)),
        "grant": {
            "granted_by": {
                "actor_id": "human:runtime-test",
                "kind": "human",
            },
            "granted_at": utc_time(timedelta(minutes=-2)),
            "expires_at": utc_time(timedelta(hours=1)),
        },
    }
    assert_schema_valid(record, "workbench-authorization.schema.json")
    return record


def local_implementation_proof(
    state: dict[str, Any],
    *,
    kind: str = "local-implementation",
) -> dict[str, Any]:
    record = {
        "record_type": "workbench-proof",
        "schema_version": "0.1.0",
        "proof_id": "PRF-LOCAL-001",
        "work_id": state["work_id"],
        "claim": "The scoped implementation behaves as specified in local verification.",
        "applicability": "required",
        "status": "passed",
        "owner": {
            "actor_id": "agent:runtime-test",
            "kind": "agent",
        },
        "required_proof": [
            {
                "requirement_id": "REQ-LOCAL-001",
                "kind": kind,
                "description": "Exercise the implemented behavior in its local integration context.",
                "acceptance_criteria": [
                    "The bounded behavior passes its independent local oracle."
                ],
                "oracle_requirement": "An automated oracle independent of the implementation path reports a non-vacuous result.",
            }
        ],
        "achieved_proof": [
            {
                "requirement_id": "REQ-LOCAL-001",
                "kind": kind,
                "result": "passed",
                "oracle": {
                    "kind": "automated-independent",
                    "description": "The integration check exercises the public behavior and asserts its expected result.",
                },
                "evidence": [
                    {
                        "record_type": "work",
                        "record_id": state["work_id"],
                    }
                ],
                "non_vacuity_check": "The oracle observed at least one executed scenario and a concrete assertion.",
                "observed_by": {
                    "actor_id": "agent:runtime-test",
                    "kind": "agent",
                },
                "observed_at": utc_time(timedelta(minutes=-1)),
                "limitations": [
                    "This is local implementation proof, not deployed-behavior proof."
                ],
            }
        ],
        "created_at": utc_time(timedelta(minutes=-2)),
        "updated_at": utc_time(timedelta(minutes=-1)),
    }
    assert_schema_valid(record, "workbench-proof.schema.json")
    return record


@pytest.fixture
def fast_lane_repo(tmp_path: Path, workbench_cli: WorkbenchCLI) -> Path:
    repo = tmp_path / "fast-lane-repo"
    repo.mkdir()
    result = workbench_cli.start(
        repo,
        route="small-change-fast-lane",
        destination="locally-verified-implementation",
    )
    assert_succeeded(result)
    assert_repo_records_schema_valid(repo)
    return repo


@pytest.fixture
def repo_before_implementation(
    fast_lane_repo: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> Path:
    for index, expected_stage in enumerate(
        ("intake", "outcome-framing", "brownfield-reconnaissance"),
        start=1,
    ):
        _, state = load_state(fast_lane_repo)
        assert state["current_stage"] == expected_stage
        assert_succeeded(
            advance_current_stage(
                workbench_cli,
                fast_lane_repo,
                tmp_path,
                f"reach-implementation-boundary-{index}",
            )
        )
        assert_repo_records_schema_valid(fast_lane_repo)
    _, state = load_state(fast_lane_repo)
    assert state["current_stage"] == "standards-resolution"
    return fast_lane_repo


@pytest.fixture
def repo_at_local_verification(
    repo_before_implementation: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> Path:
    _, state = load_state(repo_before_implementation)
    authorization = implementation_authorization(state)
    assert_succeeded(
        advance_current_stage(
            workbench_cli,
            repo_before_implementation,
            tmp_path,
            "enter-implementation",
            authorization_records=[authorization],
        )
    )
    _, state = load_state(repo_before_implementation)
    assert state["current_stage"] == "implementation"
    assert_succeeded(
        advance_current_stage(
            workbench_cli,
            repo_before_implementation,
            tmp_path,
            "enter-local-verification",
        )
    )
    _, state = load_state(repo_before_implementation)
    assert state["current_stage"] == "local-verification"
    assert_repo_records_schema_valid(repo_before_implementation)
    return repo_before_implementation


def test_next_command_rolls_forward_recoverable_transaction(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    root = started_repo / ".workbench"
    target = root / "active-work.json"
    before = target.read_bytes()
    after = before + b"\n"
    transaction_id = "0123456789abcdef0123456789abcdef"
    temporary = root / f".active-work.json.{transaction_id}.tmp"
    temporary.write_bytes(after)
    journal = {
        "version": 1,
        "transaction_id": transaction_id,
        "files": [
            {
                "target": "active-work.json",
                "temporary": temporary.name,
                "before_sha256": hashlib.sha256(before).hexdigest(),
                "after_sha256": hashlib.sha256(after).hexdigest(),
            }
        ],
    }
    journal_path = root / ".transaction.json"
    journal_path.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")

    result = workbench_cli.invoke("status", started_repo)

    assert_succeeded(result)
    assert target.read_bytes() == after
    assert not journal_path.exists()
    assert not temporary.exists()
    assert_repo_records_schema_valid(started_repo)


def test_stale_lock_file_does_not_prevent_transaction_recovery(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    root = started_repo / ".workbench"
    (root / ".lock").write_text(
        json.dumps({"pid": 99999999, "created_at": "2000-01-01T00:00:00Z"}),
        encoding="utf-8",
    )
    target = root / "active-work.json"
    before = target.read_bytes()
    after = before + b"\n"
    transaction_id = "fedcba9876543210fedcba9876543210"
    temporary = root / f".active-work.json.{transaction_id}.tmp"
    temporary.write_bytes(after)
    (root / ".transaction.json").write_text(
        json.dumps(
            {
                "version": 1,
                "transaction_id": transaction_id,
                "files": [
                    {
                        "target": "active-work.json",
                        "temporary": temporary.name,
                        "before_sha256": hashlib.sha256(before).hexdigest(),
                        "after_sha256": hashlib.sha256(after).hexdigest(),
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = workbench_cli.invoke("status", started_repo)

    assert_succeeded(result)
    assert target.read_bytes() == after
    assert not (root / ".transaction.json").exists()
    assert not temporary.exists()


def test_malformed_later_recovery_entry_cannot_partially_apply_earlier_entry(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    root = started_repo / ".workbench"
    target = root / "active-work.json"
    before = target.read_bytes()
    after = b'{"work_id":"WB-OTHER-001"}\n'
    transaction_id = "11223344556677889900aabbccddeeff"
    temporary = root / f".active-work.json.{transaction_id}.tmp"
    temporary.write_bytes(after)
    journal = {
        "version": 1,
        "transaction_id": transaction_id,
        "files": [
            {
                "target": "active-work.json",
                "temporary": temporary.name,
                "before_sha256": hashlib.sha256(before).hexdigest(),
                "after_sha256": hashlib.sha256(after).hexdigest(),
            },
            {
                "target": "../escaped.json",
                "temporary": f".escaped.json.{transaction_id}.tmp",
                "before_sha256": None,
                "after_sha256": "0" * 64,
            },
        ],
    }
    (root / ".transaction.json").write_text(json.dumps(journal) + "\n", encoding="utf-8")

    result = workbench_cli.invoke("status", started_repo)

    assert_rejected(result)
    assert target.read_bytes() == before
    assert temporary.read_bytes() == after
    assert (root / ".transaction.json").exists()


def test_recovery_rejects_duplicate_paths_before_mutation(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    root = started_repo / ".workbench"
    target = root / "active-work.json"
    before = target.read_bytes()
    after = before + b"\n"
    transaction_id = "00112233445566778899aabbccddeeff"
    temporary = root / f".active-work.json.{transaction_id}.tmp"
    temporary.write_bytes(after)
    entry = {
        "target": "active-work.json",
        "temporary": temporary.name,
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "after_sha256": hashlib.sha256(after).hexdigest(),
    }
    (root / ".transaction.json").write_text(
        json.dumps({"version": 1, "transaction_id": transaction_id, "files": [entry, entry]}) + "\n",
        encoding="utf-8",
    )

    result = workbench_cli.invoke("status", started_repo)

    assert_rejected(result)
    assert target.read_bytes() == before
    assert temporary.read_bytes() == after


@pytest.mark.parametrize("escape", ["target", "temporary"])
def test_recovery_rejects_paths_that_escape_workbench_root(
    started_repo: Path,
    workbench_cli: WorkbenchCLI,
    escape: str,
) -> None:
    root = started_repo / ".workbench"
    target = root / "active-work.json"
    payload = target.read_bytes() + b"\n"
    transaction_id = "abcdef0123456789abcdef0123456789"
    internal_temp = root / f".active-work.json.{transaction_id}.tmp"
    internal_temp.write_bytes(payload)
    entry = {
        "target": "../escaped-target.json" if escape == "target" else "active-work.json",
        "temporary": "../escaped-temporary.json" if escape == "temporary" else internal_temp.name,
        "before_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "after_sha256": hashlib.sha256(payload).hexdigest(),
    }
    journal_path = root / ".transaction.json"
    journal_path.write_text(
        json.dumps(
            {
                "version": 1,
                "transaction_id": transaction_id,
                "files": [entry],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    before = persisted_bytes(started_repo)

    result = workbench_cli.invoke("status", started_repo)

    assert_rejected(result)
    assert persisted_bytes(started_repo) == before
    assert not (started_repo / "escaped-target.json").exists()
    assert not (started_repo / "escaped-temporary.json").exists()


@pytest.mark.parametrize(
    "grant_kind",
    ["missing", "expired", "wrong-work", "wrong-stage", "schema-invalid"],
)
def test_implementation_boundary_rejects_invalid_grants_atomically(
    repo_before_implementation: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    grant_kind: str,
) -> None:
    _, state = load_state(repo_before_implementation)
    authorizations: list[dict[str, Any]] = []
    if grant_kind == "expired":
        authorizations = [
            implementation_authorization(
                state,
                authorization_id="AUTH-IMPLEMENT-EXPIRED",
                expires=timedelta(minutes=-1),
            )
        ]
    elif grant_kind == "wrong-work":
        authorizations = [
            implementation_authorization(
                state,
                authorization_id="AUTH-IMPLEMENT-WRONG-WORK",
                work_id="WB-OTHER-001",
            )
        ]
    elif grant_kind == "wrong-stage":
        authorizations = [
            implementation_authorization(
                state,
                authorization_id="AUTH-IMPLEMENT-WRONG-STAGE",
                target_stage="local-verification",
            )
        ]
    elif grant_kind == "schema-invalid":
        authorizations = [{
            "record_type": "workbench-authorization",
            "authorization_id": "AUTH-IMPLEMENT-MALFORMED",
            "work_id": state["work_id"],
            "action": "implementation",
            "status": "granted",
        }]
    before = persisted_bytes(repo_before_implementation)

    result = advance_current_stage(
        workbench_cli,
        repo_before_implementation,
        tmp_path,
        f"reject-implementation-{grant_kind}",
        authorization_records=authorizations,
    )

    assert_rejected(result)
    assert persisted_bytes(repo_before_implementation) == before
    _, after = load_state(repo_before_implementation)
    assert after["current_stage"] == "standards-resolution"


def test_valid_human_grant_allows_entry_to_implementation(
    repo_before_implementation: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    _, state = load_state(repo_before_implementation)
    authorization = implementation_authorization(state)

    result = advance_current_stage(
        workbench_cli,
        repo_before_implementation,
        tmp_path,
        "allow-implementation",
        authorization_records=[authorization],
    )

    assert_succeeded(result)
    _, after = load_state(repo_before_implementation)
    assert after["current_stage"] == "implementation"
    assert authorization["authorization_id"] in after["authorization_ids"]
    assert_repo_records_schema_valid(repo_before_implementation)


@pytest.mark.parametrize(
    "completion_evidence",
    [
        "missing-proof",
        "wrong-proof-kind",
        "missing-closure",
        "wrong-destination-closure",
        "schema-invalid-proof",
        "schema-invalid-closure",
        "mismatched-proof-kind",
    ],
)
def test_local_completion_rejects_incomplete_or_mismatched_evidence_atomically(
    repo_at_local_verification: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    completion_evidence: str,
) -> None:
    _, state = load_state(repo_at_local_verification)
    proofs = [local_implementation_proof(state)]
    authorizations = [closure_authorization(state)]
    if completion_evidence == "missing-proof":
        proofs = []
    elif completion_evidence == "wrong-proof-kind":
        proofs = [local_implementation_proof(state, kind="artifact-validity")]
    elif completion_evidence == "missing-closure":
        authorizations = []
    elif completion_evidence == "wrong-destination-closure":
        authorizations = [closure_authorization(state, destination="released-software")]
    elif completion_evidence == "schema-invalid-proof":
        proofs = [{
            "record_type": "workbench-proof",
            "proof_id": "PRF-LOCAL-MALFORMED",
            "work_id": state["work_id"],
            "status": "passed",
            "achieved_proof": [{"kind": "local-implementation", "result": "passed"}],
        }]
    elif completion_evidence == "schema-invalid-closure":
        authorizations = [{
            "record_type": "workbench-authorization",
            "authorization_id": "AUTH-CLOSE-MALFORMED",
            "work_id": state["work_id"],
            "action": "closure",
            "status": "granted",
        }]
    else:
        mismatched = local_implementation_proof(state)
        mismatched["required_proof"][0]["kind"] = "artifact-validity"
        proofs = [mismatched]
    before = persisted_bytes(repo_at_local_verification)

    result = advance_current_stage(
        workbench_cli,
        repo_at_local_verification,
        tmp_path,
        f"reject-completion-{completion_evidence}",
        proof_records=proofs,
        authorization_records=authorizations,
    )

    assert_rejected(result)
    assert persisted_bytes(repo_at_local_verification) == before
    _, after = load_state(repo_at_local_verification)
    assert after["current_stage"] == "local-verification"
    assert after["status"] == "active"


def test_matching_local_proof_and_exact_closure_complete_at_destination_stage(
    repo_at_local_verification: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    _, state = load_state(repo_at_local_verification)
    proof = local_implementation_proof(state)
    closure = closure_authorization(state)

    result = advance_current_stage(
        workbench_cli,
        repo_at_local_verification,
        tmp_path,
        "complete-locally-verified-destination",
        proof_records=[proof],
        authorization_records=[closure],
    )

    assert_succeeded(result)
    _, completed = load_state(repo_at_local_verification)
    assert completed["status"] == "completed-for-destination"
    assert completed["current_stage"] == "local-verification"
    stages = {stage["stage_id"]: stage for stage in completed["stages"]}
    assert stages["local-verification"]["status"] == "complete"
    assert stages["release"]["status"] == "pending"
    assert completed["completion"]["proof_ids"] == [proof["proof_id"]]
    assert completed["completion"]["authorized_by"] == closure["authorization_id"]
    assert proof["proof_id"] in completed["proof_ids"]
    assert closure["authorization_id"] in completed["authorization_ids"]
    assert find_event_store(repo_at_local_verification).read()[-1]["state_revision_after"] == completed["state_revision"]
    assert_repo_records_schema_valid(repo_at_local_verification)


@pytest.mark.parametrize("duplicate_kind", ["proof", "authorization"])
def test_completion_rejects_duplicate_record_ids_atomically(
    repo_at_local_verification: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    duplicate_kind: str,
) -> None:
    _, state = load_state(repo_at_local_verification)
    proof = local_implementation_proof(state)
    closure = closure_authorization(state)
    proofs = [proof]
    authorizations = [closure]
    if duplicate_kind == "proof":
        duplicate = copy.deepcopy(proof)
        duplicate["claim"] = "A different claim must not reuse the same proof identity."
        proofs.append(duplicate)
    else:
        duplicate = copy.deepcopy(closure)
        duplicate["scope"]["constraints"] = ["A different grant must not reuse the same authorization identity."]
        authorizations.append(duplicate)
    before = persisted_bytes(repo_at_local_verification)

    result = advance_current_stage(
        workbench_cli,
        repo_at_local_verification,
        tmp_path,
        f"reject-duplicate-{duplicate_kind}",
        proof_records=proofs,
        authorization_records=authorizations,
    )

    assert_rejected(result)
    assert persisted_bytes(repo_at_local_verification) == before
