"""Black-box acceptance tests for Workbench v0.2 intake finalization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from conftest import (
    WorkbenchCLI,
    assert_rejected,
    assert_schema_valid,
    assert_succeeded,
    find_event_store,
    load_state,
    persisted_bytes,
)
from test_workbench_intake import REQUEST, WORK_ID, capture


ALL_ACTIONS = {
    "decision-delegation",
    "repository-mutation",
    "tracker-publication",
    "implementation",
    "commit",
    "deployment",
    "closure",
}


def routing_input(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "title": "Improve manual validation table",
        "desired_outcome": (
            "Users can select rows and combine paginated data in one clear table."
        ),
        "business_basis": "technical-only",
        "solution_context": "brownfield",
        "engagement_intent": "implement",
        "planning_destination": "locally-verified-implementation",
        "execution_lane": "fast",
        "runtime_route": "small-change-fast-lane",
        "rationale": (
            "The request changes an existing interface and asks for local implementation; "
            "the named UI and data behavior make a bounded fast lane plausible."
        ),
        "evidence_references": [
            "C:/examples/test-validation.html",
            "docs/manual-validation.md",
        ],
        "facts": [
            {
                "statement": "The requested table combines rows loaded from multiple pages.",
                "source_references": ["captured-intake"],
            }
        ],
        "constraints": ["Do not claim deployment or release."],
        "acceptance_evidence": [
            "A local test demonstrates column separators, row selection, and appended pages."
        ],
        "assumptions": [
            "Repository inspection confirms the change remains within one execution context."
        ],
        "unresolved_questions": [],
        "stage_recommendations": [
            {
                "stage_id": "brownfield-reconnaissance",
                "applicability": "applicable",
                "reason": "Existing UI and pagination behavior must be bounded before editing.",
                "evidence_references": ["captured-intake"],
            },
            {
                "stage_id": "data-model-design",
                "applicability": "not-applicable",
                "reason": "Repository inspection found no change to persisted data semantics.",
                "evidence_references": ["captured-intake"],
            }
        ],
        "authorization_boundary": {
            "granted_actions": ["repository-mutation", "implementation"],
            "withheld_actions": [
                "decision-delegation",
                "tracker-publication",
                "commit",
                "deployment",
                "closure",
            ],
        },
        "recommendation": {
            "choice": "Use the bounded brownfield fast lane.",
            "rationale": "It reaches local proof without implying release.",
            "assumptions": ["Reconnaissance confirms a contained blast radius."],
            "tradeoffs": ["The route must expand if inspection finds a material dependency."],
            "confidence": "medium",
        },
    }
    value.update(overrides)
    return value


def write_input(path: Path, value: dict[str, Any]) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def finalize(
    cli: WorkbenchCLI,
    repo: Path,
    input_path: Path,
    *,
    key: str = "runtime-test:finalize-intake:001",
):
    return cli.invoke(
        "finalize-intake",
        repo,
        (
            "--work-id",
            WORK_ID,
            "--routing-input",
            str(input_path),
            "--idempotency-key",
            key,
            "--owner",
            "human:runtime-test",
            "--json",
        ),
    )


def revise(
    cli: WorkbenchCLI,
    repo: Path,
    input_path: Path,
    *,
    expected_revision: int = 1,
    key: str = "runtime-test:revise-routing:001",
):
    return cli.invoke(
        "revise-routing",
        repo,
        (
            "--work-id",
            WORK_ID,
            "--routing-input",
            str(input_path),
            "--expected-routing-revision",
            str(expected_revision),
            "--idempotency-key",
            key,
            "--owner",
            "human:runtime-test",
            "--json",
        ),
    )


def start_from_routing(
    cli: WorkbenchCLI,
    repo: Path,
    *,
    route: str = "small-change-fast-lane",
    destination: str = "locally-verified-implementation",
    from_routing: bool = True,
    from_intake: bool = False,
):
    args = [
        "--work-id",
        WORK_ID,
        "--title",
        "Improve manual validation table",
        "--outcome",
        "Users can select rows and combine paginated data in one clear table.",
        "--route",
        route,
        "--destination",
        destination,
        "--idempotency-key",
        "runtime-test:start-from-routing:001",
        "--owner",
        "human:runtime-test",
        "--json",
    ]
    if from_routing:
        args.append("--from-routing")
    if from_intake:
        args.append("--from-intake")
    return cli.invoke("start", repo, args)


def captured_repo(tmp_path: Path, cli: WorkbenchCLI, name: str) -> Path:
    repo = tmp_path / name
    repo.mkdir()
    assert_succeeded(capture(cli, repo))
    return repo


def read_result(result: Any) -> dict[str, Any]:
    return json.loads(result.stdout)


def test_proposal_destination_includes_applicable_data_model_design(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "proposal-data-model")
    value = routing_input(
        engagement_intent="explore",
        planning_destination="proposal",
        execution_lane="full",
        runtime_route=None,
        authorization_boundary={"granted_actions": [], "withheld_actions": sorted(ALL_ACTIONS)},
        stage_recommendations=[
            {
                "stage_id": "data-model-design",
                "applicability": "applicable",
                "reason": "The requested proposal is a data-model audit.",
                "evidence_references": ["captured-intake"],
            }
        ],
    )

    result = finalize(
        workbench_cli,
        repo,
        write_input(tmp_path / "proposal-data-model.json", value),
    )

    assert_succeeded(result)
    receipt = json.loads(
        (repo / ".workbench" / "work" / WORK_ID / "routing.json").read_text(encoding="utf-8")
    )
    design = next(
        phase for phase in receipt["compiled_plan"]["phases"]
        if phase["phase_id"] == "design-decide"
    )
    assert design["checkpoint_stage"] == "proposal"
    assert [item["stage_id"] for item in design["activities"] if item["applicability"] == "applicable"] == [
        "data-model-design",
        "proposal",
    ]


def test_finalize_persists_valid_receipt_and_projects_ready_state(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-ready")
    input_path = write_input(tmp_path / "routing-ready.json", routing_input())
    intake_path = repo / ".workbench" / "work" / WORK_ID / "intake.json"
    intake_before = intake_path.read_bytes()

    result = finalize(workbench_cli, repo, input_path)

    assert_succeeded(result)
    receipt_path = repo / ".workbench" / "work" / WORK_ID / "routing.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert_schema_valid(receipt, "workbench-routing-receipt.schema.json")
    assert receipt["business_basis"] == "technical-only"
    assert receipt["solution_context"] == "brownfield"
    assert receipt["engagement_intent"] == "implement"
    assert receipt["execution_lane"] == "fast"
    assert set(receipt["authorization_boundary"]["granted_actions"]) | set(
        receipt["authorization_boundary"]["withheld_actions"]
    ) == ALL_ACTIONS
    assert receipt["intake"]["sha256"]["value"] == hashlib.sha256(
        intake_before
    ).hexdigest()
    assert intake_path.read_bytes() == intake_before

    for command in ("status", "resume", "next"):
        projection = workbench_cli.invoke(command, repo, ("--json",))
        assert_succeeded(projection)
        view = read_result(projection)
        assert view["status"] == "routing-ready"
        assert view["routing_profile"] == {
            "business_basis": "technical-only",
            "solution_context": "brownfield",
            "engagement_intent": "implement",
            "planning_destination": "locally-verified-implementation",
            "execution_lane": "fast",
            "runtime_route": "small-change-fast-lane",
        }
        assert view["frontier"]["agent_ready"]


def test_finalize_retry_is_idempotent_and_conflict_is_atomic(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-idempotency")
    input_path = write_input(tmp_path / "routing.json", routing_input())
    assert_succeeded(finalize(workbench_cli, repo, input_path))
    before = persisted_bytes(repo)

    retry = finalize(workbench_cli, repo, input_path)
    assert_succeeded(retry)
    assert read_result(retry)["result"] == "idempotent"
    assert persisted_bytes(repo) == before

    write_input(input_path, routing_input(rationale="A conflicting rationale."))
    conflict = finalize(workbench_cli, repo, input_path)
    assert_rejected(conflict)
    assert persisted_bytes(repo) == before


def test_material_question_blocks_start_and_appears_on_user_frontier(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-question")
    value = routing_input(
        unresolved_questions=[
            {
                "question": "Should row selection persist across loaded pages?",
                "why_material": "The answer changes selection state and acceptance tests.",
                "owner": {"actor_id": "human:runtime-test", "kind": "human"},
            }
        ]
    )
    assert_succeeded(finalize(workbench_cli, repo, write_input(tmp_path / "question.json", value)))

    status = workbench_cli.invoke("status", repo, ("--json",))
    assert_succeeded(status)
    projection = read_result(status)
    assert projection["status"] == "routing-blocked"
    assert projection["frontier"]["user_decisions"][0]["question"].startswith(
        "Should row selection"
    )
    before = persisted_bytes(repo)
    assert_rejected(start_from_routing(workbench_cli, repo))
    assert persisted_bytes(repo) == before


def test_answered_question_revises_same_item_and_preserves_original_receipt(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-revision")
    question = "Should row selection persist across loaded pages?"
    initial = routing_input(
        unresolved_questions=[
            {
                "question": question,
                "why_material": "The answer changes selection state and acceptance tests.",
                "owner": {"actor_id": "human:runtime-test", "kind": "human"},
            }
        ]
    )
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "routing-revision-initial.json", initial),
        )
    )
    folder = repo / ".workbench" / "work" / WORK_ID
    original_path = folder / "routing.json"
    original_bytes = original_path.read_bytes()

    updated = routing_input(
        unresolved_questions=[],
        revision_reason="The user answered the material routing question.",
        resolved_questions=[
            {
                "question": question,
                "answer": "Yes. Selection must persist across every loaded page.",
                "source_references": ["user-response:2026-09-14"],
            }
        ],
    )
    revision_input = write_input(tmp_path / "routing-revision-updated.json", updated)
    result = revise(workbench_cli, repo, revision_input)

    assert_succeeded(result)
    view = read_result(result)
    assert view["result"] == "revised"
    assert view["work_id"] == WORK_ID
    assert view["routing_revision"] == 2
    assert view["status"] == "routing-ready"
    assert view["human_control"]["decisions"][0]["answer"].startswith("Yes.")
    assert original_path.read_bytes() == original_bytes
    plain_status = workbench_cli.invoke("status", repo)
    assert_succeeded(plain_status)
    assert "routing revision 2" in plain_status.stdout

    revision_path = folder / "routing-revisions" / "000002.json"
    revision_record = json.loads(revision_path.read_text(encoding="utf-8"))
    assert_schema_valid(revision_record, "workbench-routing-receipt.schema.json")
    assert revision_record["supersedes"]["sha256"]["value"] == hashlib.sha256(
        original_bytes
    ).hexdigest()

    retry_before = persisted_bytes(repo)
    retry = revise(workbench_cli, repo, revision_input)
    assert_succeeded(retry)
    assert read_result(retry)["result"] == "idempotent"
    assert persisted_bytes(repo) == retry_before

    assert_succeeded(start_from_routing(workbench_cli, repo))
    event = find_event_store(repo).read()[0]
    assert [item["uri"] for item in event["inputs"]] == [
        "intake.json",
        "routing-revisions/000002.json",
    ]
    assert event["payload"]["fingerprint_input"]["routing_sha256"] == hashlib.sha256(
        revision_path.read_bytes()
    ).hexdigest()
    assert_succeeded(workbench_cli.invoke("replay", repo, ("--json",)))

    before_rejected_revision = persisted_bytes(repo)
    assert_rejected(
        revise(
            workbench_cli,
            repo,
            revision_input,
            expected_revision=2,
            key="runtime-test:revise-routing:after-start",
        )
    )
    assert persisted_bytes(repo) == before_rejected_revision


def test_routing_revision_requires_explicit_answers_for_removed_questions(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-revision-missing-answer")
    question = "Which agency role owns the final review?"
    initial = routing_input(
        unresolved_questions=[
            {
                "question": question,
                "why_material": "The owner changes permissions and workflow handoffs.",
                "owner": {"actor_id": "human:runtime-test", "kind": "human"},
            }
        ]
    )
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "routing-missing-answer-initial.json", initial),
        )
    )
    before = persisted_bytes(repo)
    incomplete = routing_input(
        unresolved_questions=[],
        revision_reason="The routing profile was updated without recording the answer.",
        resolved_questions=[],
    )

    result = revise(
        workbench_cli,
        repo,
        write_input(tmp_path / "routing-missing-answer-updated.json", incomplete),
    )

    assert_rejected(result)
    assert "record an answer" in result.output
    assert persisted_bytes(repo) == before


def test_routing_revision_history_detects_predecessor_tampering(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-revision-tamper")
    initial = routing_input()
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "routing-tamper-initial.json", initial),
        )
    )
    updated = routing_input(
        revision_reason="New repository evidence refined the route.",
        resolved_questions=[],
    )
    assert_succeeded(
        revise(
            workbench_cli,
            repo,
            write_input(tmp_path / "routing-tamper-updated.json", updated),
        )
    )
    original_path = repo / ".workbench" / "work" / WORK_ID / "routing.json"
    original = json.loads(original_path.read_text(encoding="utf-8"))
    original["rationale"] = "Tampered rationale."
    original_path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(repo)

    assert_rejected(workbench_cli.invoke("status", repo, ("--json",)))
    assert_rejected(start_from_routing(workbench_cli, repo))
    assert persisted_bytes(repo) == before


def test_pre_v04_routing_receipt_can_be_revised_without_replacement(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "legacy-routing-revision")
    question = "Which user group owns the primary journey?"
    initial = routing_input(
        unresolved_questions=[
            {
                "question": question,
                "why_material": "The answer changes the product workflow and permissions.",
                "owner": {"actor_id": "human:runtime-test", "kind": "human"},
            }
        ]
    )
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "legacy-routing-initial.json", initial),
        )
    )
    original_path = repo / ".workbench" / "work" / WORK_ID / "routing.json"
    legacy = json.loads(original_path.read_text(encoding="utf-8"))
    legacy["schema_version"] = "0.3.0"
    legacy.pop("routing_revision")
    fingerprint_payload = {
        key: value
        for key, value in legacy.items()
        if key not in {"created_at", "input_fingerprint"}
    }
    legacy["input_fingerprint"]["value"] = hashlib.sha256(
        json.dumps(
            fingerprint_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    original_path.write_text(
        json.dumps(legacy, indent=2) + "\n", encoding="utf-8"
    )
    legacy_bytes = original_path.read_bytes()

    updated = routing_input(
        revision_reason="The pre-v0.4 receipt needs a clarified rationale.",
        unresolved_questions=[],
        resolved_questions=[
            {
                "question": question,
                "answer": "Insurance agents own the primary journey; administrators support it.",
                "source_references": ["user-response:2026-09-14"],
            }
        ],
    )
    result = revise(
        workbench_cli,
        repo,
        write_input(tmp_path / "legacy-routing-updated.json", updated),
    )

    assert_succeeded(result)
    assert read_result(result)["routing_revision"] == 2
    assert original_path.read_bytes() == legacy_bytes


def test_undetermined_stage_applicability_is_persisted_and_blocks_start(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-undetermined-stage")
    value = routing_input()
    value["stage_recommendations"][0]["applicability"] = "undetermined"
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "undetermined-stage.json", value),
        )
    )

    projection = read_result(workbench_cli.invoke("next", repo, ("--json",)))
    assert projection["status"] == "routing-blocked"
    assert projection["frontier"]["agent_ready"][0]["stage_id"] == (
        "brownfield-reconnaissance"
    )
    before = persisted_bytes(repo)
    assert_rejected(start_from_routing(workbench_cli, repo))
    assert persisted_bytes(repo) == before


def test_greenfield_profile_compiles_and_starts_without_a_legacy_route(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-greenfield")
    value = routing_input(
        business_basis="supplied-requirements",
        solution_context="greenfield",
        execution_lane="full",
        runtime_route=None,
        rationale="This is a new software system with no existing implementation.",
    )
    assert_succeeded(finalize(workbench_cli, repo, write_input(tmp_path / "greenfield.json", value)))

    status = workbench_cli.invoke("status", repo, ("--json",))
    assert_succeeded(status)
    projection = read_result(status)
    assert projection["status"] == "routing-ready"
    assert projection["routing_profile"]["solution_context"] == "greenfield"
    assert projection["routing_profile"]["runtime_route"] is None
    assert projection["route"] == "profile-compiled"
    assert not projection["frontier"]["external_blockers"]
    start = workbench_cli.invoke(
        "start",
        repo,
        (
            "--work-id", WORK_ID,
            "--idempotency-key", "runtime-test:start-greenfield:001",
            "--from-routing",
            "--json",
        ),
    )
    assert_succeeded(start)
    started = read_result(start)
    assert started["route"] == "profile-compiled"
    assert started["current_stage"] == "outcome-framing"


def test_database_backed_profile_makes_data_model_the_design_checkpoint(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-data-model")
    value = routing_input(
        stage_recommendations=[
            {
                "stage_id": "brownfield-reconnaissance",
                "applicability": "applicable",
                "reason": "Existing persistence behavior must be inspected before editing.",
                "evidence_references": ["captured-intake"],
            },
            {
                "stage_id": "solution-architecture",
                "applicability": "applicable",
                "reason": "The feature changes service and persistence boundaries.",
                "evidence_references": ["captured-intake"],
            },
            {
                "stage_id": "data-model-design",
                "applicability": "applicable",
                "reason": "The database schema and persisted invariants will change.",
                "evidence_references": ["captured-intake"],
            },
        ]
    )
    result = finalize(
        workbench_cli,
        repo,
        write_input(tmp_path / "data-model.json", value),
    )

    assert_succeeded(result)
    routing = json.loads(
        (repo / ".workbench" / "work" / WORK_ID / "routing.json").read_text(encoding="utf-8")
    )
    design = next(
        phase for phase in routing["compiled_plan"]["phases"]
        if phase["phase_id"] == "design-decide"
    )
    assert design["checkpoint_stage"] == "data-model-design"


def test_software_profile_without_data_model_disposition_is_rejected_atomically(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-missing-data-model")
    value = routing_input()
    value["stage_recommendations"] = [
        item for item in value["stage_recommendations"]
        if item["stage_id"] != "data-model-design"
    ]
    before = persisted_bytes(repo)

    result = finalize(
        workbench_cli,
        repo,
        write_input(tmp_path / "missing-data-model.json", value),
    )

    assert_rejected(result)
    assert "must explicitly classify data-model-design" in result.output
    assert persisted_bytes(repo) == before


@pytest.mark.parametrize(
    ("route", "destination"),
    [
        ("brownfield-feature", "locally-verified-implementation"),
        ("small-change-fast-lane", "implementation-plan"),
    ],
)
def test_bound_start_rejects_route_or_destination_mismatch(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    route: str,
    destination: str,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, f"mismatch-{route}-{destination}")
    assert_succeeded(finalize(workbench_cli, repo, write_input(tmp_path / f"{route}.json", routing_input())))
    before = persisted_bytes(repo)

    result = start_from_routing(
        workbench_cli,
        repo,
        route=route,
        destination=destination,
    )

    assert_rejected(result)
    assert persisted_bytes(repo) == before


@pytest.mark.parametrize(
    "defect",
    ["overlap", "incomplete", "duplicate-stage", "unknown-stage", "profile-route-mismatch"],
)
def test_finalize_rejects_unsafe_or_ambiguous_routing_atomically(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
    defect: str,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, f"invalid-{defect}")
    value = routing_input()
    if defect == "overlap":
        value["authorization_boundary"]["withheld_actions"].append("implementation")
    elif defect == "incomplete":
        value["authorization_boundary"]["withheld_actions"].remove("commit")
    elif defect == "duplicate-stage":
        value["stage_recommendations"].append(value["stage_recommendations"][0].copy())
    elif defect == "unknown-stage":
        value["stage_recommendations"][0]["stage_id"] = "not-a-real-stage"
    else:
        value["runtime_route"] = "brownfield-feature"
    before = persisted_bytes(repo)

    result = finalize(
        workbench_cli,
        repo,
        write_input(tmp_path / f"invalid-{defect}.json", value),
    )

    assert_rejected(result)
    assert persisted_bytes(repo) == before


def test_start_binds_intake_and_routing_and_replay_rejects_tampering(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-bound")
    input_path = write_input(tmp_path / "bound.json", routing_input())
    assert_succeeded(finalize(workbench_cli, repo, input_path))

    legacy_start = start_from_routing(
        workbench_cli, repo, from_routing=False, from_intake=True
    )
    assert_rejected(legacy_start)
    assert_succeeded(start_from_routing(workbench_cli, repo))
    _, compiled_state = load_state(repo)
    assert [item["phase_id"] for item in compiled_state["stages"]] == [
        "frame", "discover", "plan", "implement", "verify",
    ]
    assert [item["stage_id"] for item in compiled_state["stages"]] == [
        "outcome-framing",
        "brownfield-reconnaissance",
        "standards-resolution",
        "implementation",
        "local-verification",
    ]
    assert all(item["stage_id"] not in {"process-model", "proposal", "release"}
               for item in compiled_state["stages"])

    folder = repo / ".workbench" / "work" / WORK_ID
    event = find_event_store(repo).read()[0]
    assert [item["uri"] for item in event["inputs"]] == ["intake.json", "routing.json"]
    assert event["cause"]["references"] == event["inputs"]
    fp_input = event["payload"]["fingerprint_input"]
    assert fp_input["intake_sha256"] == hashlib.sha256(
        (folder / "intake.json").read_bytes()
    ).hexdigest()
    assert fp_input["routing_sha256"] == hashlib.sha256(
        (folder / "routing.json").read_bytes()
    ).hexdigest()
    replay = workbench_cli.invoke("replay", repo, ("--json",))
    assert_succeeded(replay)
    status = read_result(workbench_cli.invoke("status", repo, ("--json",)))
    assert status["routing_profile"]["execution_lane"] == "fast"

    receipt_path = folder / "routing.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["rationale"] = "Hidden mutation."
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(repo)
    assert_rejected(workbench_cli.invoke("status", repo, ("--json",)))
    assert_rejected(workbench_cli.invoke("replay", repo, ("--json",)))
    assert persisted_bytes(repo) == before


def test_exact_intake_bytes_remain_bound_after_finalization(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = captured_repo(tmp_path, workbench_cli, "routing-intake-bytes")
    assert_succeeded(
        finalize(
            workbench_cli,
            repo,
            write_input(tmp_path / "intake-bytes.json", routing_input()),
        )
    )
    intake_path = repo / ".workbench" / "work" / WORK_ID / "intake.json"
    intake_path.write_bytes(b"\n" + intake_path.read_bytes())
    before = persisted_bytes(repo)

    assert_rejected(workbench_cli.invoke("status", repo, ("--json",)))
    assert_rejected(start_from_routing(workbench_cli, repo))
    assert persisted_bytes(repo) == before
