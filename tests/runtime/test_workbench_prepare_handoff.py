"""Black-box coverage for the compact Workbench handoff authoring helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import PROJECT_ROOT, WorkbenchCLI, assert_succeeded
from test_workbench_v03 import routed_repo
from test_workbench_v05 import WORK_ID
from test_workbench_routing import routing_input


HELPER = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-handoff.py"


def test_prepare_handoff_owns_mechanical_envelope_and_is_accepted(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    artifact_path = repo / ".workbench" / "work" / WORK_ID / "artifacts" / "outcome.md"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("# Outcome\n\nThe bounded outcome is recorded.\n", encoding="utf-8")
    dynamic_route = repo / "frontend" / "pages" / "cases" / "[caseId]" / "index.tsx"
    dynamic_route.parent.mkdir(parents=True)
    dynamic_route.write_text("export default function CasePage() {}\n", encoding="utf-8")
    source = {
        "handoff_id": "HO-PREPARED-FRAME",
        "specialist": "workbench",
        "artifact": {
            "artifact_id": "ART-PREPARED-FRAME-" + "X" * 80,
            "path": artifact_path.relative_to(repo).as_posix(),
            "title": "Prepared outcome frame",
            "artifact_kind": "outcome-frame",
        },
        "findings": [{
            "statement": "The requested outcome and boundary are explicit.",
            "finding_type": "fact",
            "sources": [".workbench/work/WB-INTAKE-001/intake.json"],
        }, {
            "statement": "The dynamic route is part of the inspected seam.",
            "finding_type": "fact",
            "sources": ["frontend/pages/cases/[caseId]/index.tsx"],
        }],
        "uncertainties": [{
            "question": "A downstream implementation detail remains open.",
            "owner": "agent",
        }],
        "options": [{
            "option_id": "OPT-MEASURE",
            "summary": "Measure the active journey first.",
            "tradeoffs": ["Requires environment access."],
        }],
        "proof": {
            "proof_id": "PRF-PREPARED-FRAME-" + "Y" * 80,
            "requirement_id": "REQ-PREPARED-FRAME-" + "Z" * 80,
            "claim": "The outcome-frame artifact records the requested boundary.",
            "acceptance_criteria": "The outcome and scope boundary are explicit.",
            "non_vacuity_check": "The review checked that both an outcome and an exclusion are present.",
        },
    }
    source_path = tmp_path / "phase.json"
    bundle_path = tmp_path / "bundle.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")

    prepared = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", WORK_ID,
         "--input", str(source_path), "--output", str(bundle_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )

    assert prepared.returncode == 0, prepared.stderr
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["handoff"]["stage"] == "outcome-framing"
    assert bundle["handoff"]["suggested_next_stage"] == "brownfield-reconnaissance"
    assert bundle["handoff"]["input_fingerprint"]["value"]
    assert len(bundle["handoff"]["handoff_id"]) <= 67
    assert len(bundle["records"][0]["artifact_id"]) <= 68
    assert len(bundle["records"][0]["proof_ids"][0]) <= 68
    assert bundle["records"][0]["artifact_kind"] == "other"
    assert bundle["records"][0]["custom_kind"] == "outcome-frame"
    assert bundle["records"][1]["status"] == "passed"
    assert bundle["handoff"]["findings"][0]["basis"] == "fact"
    assert bundle["handoff"]["findings"][1]["source_references"][0]["uri"] == (
        "frontend/pages/cases/[caseId]/index.tsx"
    )
    assert bundle["handoff"]["options"] == [{
        "name": "OPT-MEASURE",
        "benefits": ["Measure the active journey first."],
        "costs": [],
        "risks": ["Requires environment access."],
    }]
    assert bundle["handoff"]["uncertainties"][0]["description"] == (
        "A downstream implementation detail remains open."
    )
    assert bundle["handoff"]["uncertainties"][0]["next_action"]["description"].startswith(
        "Resolve this uncertainty:"
    )
    accepted = workbench_cli.invoke(
        "accept-handoff", repo,
        ("--work-id", WORK_ID, "--handoff-bundle", str(bundle_path),
         "--idempotency-key", "runtime-test:prepared-handoff:001", "--json"),
    )
    assert_succeeded(accepted)


def test_prepare_routing_normalizes_mechanical_fields_and_detects_prestart_artifacts(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    started = tmp_path / "started"
    started.mkdir()
    repo = routed_repo(started, workbench_cli)
    # Use a small independent pre-start shape; the helper is intentionally a
    # normalizer, while route-and-start remains the authoritative validator.
    work_id = "WB-PREPARE-ROUTING"
    work_dir = repo / ".workbench" / "work" / work_id
    work_dir.mkdir(parents=True)
    (work_dir / "intake.json").write_text("{}", encoding="utf-8")
    source = {
        "title": "T" * 300,
        "solution_context": "brownfield",
        "execution_lane": "full",
        "business_basis": "technical-only",
        "runtime_route": "proposal-only",
        "facts": [{"statement": "fact", "sources": ["repo"], "basis": "fact"}],
        "authorization_boundary": {"granted_actions": ["read-only"]},
        "unresolved_questions": [{
            "question": "Which live revision is deployed?",
            "why_material": "It may change option ranking but not the ability to propose conditional options.",
            "owner": "human",
        }],
        "recommendation": {
            "choice": "C" * 300, "rationale": "reason", "assumptions": [],
            "tradeoffs": ["cost"], "confidence": "medium",
        },
    }
    source_path = tmp_path / "routing-source.json"
    output_path = tmp_path / "routing-prepared.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    helper = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-routing.py"

    prepared = subprocess.run(
        [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(output_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )

    assert prepared.returncode == 0, prepared.stderr
    output = json.loads(output_path.read_text(encoding="utf-8"))
    assert output["runtime_route"] == "brownfield-feature"
    assert len(output["title"]) == len(output["recommendation"]["choice"]) == 256
    assert output["facts"] == [{"statement": "fact", "source_references": ["repo"]}]
    assert output["evidence_references"] == ["repo"]
    assert output["unresolved_questions"] == []
    assert output["assumptions"] == []
    assert output["phase_questions"] == [{
        "question": "Which live revision is deployed?",
        "why_material": "It may change option ranking but not the ability to propose conditional options.",
        "owner": {"actor_id": "user:local", "kind": "human"},
    }]
    assert output["stage_recommendations"] == [{
        "stage_id": "data-model-design",
        "applicability": "not-applicable",
        "reason": "No implementation or persisted-data change is authorized at this options-only destination.",
        "evidence_references": [],
    }]
    assert set(output["authorization_boundary"]["withheld_actions"]) == {
        "decision-delegation", "repository-mutation", "tracker-publication",
        "implementation", "commit", "deployment", "closure",
    }

    (work_dir / "draft.md").write_text("too early", encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(output_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert rejected.returncode == 2
    assert "move analysis artifacts elsewhere" in rejected.stderr


def test_prepare_routing_preserves_compact_semantics_and_rejects_ambiguity(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    work_id = "WB-COMPACT-SEMANTICS"
    captured = workbench_cli.invoke(
        "capture-intake", repo,
        ("--work-id", work_id, "--request", "Help me plan this system, then implement it.",
         "--idempotency-key", "compact-semantics:intake"),
    )
    assert_succeeded(captured)
    source_path = tmp_path / "routing-source.json"
    output_path = tmp_path / "routing-prepared.json"
    helper = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-routing.py"
    source_path.write_text(json.dumps({
        "title": "Collaborative implementation",
        "desired_outcome": "Implement the agreed workflow.",
        "solution_context": "brownfield",
        "lane": "full",
        "intent": "implement",
        "destination": "locally-verified-implementation",
        "planning_posture": "collaborative",
        "sourced_facts": [{"statement": "A plan exists.", "sources": ["plan.md"]}],
        "granted_actions": ["repository-mutation", "implementation"],
        "unresolved_questions": [{
            "question": "Which user-visible state names should the workflow use?",
            "why_material": "The answer changes the specification.",
            "owner": "human",
            "blocks_start": False,
        }],
        "acceptance_evidence": ["The implementation passes its behavioral tests."],
        "stage_recommendations": [{
            "stage_id": "outcome-framing",
            "applicability": "applicable",
            "reason": "Confirm the target before implementation.",
            "evidence_references": ["plan.md"],
        }, {
            "stage_id": "data-model-design",
            "applicability": "not-applicable",
            "reason": "No persisted product data changes.",
            "evidence_references": ["plan.md"],
        }],
    }), encoding="utf-8")

    prepared = subprocess.run(
        [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(output_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )

    assert prepared.returncode == 0, prepared.stderr
    output = json.loads(output_path.read_text(encoding="utf-8"))
    assert output["execution_lane"] == "full"
    assert output["engagement_intent"] == "implement"
    assert output["planning_destination"] == "locally-verified-implementation"
    assert output["planning_posture"] == "collaborative"
    assert output["facts"] == [{"statement": "A plan exists.", "source_references": ["plan.md"]}]
    assert output["authorization_boundary"]["granted_actions"] == [
        "implementation", "repository-mutation",
    ]
    assert output["assumptions"] == []
    assert output["phase_questions"][0]["question"].startswith("Which user-visible")

    for update, expected_error in ((
        {"execution_lane": "fast"}, "conflicting compact routing fields",
    ), (
        {"mystery_semantic": "silently lost before"}, "unknown compact routing fields",
    )):
        invalid = json.loads(source_path.read_text(encoding="utf-8"))
        invalid.update(update)
        source_path.write_text(json.dumps(invalid), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
             "--input", str(source_path), "--output", str(output_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
        )
        assert rejected.returncode == 2
        assert expected_error in rejected.stderr


def test_collaborative_outcome_gate_requires_ready_shared_understanding_and_confirmation(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "collaborative"
    repo.mkdir()
    work_id = "WB-COLLABORATIVE-GATE"
    assert_succeeded(workbench_cli.invoke(
        "capture-intake", repo,
        ("--work-id", work_id, "--request", "Help me plan and implement the workflow.",
         "--idempotency-key", "collaborative-gate:intake"),
    ))
    route = routing_input(
        planning_posture="collaborative",
        phase_questions=[],
        planning_destination="locally-verified-implementation",
        engagement_intent="implement",
        execution_lane="full",
        runtime_route="brownfield-feature",
        authorization_boundary={
            "granted_actions": ["repository-mutation", "implementation"],
            "withheld_actions": [
                "decision-delegation", "tracker-publication", "commit", "deployment", "closure",
            ],
        },
        stage_recommendations=[{
            "stage_id": "data-model-design",
            "applicability": "not-applicable",
            "reason": "The fixture changes no persisted product data.",
            "evidence_references": ["captured-intake"],
        }],
    )
    route_path = tmp_path / "collaborative-routing.json"
    route_path.write_text(json.dumps(route), encoding="utf-8")
    assert_succeeded(workbench_cli.invoke(
        "route-and-start", repo,
        ("--work-id", work_id, "--routing-input", str(route_path),
         "--idempotency-key", "collaborative-gate:start"),
    ))
    understanding = repo / "shared-understanding.md"
    understanding.write_text("# Shared understanding\n\nOutcome, scope, journey, and proof.\n", encoding="utf-8")
    source_path = tmp_path / "shared-source.json"
    bundle_path = tmp_path / "shared-bundle.json"
    base_source = {
        "handoff_id": "HO-COLLABORATIVE-FRAME-DRAFT",
        "artifact": {
            "artifact_id": "ART-COLLABORATIVE-SHARED-DRAFT",
            "path": understanding.relative_to(repo).as_posix(),
            "title": "Shared understanding",
            "artifact_kind": "shared-understanding",
            "readiness": "ready",
        },
        "findings": [{"statement": "The target is explicit.", "basis": "fact", "sources": ["captured-intake"]}],
    }
    source_path.write_text(json.dumps(base_source), encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(bundle_path), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert rejected.returncode == 2
    assert "confirmed user-owned decision" in rejected.stderr

    confirmed_source = dict(base_source)
    confirmed_source["handoff_id"] = "HO-COLLABORATIVE-FRAME-CONFIRMED"
    confirmed_source["artifact"] = {
        **base_source["artifact"],
        "artifact_id": "ART-COLLABORATIVE-SHARED-CONFIRMED",
    }
    confirmed_source["decisions"] = [{
        "decision_id": "DEC-COLLABORATIVE-SHARED",
        "question": "Does this artifact represent our shared understanding?",
        "authority": "user-owned",
        "state": "confirmed",
        "options": [
            {"option_id": "OPT-SHARED-CONFIRM", "name": "Confirm"},
            {"option_id": "OPT-SHARED-REVISE", "name": "Revise"},
        ],
        "selected_option_id": "OPT-SHARED-CONFIRM",
        "rationale": "The user accepted the target and path.",
        "artifact_inputs": ["ART-COLLABORATIVE-SHARED-CONFIRMED"],
    }]
    source_path.write_text(json.dumps(confirmed_source), encoding="utf-8")
    accepted = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(bundle_path), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert accepted.returncode == 0, accepted.stderr
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    artifact_record = next(item for item in bundle["records"] if item["record_type"] == "workbench-artifact")
    decision_record = next(item for item in bundle["records"] if item["record_type"] == "workbench-decision")
    assert artifact_record["artifact_kind"] == "shared-understanding"
    assert artifact_record["readiness"] == "ready"
    assert decision_record["state"] == "confirmed"


def test_ticket_frontier_derives_readiness_claims_atomically_and_unlocks_dependents(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    for name in ("ticket-a.md", "ticket-b.md"):
        (repo / name).write_text(f"# {name}\n\nVertical slice and proof contract.\n", encoding="utf-8")
    source_path = tmp_path / "tickets-source.json"
    bundle_path = tmp_path / "tickets-bundle.json"
    source_path.write_text(json.dumps({
        "handoff_id": "HO-TICKET-FRONTIER",
        "artifacts": [{
            "artifact_id": "ART-TICKET-A", "path": "ticket-a.md",
            "title": "Ticket A", "artifact_kind": "implementation-ticket", "readiness": "ready",
        }, {
            "artifact_id": "ART-TICKET-B", "path": "ticket-b.md",
            "title": "Ticket B", "artifact_kind": "implementation-ticket", "readiness": "ready",
        }],
        "node_additions": [{
            "node": {
                "node_id": "DLV-TICKET-A", "kind": "deliverable", "title": "Ticket A",
                "why_it_matters": "Delivers the first vertical slice.",
                "owner": {"actor_id": "agent:workbench", "kind": "agent"},
                "status": "ready",
                "next_action": {"description": "Implement ticket A.", "owner": {"actor_id": "agent:workbench", "kind": "agent"}, "target_type": "node", "target_id": "DLV-TICKET-A"},
                "done_when": ["Ticket A proof passes."],
                "evidence": [{"record_type": "artifact", "record_id": "ART-TICKET-A"}],
                "source_ids": ["AC-1"], "proof_status": "pending"
            },
            "depends_on": []
        }, {
            "node": {
                "node_id": "DLV-TICKET-B", "kind": "deliverable", "title": "Ticket B",
                "why_it_matters": "Delivers the dependent vertical slice.",
                "owner": {"actor_id": "agent:workbench", "kind": "agent"},
                "status": "ready",
                "next_action": {"description": "Implement ticket B.", "owner": {"actor_id": "agent:workbench", "kind": "agent"}, "target_type": "node", "target_id": "DLV-TICKET-B"},
                "done_when": ["Ticket B proof passes."],
                "evidence": [{"record_type": "artifact", "record_id": "ART-TICKET-B"}],
                "source_ids": ["AC-2"], "proof_status": "pending"
            },
            "depends_on": ["DLV-TICKET-A"]
        }],
    }), encoding="utf-8")
    accepted = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", WORK_ID,
         "--input", str(source_path), "--output", str(bundle_path), "--accept-only"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert accepted.returncode == 0, accepted.stderr
    lifecycle = json.loads(accepted.stdout)["lifecycle"]
    assert lifecycle["state_revision"] == 2

    projected = workbench_cli.invoke("next", repo, ("--work-id", WORK_ID, "--json"))
    assert_succeeded(projected)
    view = json.loads(projected.stdout)
    ready_ids = {item.get("node_id") for item in view["frontier"]["agent_ready"]}
    assert "DLV-TICKET-A" in ready_ids
    assert "DLV-TICKET-B" not in ready_ids

    blocked_claim = workbench_cli.invoke(
        "claim-node", repo,
        ("--work-id", WORK_ID, "--node-id", "DLV-TICKET-B", "--expected-revision", "2",
         "--idempotency-key", "ticket-frontier:claim-b", "--json"),
    )
    assert blocked_claim.returncode == 2
    assert "incomplete dependencies" in blocked_claim.output
    claimed = workbench_cli.invoke(
        "claim-node", repo,
        ("--work-id", WORK_ID, "--node-id", "DLV-TICKET-A", "--expected-revision", "2",
         "--idempotency-key", "ticket-frontier:claim-a", "--json"),
    )
    assert_succeeded(claimed)

    (repo / "implementation-a.md").write_text("# Implementation A\n\nVerified.\n", encoding="utf-8")
    completion_source = tmp_path / "completion-source.json"
    completion_bundle = tmp_path / "completion-bundle.json"
    completion_source.write_text(json.dumps({
        "handoff_id": "HO-TICKET-A-COMPLETE",
        "node_id": "DLV-TICKET-A",
        "artifact": {
            "artifact_id": "ART-IMPLEMENTATION-A", "path": "implementation-a.md",
            "title": "Implementation A", "artifact_kind": "implementation", "readiness": "ready",
        },
        "proof": {
            "proof_id": "PRF-TICKET-A", "requirement_id": "REQ-TICKET-A",
            "claim": "Ticket A meets AC-1.",
            "acceptance_criteria": ["The public seam passes."],
            "non_vacuity_check": "The behavior test exercised a non-empty fixture."
        },
        "node_updates": [{
            "node_id": "DLV-TICKET-A", "proposed_status": "completed",
            "rationale": "The ticket-scoped proof passed."
        }]
    }), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", WORK_ID,
         "--input", str(completion_source), "--output", str(completion_bundle), "--accept-only"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert completed.returncode == 0, completed.stderr
    projected = workbench_cli.invoke("next", repo, ("--work-id", WORK_ID, "--json"))
    assert_succeeded(projected)
    ready_ids = {
        item.get("node_id")
        for item in json.loads(projected.stdout)["frontier"]["agent_ready"]
    }
    assert "DLV-TICKET-B" in ready_ids
    ready_b = next(
        item for item in json.loads(projected.stdout)["frontier"]["agent_ready"]
        if item.get("node_id") == "DLV-TICKET-B"
    )
    assert ready_b["blockers"] == []


def test_specification_gate_rejects_draft_and_accepts_ready_proven_artifact(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = tmp_path / "spec-gate"
    repo.mkdir()
    work_id = "WB-SPEC-GATE"
    assert_succeeded(workbench_cli.invoke(
        "capture-intake", repo,
        ("--work-id", work_id, "--request", "Write a behavior specification.",
         "--idempotency-key", "spec-gate:intake"),
    ))
    route = routing_input(
        planning_posture="delegated", phase_questions=[], engagement_intent="plan",
        planning_destination="specification", execution_lane="full",
        runtime_route="brownfield-feature",
        stage_recommendations=[{
            "stage_id": "data-model-design", "applicability": "not-applicable",
            "reason": "No persisted data change is part of the fixture.",
            "evidence_references": ["captured-intake"],
        }],
    )
    route_path = tmp_path / "spec-routing.json"
    route_path.write_text(json.dumps(route), encoding="utf-8")
    assert_succeeded(workbench_cli.invoke(
        "route-and-start", repo,
        ("--work-id", work_id, "--routing-input", str(route_path),
         "--idempotency-key", "spec-gate:start"),
    ))
    (repo / "frame.md").write_text("# Frame\n\nBounded outcome.\n", encoding="utf-8")
    frame_source = tmp_path / "spec-frame.json"
    frame_bundle = tmp_path / "spec-frame-bundle.json"
    frame_source.write_text(json.dumps({
        "handoff_id": "HO-SPEC-FRAME",
        "artifact": {"artifact_id": "ART-SPEC-FRAME", "path": "frame.md", "title": "Frame", "artifact_kind": "other"},
    }), encoding="utf-8")
    advanced = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(frame_source), "--output", str(frame_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert advanced.returncode == 0, advanced.stderr

    (repo / "spec.md").write_text("# Spec\n\nOUT-1, US-1, INV-1, AC-1, and proof ownership.\n", encoding="utf-8")
    review = {field: True for field in (
        "provenance_reconciled", "measurements_bounded", "conditional_ordering", "durable_artifact_final",
    )}
    spec_source = tmp_path / "spec-source.json"
    spec_bundle = tmp_path / "spec-bundle.json"
    base = {
        "handoff_id": "HO-SPEC-DRAFT",
        "artifact": {
            "artifact_id": "ART-SPEC-DRAFT", "path": "spec.md", "title": "Specification",
            "artifact_kind": "specification", "readiness": "draft",
        },
        "review": review,
    }
    spec_source.write_text(json.dumps(base), encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(spec_source), "--output", str(spec_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert rejected.returncode == 2
    assert "marked ready" in rejected.stderr

    ready = dict(base)
    ready["handoff_id"] = "HO-SPEC-READY"
    ready["artifact"] = {**base["artifact"], "artifact_id": "ART-SPEC-READY", "readiness": "ready"}
    ready["proof"] = {
        "proof_id": "PRF-SPEC-GATE-READY", "requirement_id": "REQ-SPEC-GATE-READY",
        "claim": "The ready specification is traceable and complete.",
        "acceptance_criteria": ["Stable IDs and proof ownership are present."],
        "non_vacuity_check": "The artifact contains OUT-1, US-1, INV-1, and AC-1."
    }
    spec_source.write_text(json.dumps(ready), encoding="utf-8")
    accepted = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(spec_source), "--output", str(spec_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert accepted.returncode == 0, accepted.stderr


def test_prepared_compact_routing_starts_without_schema_discovery(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    work_id = "WB-COMPACT-ROUTING"
    captured = workbench_cli.invoke(
        "capture-intake", repo,
        ("--work-id", work_id, "--request", "Investigate preview latency and give options.",
         "--idempotency-key", "compact-routing:intake"),
    )
    assert_succeeded(captured)
    compact = {
        "title": "Preview latency options",
        "desired_outcome": "Provide ranked, evidence-bounded latency options.",
        "solution_context": "Insurance-document processing platform at commit abc123.",
        "execution_lane": "investigation",
        "business_basis": "efficiency",
        "engagement_intent": "options-only",
        "planning_destination": "decision-ready options",
        "facts": [{"statement": "The preview is rendered on demand.", "source_reference": "app/preview.py"}],
        "recommendation": "Measure the deployed seam before selecting an implementation.",
        "unresolved_questions": [{
            "question": "Is the deployed cache warm?",
            "why_material": "It changes option ranking, not whether conditional options can be produced.",
        }],
    }
    source_path = tmp_path / "compact-routing.json"
    output_path = tmp_path / "prepared-routing.json"
    source_path.write_text(json.dumps(compact), encoding="utf-8")
    helper = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-routing.py"
    prepared = subprocess.run(
        [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(output_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert prepared.returncode == 0, prepared.stderr
    normalized = json.loads(output_path.read_text(encoding="utf-8"))
    assert normalized["solution_context"] == "brownfield"
    assert normalized["execution_lane"] == "full"
    assert normalized["business_basis"] == "technical-only"
    assert normalized["engagement_intent"] == "explore"
    assert normalized["planning_destination"] == "proposal"
    assert normalized["facts"][0]["source_references"] == ["app/preview.py"]
    assert normalized["recommendation"]["choice"].startswith("Measure the deployed seam")
    started = workbench_cli.invoke(
        "route-and-start", repo,
        ("--work-id", work_id, "--routing-input", str(output_path),
         "--idempotency-key", "compact-routing:start"),
    )
    assert_succeeded(started)

    artifacts = repo / ".workbench" / "work" / work_id / "artifacts"
    frame_artifact = repo / "diagnosis.md"
    frame_artifact.write_text("# Frame\n\nOutcome and boundaries.\n", encoding="utf-8")
    frame_source = tmp_path / "frame-source.json"
    frame_bundle = tmp_path / "frame-bundle.json"
    frame_source.write_text(json.dumps({
        "handoff_id": "HO-COMPACT-FRAME",
        "artifact": {
            "artifact_id": "ART-COMPACT-SHARED", "path": frame_artifact.relative_to(repo).as_posix(),
            "title": "Compact frame", "artifact_kind": "other",
        },
        "findings": [{"claim": "The outcome is bounded.", "finding_type": "fact", "sources": ["captured-intake"]}],
    }), encoding="utf-8")
    prepared_frame = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(frame_source), "--output", str(frame_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert prepared_frame.returncode == 0, prepared_frame.stderr
    prepared_frame_value = json.loads(frame_bundle.read_text(encoding="utf-8"))
    frame_snapshot = repo / prepared_frame_value["records"][0]["location"]["value"]
    assert frame_snapshot != frame_artifact
    assert frame_snapshot.read_text(encoding="utf-8").startswith("# Frame")
    assert json.loads(prepared_frame.stdout)["result"] == "accepted-and-advanced"
    assert "human_control" not in json.loads(prepared_frame.stdout)["lifecycle"]

    proposal_artifact = frame_artifact
    proposal_artifact.write_text("# Proposal\n\nRanked options with uncertainty.\n", encoding="utf-8")
    proposal_source = tmp_path / "proposal-source.json"
    proposal_bundle = tmp_path / "proposal-bundle.json"
    proposal_value = {
        "handoff_id": "HO-COMPACT-PROPOSAL",
        "artifact": {
            "artifact_id": "ART-COMPACT-SHARED",
            "path": proposal_artifact.relative_to(repo).as_posix(),
            "title": "Compact proposal", "artifact_kind": "proposal",
        },
        "findings": [{"statement": "The options are ranked.", "basis": "inference", "sources": ["proposal.md"]}],
    }
    proposal_source.write_text(json.dumps(proposal_value), encoding="utf-8")
    rejected_proposal = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(proposal_source), "--output", str(proposal_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert rejected_proposal.returncode == 2
    assert "terminal acceptance requires review fields" in rejected_proposal.stderr
    proposal_value["review"] = {
        "provenance_reconciled": True,
        "measurements_bounded": True,
        "conditional_ordering": True,
        "durable_artifact_final": True,
    }
    proposal_source.write_text(json.dumps(proposal_value), encoding="utf-8")
    prepared_proposal = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(proposal_source), "--output", str(proposal_bundle), "--accept-and-advance"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert prepared_proposal.returncode == 0, prepared_proposal.stderr
    assert json.loads(prepared_proposal.stdout)["review_marker"] == "DIAGNOSIS_PROPOSAL_REVIEW_V2"
    assert json.loads(prepared_proposal.stdout)["lifecycle"]["status"] == "awaiting-acceptance"
    terminal_bundle = json.loads(proposal_bundle.read_text(encoding="utf-8"))
    assert len(terminal_bundle["records"]) == 2
    assert terminal_bundle["records"][0]["artifact_id"] != "ART-COMPACT-SHARED"
    assert (repo / terminal_bundle["records"][0]["location"]["value"]) != frame_snapshot
    assert frame_snapshot.read_text(encoding="utf-8").startswith("# Frame")
    assert terminal_bundle["records"][1]["record_type"] == "workbench-proof"
    assert terminal_bundle["handoff"]["terminal_disposition"] == "completed-for-destination"
    state = json.loads((repo / ".workbench" / "work" / work_id / "state.json").read_text(encoding="utf-8"))
    assert state["status"] == "awaiting-acceptance"


def test_accept_to_proposal_serializes_final_result_once(
    tmp_path: Path, workbench_cli: WorkbenchCLI,
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    work_id = "WB-ONE-PROPOSAL-HANDOFF"
    captured = workbench_cli.invoke(
        "capture-intake", repo,
        ("--work-id", work_id, "--request", "Investigate latency and give options.",
         "--idempotency-key", "one-proposal:intake"),
    )
    assert_succeeded(captured)
    routing = tmp_path / "routing.json"
    routing.write_text(json.dumps({
        "request": "Investigate latency and give options.",
        "title": "Latency options",
        "desired_outcome": "Provide ranked latency options.",
        "solution_context": "brownfield",
        "execution_lane": "full",
        "business_basis": "technical-only",
        "engagement_intent": "explore",
        "planning_destination": "proposal",
        "recommendation": "Measure the relevant seam.",
    }), encoding="utf-8")
    prepared_routing = tmp_path / "prepared-routing.json"
    routing_helper = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-routing.py"
    prepared = subprocess.run(
        [sys.executable, str(routing_helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(routing), "--output", str(prepared_routing)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert prepared.returncode == 0, prepared.stderr
    started = workbench_cli.invoke(
        "route-and-start", repo,
        ("--work-id", work_id, "--routing-input", str(prepared_routing),
         "--idempotency-key", "one-proposal:start"),
    )
    assert_succeeded(started)

    artifact = repo / "proposal.md"
    artifact.write_text("# Proposal\n\nRanked, bounded options.\n", encoding="utf-8")
    source = tmp_path / "proposal-source.json"
    source_value = {
        "handoff_id": "HO-ONE-PROPOSAL",
        "artifact": {
            "artifact_id": "ART-ONE-PROPOSAL", "path": "proposal.md",
            "title": "Latency proposal", "artifact_kind": "proposal",
        },
        "findings": [{"summary": "Options are ranked.", "classification": "inference", "sources": ["proposal.md"]}],
    }
    source.write_text(json.dumps(source_value), encoding="utf-8")
    output = tmp_path / "proposal-bundle.json"

    rejected = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source), "--output", str(output), "--accept-to-proposal"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert rejected.returncode == 2
    assert "terminal acceptance requires review fields" in rejected.stderr
    unchanged = json.loads((repo / ".workbench" / "work" / work_id / "state.json").read_text(encoding="utf-8"))
    assert unchanged["current_stage"] == "outcome-framing"

    source_value["review"] = {field: True for field in (
        "provenance_reconciled", "measurements_bounded",
        "conditional_ordering", "durable_artifact_final",
    )}
    source.write_text(json.dumps(source_value), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source), "--output", str(output), "--accept-to-proposal"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["result"] == "accepted-to-proposal"
    assert result["review_marker"] == "DIAGNOSIS_PROPOSAL_REVIEW_V2"
    assert output.exists()
    assert output.with_name("proposal-bundle.framing.json").exists()
    state = json.loads((repo / ".workbench" / "work" / work_id / "state.json").read_text(encoding="utf-8"))
    assert state["status"] == "awaiting-acceptance"
    assert len(state["handoff_ids"]) == 2


def test_prepare_routing_can_capture_and_start_in_one_invocation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    work_id = "WB-ONE-SHOT-START"
    source = {
        "request": "/workbench investigate preview latency and give options",
        "title": "Preview latency options",
        "desired_outcome": "Provide evidence-bounded latency options.",
        "solution_context": "brownfield",
        "execution_lane": "full",
        "business_basis": "technical-only",
        "planning_destination": "proposal",
        "recommendation": "Inspect the bounded request path.",
    }
    source_path = tmp_path / "routing.json"
    output_path = tmp_path / "prepared.json"
    source_path.write_text(json.dumps(source), encoding="utf-8")
    helper = PROJECT_ROOT / "skills" / "workbench" / "scripts" / "prepare-routing.py"

    completed = subprocess.run(
        [sys.executable, str(helper), "--repo", str(repo), "--work-id", work_id,
         "--input", str(source_path), "--output", str(output_path), "--capture-and-start"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["result"] == "captured-and-started"
    assert "human_control" not in json.loads(completed.stdout)["lifecycle"]
    state = json.loads((repo / ".workbench" / "work" / work_id / "state.json").read_text(encoding="utf-8"))
    assert state["status"] == "active"
    assert state["current_stage"] == "outcome-framing"
