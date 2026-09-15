"""Regression tests for Workbench v0.3 proportional orchestration."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from conftest import (
    WorkbenchCLI,
    assert_rejected,
    assert_succeeded,
    load_state,
    persisted_bytes,
)
from test_workbench_intake import WORK_ID, capture
from test_workbench_routing import finalize, routing_input, write_input


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def routed_repo(tmp_path: Path, cli: WorkbenchCLI) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert_succeeded(capture(cli, repo))
    route = routing_input(
        stage_recommendations=[
            {
                "stage_id": "process-model",
                "applicability": "not-applicable",
                "reason": "The requested feature does not change the business process.",
                "evidence_references": ["captured-intake"],
            },
            {
                "stage_id": "proposal",
                "applicability": "not-applicable",
                "reason": "The user already requested implementation.",
                "evidence_references": ["captured-intake"],
            },
            {
                "stage_id": "data-model-design",
                "applicability": "not-applicable",
                "reason": "The focused test fixture does not alter persisted data semantics.",
                "evidence_references": ["captured-intake"],
            },
        ]
    )
    assert_succeeded(finalize(cli, repo, write_input(tmp_path / "routing.json", route)))
    assert_succeeded(
        cli.invoke(
            "start",
            repo,
            (
                "--work-id", WORK_ID,
                "--from-routing",
                "--idempotency-key", "runtime-test:v03-start:001",
                "--json",
            ),
        )
    )
    return repo


def test_route_and_start_is_atomic_and_defaults_unlisted_authority_to_denied(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "atomic"
    repo.mkdir()
    assert_succeeded(capture(workbench_cli, repo))
    value = routing_input()
    value["authorization_boundary"] = {
        "granted_actions": ["repository-mutation", "implementation"]
    }
    route_path = write_input(tmp_path / "atomic-routing.json", value)
    args = (
        "--work-id", WORK_ID,
        "--routing-input", str(route_path),
        "--idempotency-key", "runtime-test:v03-route-and-start:001",
        "--owner", "human:runtime-test",
        "--json",
    )

    result = workbench_cli.invoke("route-and-start", repo, args)

    assert_succeeded(result)
    view = json.loads(result.stdout)
    assert view["route"] == "profile-compiled"
    folder = repo / ".workbench" / "work" / WORK_ID
    routing = json.loads((folder / "routing.json").read_text(encoding="utf-8"))
    assert set(routing["authorization_boundary"]["withheld_actions"]) == {
        "decision-delegation", "tracker-publication", "commit", "deployment", "closure"
    }
    before = persisted_bytes(repo)
    retry = workbench_cli.invoke("route-and-start", repo, args)
    assert_succeeded(retry)
    assert json.loads(retry.stdout)["result"] == "idempotent"
    assert persisted_bytes(repo) == before


def test_manual_table_feedback_route_uses_six_checkpoints_without_process_or_proposal(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "manual-table-feedback"
    repo.mkdir()
    assert_succeeded(capture(workbench_cli, repo))
    recommendations = [
        {
            "stage_id": stage_id,
            "applicability": applicability,
            "reason": reason,
            "evidence_references": ["captured-intake"],
        }
        for stage_id, applicability, reason in (
            ("evidence-intake", "applicable", "The separator HTML is interaction evidence."),
            ("process-model", "not-applicable", "The feature does not change the business process."),
            ("proposal", "not-applicable", "Implementation was explicitly requested."),
            ("experience-design", "applicable", "Column interactions affect the user experience."),
            ("solution-architecture", "applicable", "UI, API, extraction, and CSV boundaries are material."),
            ("data-model-design", "not-applicable", "The change does not alter persisted data semantics."),
        )
    ]
    value = routing_input(
        execution_lane="full",
        runtime_route="brownfield-feature",
        stage_recommendations=recommendations,
    )
    route_path = write_input(tmp_path / "manual-table-routing.json", value)
    result = workbench_cli.invoke(
        "route-and-start",
        repo,
        (
            "--work-id", WORK_ID,
            "--routing-input", str(route_path),
            "--idempotency-key", "runtime-test:manual-table-feedback:001",
            "--owner", "human:runtime-test",
            "--json",
        ),
    )

    assert_succeeded(result)
    _, state = load_state(repo)
    assert [(item["phase_id"], item["stage_id"]) for item in state["stages"]] == [
        ("frame", "outcome-framing"),
        ("discover", "evidence-intake"),
        ("design-decide", "solution-architecture"),
        ("plan", "delivery-planning"),
        ("implement", "implementation"),
        ("verify", "local-verification"),
    ]
    routing = json.loads(
        (repo / ".workbench" / "work" / WORK_ID / "routing.json").read_text(encoding="utf-8")
    )
    applicability = {
        activity["stage_id"]: activity["applicability"]
        for phase in routing["compiled_plan"]["phases"]
        for activity in phase["activities"]
    }
    assert applicability["process-model"] == "not-applicable"
    assert applicability["proposal"] == "not-applicable"
    assert all(item["stage_id"] not in {"release", "deployed-verification", "outcome-verification"}
               for item in state["stages"])


def artifact(repo: Path, *, digest_override: str | None = None) -> dict[str, Any]:
    path = repo / "docs" / "outcome.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Outcome\n\nUsers can combine selected rows.\n", encoding="utf-8")
    content_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "record_type": "workbench-artifact",
        "schema_version": "0.3.0",
        "artifact_id": "ART-V03-OUTCOME",
        "work_id": WORK_ID,
        "artifact_kind": "evidence-record",
        "title": "Outcome evidence",
        "status": "current",
        "owner": {"actor_id": "agent:outcome", "kind": "agent"},
        "producing_stage": "outcome-framing",
        "produced_by": {"actor_id": "agent:outcome", "kind": "agent"},
        "location": {"kind": "workspace-path", "value": "docs/outcome.md"},
        "source_lineage": [
            {
                "relationship": "derived-from",
                "source": {"record_type": "work", "record_id": WORK_ID},
            }
        ],
        "consumers": [
            {
                "kind": "stage",
                "consumer_id": "brownfield-reconnaissance",
                "purpose": "Carry the framed outcome into discovery.",
            }
        ],
        "proof_ids": [],
        "obligation_node_ids": [],
        "content_integrity": {
            "algorithm": "sha256",
            "value": digest_override or content_digest,
        },
        "confidentiality": "internal",
        "known_defects": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def handoff(artifact_record: dict[str, Any]) -> dict[str, Any]:
    inputs = [{"record_type": "work", "record_id": WORK_ID}]
    policy_versions = {"decision_policy": "0.3.0", "artifact_contracts": "0.3.0"}
    return {
        "record_type": "workbench-handoff",
        "schema_version": "0.3.0",
        "handoff_id": "HO-V03-OUTCOME",
        "work_id": WORK_ID,
        "node_id": "O-INTAKE-001",
        "stage": "outcome-framing",
        "specialist": "outcome-framing",
        "status": "completed",
        "owner": {"actor_id": "agent:outcome", "kind": "agent"},
        "idempotency_key": "runtime-test:v03-handoff-record:001",
        "input_fingerprint": {
            "algorithm": "sha256",
            "value": canonical_digest({
                "inputs_used": inputs,
                "policy_versions": policy_versions,
            }),
        },
        "inputs_used": inputs,
        "applicability": {
            "applied": ["outcome-framing"],
            "skipped": [],
            "could_not_determine": [],
        },
        "policy_versions": policy_versions,
        "findings": ["The requested outcome and local proof boundary are explicit."],
        "options": [],
        "decisions_required": [],
        "artifacts_produced": [
            {
                "record_type": "artifact",
                "record_id": artifact_record["artifact_id"],
                "path": artifact_record["location"]["value"],
            }
        ],
        "node_updates": [],
        "authorization_ids": [],
        "suggested_next_stage": "brownfield-reconnaissance",
        "why_next": "Inspect the current implementation and blast radius.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def write_bundle(path: Path, handoff_record: dict[str, Any], records: list[dict[str, Any]]) -> Path:
    path.write_text(
        json.dumps({"handoff": handoff_record, "records": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def accept(cli: WorkbenchCLI, repo: Path, bundle: Path):
    _, state = load_state(repo)
    return cli.invoke(
        "accept-handoff",
        repo,
        (
            "--work-id", WORK_ID,
            "--handoff-bundle", str(bundle),
            "--idempotency-key", "runtime-test:v03-accept:001",
            "--expected-revision", str(state["state_revision"]),
            "--actor", "agent:workbench",
            "--json",
        ),
    )


def test_accept_handoff_registers_artifact_and_detects_later_tampering(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    artifact_record = artifact(repo)
    bundle = write_bundle(tmp_path / "handoff.json", handoff(artifact_record), [artifact_record])

    result = accept(workbench_cli, repo, bundle)

    assert_succeeded(result)
    _, state = load_state(repo)
    assert state["artifact_ids"] == ["ART-V03-OUTCOME"]
    assert state["handoff_ids"] == ["HO-V03-OUTCOME"]
    assert state["stages"][0]["output_artifact_ids"] == ["ART-V03-OUTCOME"]
    assert (repo / ".workbench" / "work" / WORK_ID / "records" / "ART-V03-OUTCOME.json").is_file()
    advance_args = (
        "--work-id", WORK_ID,
        "--accepted-handoff", "HO-V03-OUTCOME",
        "--idempotency-key", "runtime-test:v03-advance:001",
        "--expected-revision", str(state["state_revision"]),
        "--actor", "agent:workbench",
        "--json",
    )
    advanced = workbench_cli.invoke("advance-stage", repo, advance_args)
    assert_succeeded(advanced)
    _, advanced_state = load_state(repo)
    assert advanced_state["current_stage"] == "brownfield-reconnaissance"
    before_retry = persisted_bytes(repo)
    retry = workbench_cli.invoke("advance-stage", repo, advance_args)
    assert_succeeded(retry)
    assert json.loads(retry.stdout)["result"] == "idempotent"
    assert persisted_bytes(repo) == before_retry
    assert_succeeded(workbench_cli.invoke("replay", repo, ("--work-id", WORK_ID, "--json")))

    record_path = repo / ".workbench" / "work" / WORK_ID / "records" / "ART-V03-OUTCOME.json"
    original_record = record_path.read_bytes()
    changed_record = json.loads(original_record)
    changed_record["title"] = "Edited after acceptance"
    record_path.write_text(json.dumps(changed_record, indent=2) + "\n", encoding="utf-8")
    assert_rejected(workbench_cli.invoke("status", repo, ("--work-id", WORK_ID, "--json")))
    record_path.write_bytes(original_record)

    (repo / "docs" / "outcome.md").write_text("changed", encoding="utf-8")
    assert_rejected(workbench_cli.invoke("status", repo, ("--work-id", WORK_ID, "--json")))


def test_handoff_with_wrong_artifact_digest_is_rejected_atomically(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    artifact_record = artifact(repo, digest_override="0" * 64)
    bundle = write_bundle(tmp_path / "bad-handoff.json", handoff(artifact_record), [artifact_record])
    before = persisted_bytes(repo)

    assert_rejected(accept(workbench_cli, repo, bundle))
    assert persisted_bytes(repo) == before


def test_v03_proof_rejects_a_component_harness_for_an_authenticated_journey(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    artifact_record = artifact(repo)
    timestamp = datetime.now(timezone.utc).isoformat()
    proof = {
        "record_type": "workbench-proof",
        "schema_version": "0.3.0",
        "proof_id": "PRF-V03-AUTH-JOURNEY",
        "work_id": WORK_ID,
        "claim": "The authenticated manual-table journey works.",
        "verification_scope": "integration-journey",
        "applicability": "required",
        "status": "passed",
        "owner": {"actor_id": "agent:review", "kind": "agent"},
        "required_proof": [
            {
                "requirement_id": "REQ-V03-AUTH-JOURNEY",
                "kind": "integration",
                "description": "Exercise the real authenticated modal.",
                "acceptance_criteria": ["The production case route opens the real modal."],
                "oracle_requirement": "Playwright observes the production application flow.",
                "verification_target": {
                    "environment": "local-production-build",
                    "seam": "authenticated-application-flow",
                    "journey": "case-route-to-manual-selection-modal",
                },
            }
        ],
        "achieved_proof": [
            {
                "requirement_id": "REQ-V03-AUTH-JOURNEY",
                "kind": "integration",
                "result": "passed",
                "oracle": {
                    "kind": "automated-independent",
                    "description": "Playwright exercised an isolated component page.",
                },
                "evidence": [{"record_type": "artifact", "record_id": "ART-V03-OUTCOME"}],
                "non_vacuity_check": "The isolated component rendered test data.",
                "observed_by": {"actor_id": "agent:review", "kind": "agent"},
                "observed_at": timestamp,
                "limitations": ["Authentication and production routing were not exercised."],
                "verification_target": {
                    "environment": "isolated-browser-harness",
                    "seam": "component",
                    "journey": "invented-test-page",
                },
            }
        ],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    bundle = write_bundle(
        tmp_path / "bad-proof.json",
        handoff(artifact_record),
        [artifact_record, proof],
    )
    before = persisted_bytes(repo)

    assert_rejected(accept(workbench_cli, repo, bundle))
    assert persisted_bytes(repo) == before


def test_status_separates_blocked_integration_from_other_verification_scopes(
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    artifact_record = artifact(repo)
    timestamp = datetime.now(timezone.utc).isoformat()
    proof = {
        "record_type": "workbench-proof",
        "schema_version": "0.3.0",
        "proof_id": "PRF-V03-INTEGRATION-BLOCKED",
        "work_id": WORK_ID,
        "claim": "The authenticated application journey works.",
        "verification_scope": "integration-journey",
        "applicability": "required",
        "status": "blocked",
        "owner": {"actor_id": "agent:review", "kind": "agent"},
        "next_action": {
            "description": "Provide an approved authenticated test fixture.",
            "owner": {"actor_id": "human:test-owner", "kind": "human"},
            "target_type": "evidence",
            "target_id": "AUTHENTICATED-FIXTURE",
        },
        "blockers": [
            {
                "kind": "external",
                "description": "No authenticated fixture is available.",
                "owner": {"actor_id": "human:test-owner", "kind": "human"},
                "next_action": {
                    "description": "Provide an approved authenticated test fixture.",
                    "owner": {"actor_id": "human:test-owner", "kind": "human"},
                    "target_type": "evidence",
                    "target_id": "AUTHENTICATED-FIXTURE",
                },
            }
        ],
        "required_proof": [
            {
                "requirement_id": "REQ-V03-INTEGRATION-BLOCKED",
                "kind": "integration",
                "description": "Exercise the authenticated production flow.",
                "acceptance_criteria": ["The real modal opens through the case route."],
                "oracle_requirement": "Playwright observes the authenticated journey.",
                "verification_target": {
                    "environment": "local-production-build",
                    "seam": "authenticated-application-flow",
                    "journey": "case-route-to-manual-selection-modal",
                },
            }
        ],
        "achieved_proof": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    repository_health = {
        "record_type": "workbench-proof",
        "schema_version": "0.3.0",
        "proof_id": "PRF-V03-REPOSITORY-HEALTH",
        "work_id": WORK_ID,
        "claim": "The repository-wide release checks pass.",
        "verification_scope": "repository-health",
        "applicability": "required",
        "status": "failed",
        "owner": {"actor_id": "agent:review", "kind": "agent"},
        "failure_summary": "A pre-existing repository governance baseline is stale.",
        "required_proof": [
            {
                "requirement_id": "REQ-V03-REPOSITORY-HEALTH",
                "kind": "integration",
                "description": "Run the repository-wide governance suite.",
                "acceptance_criteria": ["The repository governance suite passes."],
                "oracle_requirement": "The repository-owned governance command exits successfully.",
                "verification_target": {
                    "environment": "local-repository",
                    "seam": "repository-governance-suite",
                    "journey": "full-policy-check",
                },
            }
        ],
        "achieved_proof": [
            {
                "requirement_id": "REQ-V03-REPOSITORY-HEALTH",
                "kind": "integration",
                "result": "failed",
                "oracle": {
                    "kind": "automated-independent",
                    "description": "The governance command reported a stale baseline.",
                },
                "evidence": [{"record_type": "artifact", "record_id": "ART-V03-OUTCOME"}],
                "observed_by": {"actor_id": "agent:review", "kind": "agent"},
                "observed_at": timestamp,
                "limitations": ["The failure predates the feature-focused change."],
                "verification_target": {
                    "environment": "local-repository",
                    "seam": "repository-governance-suite",
                    "journey": "full-policy-check",
                },
            }
        ],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    bundle = write_bundle(
        tmp_path / "blocked-proof.json",
        handoff(artifact_record),
        [artifact_record, proof, repository_health],
    )
    assert_succeeded(accept(workbench_cli, repo, bundle))

    status = workbench_cli.invoke("status", repo, ("--work-id", WORK_ID, "--json"))
    assert_succeeded(status)
    view = json.loads(status.stdout)
    assert view["verification"]["integration-journey"] == {
        "status": "blocked",
        "proof_ids": ["PRF-V03-INTEGRATION-BLOCKED"],
    }
    assert view["verification"]["feature-focused"]["status"] == "not-recorded"
    assert view["verification"]["repository-health"] == {
        "status": "failed",
        "proof_ids": ["PRF-V03-REPOSITORY-HEALTH"],
    }
    assert view["verification"]["user-acceptance"]["status"] == "not-recorded"
