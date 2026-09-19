"""Black-box coverage for the compact Workbench handoff authoring helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import PROJECT_ROOT, WorkbenchCLI, assert_succeeded
from test_workbench_v03 import routed_repo
from test_workbench_v05 import WORK_ID


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
    assert output["assumptions"][0].startswith("Open but non-blocking:")
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
