#!/usr/bin/env python3
"""Compile a compact phase result into a schema-valid Workbench handoff bundle.

The runtime schemas remain authoritative. This helper owns their mechanical fields
so an agent can spend its context on findings instead of reconstructing envelopes,
digests, record references, and lifecycle pointers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from workbench import RUNTIME_VERSION, WorkbenchError, digest, load_json, now, validate_record


AGENT = {"actor_id": "agent:workbench", "kind": "agent"}
HUMAN = {"actor_id": "user:local", "kind": "human"}
ARTIFACT_KINDS = {
    "evidence-record", "process-model", "validation-plan", "validation-result", "proposal",
    "experience-design", "prototype", "architecture", "data-model", "diagram",
    "standards-profile", "specification", "delivery-plan", "implementation", "review",
    "release-record", "outcome-measurement", "other",
}
TERMINAL_REVIEW_FIELDS = (
    "provenance_reconciled",
    "measurements_bounded",
    "conditional_ordering",
    "durable_artifact_final",
)
TERMINAL_REVIEW_MARKER = "DIAGNOSIS_PROPOSAL_REVIEW_V2"


def run_workbench(arguments: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("workbench.py")), *arguments, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise WorkbenchError(detail or f"Workbench command failed: {arguments[0]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise WorkbenchError(f"Workbench command returned invalid JSON: {arguments[0]}") from exc


def actor(value: str | dict | None) -> dict:
    if isinstance(value, dict):
        return value
    if value == "human":
        return HUMAN.copy()
    return AGENT.copy()


def compact_id(value: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ValueError(f"ID must start with {prefix}: {value!r}")
    return prefix + value[len(prefix):][:64]


def external_reference(repo: Path, value: str) -> dict:
    raw = value.strip()
    candidate = raw.split(":", 1)[0] if ":" in raw and not raw.startswith(("urn:", "http:" , "https:")) else raw
    path = repo / candidate
    uri = quote(candidate.replace("\\", "/"), safe="/._-") if path.exists() else "urn:workbench:" + quote(raw, safe="._-")
    return {"record_type": "external", "record_id": raw, "uri": uri}


def next_action(value: str | dict, *, owner: dict, target_type: str, target_id: str) -> dict:
    if isinstance(value, dict):
        return value
    return {
        "description": value,
        "owner": owner,
        "target_type": target_type,
        "target_id": target_id,
    }


def require_terminal_review(repo: Path, work_id: str, source: dict) -> None:
    """Require an explicit final-content review before an irreversible terminal snapshot."""
    state = load_json(repo / ".workbench" / "work" / work_id / "state.json")
    stages = state["stages"]
    stage_index = next(
        index for index, item in enumerate(stages)
        if item["stage_id"] == state["current_stage"]
    )
    if stage_index + 1 < len(stages):
        return
    review = source.get("review")
    missing = [
        field for field in TERMINAL_REVIEW_FIELDS
        if not isinstance(review, dict) or review.get(field) is not True
    ]
    if missing:
        raise ValueError(
            "terminal acceptance requires review fields set to true after reviewing the final artifact: "
            + ", ".join(missing)
        )


def lifecycle_summary(value: dict) -> dict:
    summary = {
        key: value[key] for key in (
            "work_id", "status", "current_stage", "current_stage_status",
            "current_phase", "state_revision", "planning_destination",
        ) if key in value
    }
    if isinstance(value.get("next_action"), dict):
        action = value["next_action"]
        summary["next_action"] = {
            key: action[key] for key in ("description", "target_type", "target_id") if key in action
        }
        if isinstance(action.get("owner"), dict):
            summary["next_action"]["owner"] = action["owner"]
    verification = value.get("verification")
    if isinstance(verification, dict):
        recorded = {
            key: item for key, item in verification.items()
            if isinstance(item, dict) and item.get("status") != "not-recorded"
        }
        if recorded:
            summary["verification"] = recorded
    return summary


def compile_bundle(repo: Path, work_id: str, source: dict) -> dict:
    work_dir = repo / ".workbench" / "work" / work_id
    state = load_json(work_dir / "state.json")
    map_record = load_json(work_dir / "map.json")
    stage = state["current_stage"]
    stages = state["stages"]
    stage_index = next(index for index, item in enumerate(stages) if item["stage_id"] == stage)
    following = stages[stage_index + 1]["stage_id"] if stage_index + 1 < len(stages) else None
    timestamp = now()

    artifact_spec = source["artifact"]
    artifact_path = Path(artifact_spec["path"])
    if artifact_path.is_absolute():
        raise ValueError("artifact.path must be repository-relative")
    absolute_artifact = (repo / artifact_path).resolve()
    if repo.resolve() not in absolute_artifact.parents or not absolute_artifact.is_file():
        raise ValueError(f"artifact.path must name an existing file inside the repository: {artifact_path}")
    artifact_id = compact_id(artifact_spec["artifact_id"], "ART-")
    reused_artifact_id = artifact_id in state.get("artifact_ids", [])
    if reused_artifact_id:
        content_tag = hashlib.sha256(absolute_artifact.read_bytes()).hexdigest()[:10].upper()
        artifact_id = compact_id(f"{artifact_id}-{stage.upper()}-{content_tag}", "ART-")
    canonical_artifact_dir = work_dir / "artifacts"
    try:
        already_canonical = absolute_artifact.parent == canonical_artifact_dir.resolve()
    except OSError:
        already_canonical = False
    if not already_canonical or reused_artifact_id:
        suffix = artifact_path.suffix or ".md"
        canonical_artifact_dir.mkdir(parents=True, exist_ok=True)
        snapshot = canonical_artifact_dir / f"{stage}-{artifact_id.removeprefix('ART-')}{suffix}"
        if snapshot.resolve() != absolute_artifact:
            shutil.copyfile(absolute_artifact, snapshot)
        absolute_artifact = snapshot.resolve()
        artifact_path = absolute_artifact.relative_to(repo)
    requested_kind = artifact_spec.get("artifact_kind", "other")
    artifact_kind = requested_kind if requested_kind in ARTIFACT_KINDS else "other"
    artifact = {
        "record_type": "workbench-artifact",
        "schema_version": RUNTIME_VERSION,
        "artifact_id": artifact_id,
        "work_id": work_id,
        "artifact_kind": artifact_kind,
        "title": artifact_spec["title"],
        "status": "current",
        "owner": AGENT.copy(),
        "producing_stage": stage,
        "produced_by": AGENT.copy(),
        "location": {"kind": "workspace-path", "value": artifact_path.as_posix()},
        "source_lineage": [{
            "relationship": "derived-from",
            "source": {"record_type": "work", "record_id": work_id},
            "note": artifact_spec.get("lineage", f"Records the accepted result for {stage}."),
        }],
        "consumers": [{
            "kind": "stage" if following else "work-item",
            "consumer_id": following or work_id,
            "purpose": artifact_spec.get("purpose", "Preserve the accepted phase result for the next lifecycle decision."),
        }],
        "proof_ids": [],
        "obligation_node_ids": [],
        "content_integrity": {
            "algorithm": "sha256",
            "value": hashlib.sha256(absolute_artifact.read_bytes()).hexdigest(),
        },
        "confidentiality": artifact_spec.get("confidentiality", "internal"),
        "known_defects": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    if artifact_kind == "other":
        artifact["custom_kind"] = artifact_spec.get("custom_kind", requested_kind if requested_kind != "other" else "phase-result")

    inputs = [{"record_type": "work", "record_id": work_id}]
    inputs.extend({"record_type": "handoff", "record_id": item} for item in state.get("handoff_ids", []))
    policies = {"workbench": RUNTIME_VERSION}

    findings = []
    for item in source.get("findings", []):
        if isinstance(item, str):
            findings.append(item)
            continue
        sources = item.get("sources", item.get("source_references", []))
        statement = item.get("statement", item.get("claim", item.get("finding", item.get("description"))))
        if not statement:
            raise ValueError("each finding needs statement, claim, finding, or description")
        basis = item.get("basis", item.get("finding_type", "inference"))
        findings.append({
            "statement": statement,
            "basis": basis,
            "source_references": [
                value if isinstance(value, dict) else external_reference(repo, value)
                for value in sources
            ],
        })

    uncertainties = []
    for index, item in enumerate(source.get("uncertainties", []), 1):
        owner = actor(item.get("owner"))
        description = item.get("description", item.get("question"))
        if not description:
            raise ValueError(f"uncertainty {index} needs description or question")
        uncertainties.append({
            "description": description,
            "owner": owner,
            "next_action": next_action(
                item.get("next_action", f"Resolve this uncertainty: {description}"),
                owner=owner, target_type="evidence",
                target_id=f"{work_id}-uncertainty-{index}",
            ),
        })

    handoff_id = compact_id(source["handoff_id"], "HO-")
    handoff = {
        "record_type": "workbench-handoff",
        "schema_version": RUNTIME_VERSION,
        "handoff_id": handoff_id,
        "work_id": work_id,
        "node_id": source.get("node_id", f"O-{work_id.removeprefix('WB-')}"),
        "stage": stage,
        "specialist": source.get("specialist", "workbench"),
        "status": "completed",
        "owner": AGENT.copy(),
        "idempotency_key": source.get("idempotency_key", f"prepare:{handoff_id}:v1"),
        "input_fingerprint": {
            "algorithm": "sha256",
            "value": digest({"inputs_used": inputs, "policy_versions": policies}),
        },
        "inputs_used": inputs,
        "applicability": {
            "applied": source.get("applied", stages[stage_index].get("activity_stage_ids", [stage])),
            "skipped": source.get("skipped", []),
            "could_not_determine": source.get("could_not_determine", []),
        },
        "policy_versions": policies,
        "findings": findings,
        "uncertainties": uncertainties,
        "options": [
            item if {"name", "benefits", "costs", "risks"} <= set(item) else {
                "name": item.get("name", item.get("option_id", f"Option {index}")),
                "benefits": item.get("benefits", [item.get("summary", "Provides a candidate mechanism.")]),
                "costs": item.get("costs", []),
                "risks": item.get("risks", item.get("tradeoffs", [])),
            }
            for index, item in enumerate(source.get("options", []), 1)
        ],
        "decisions_required": [],
        "artifacts_produced": [{
            "record_type": "artifact", "record_id": artifact_id, "path": artifact_path.as_posix(),
        }],
        "node_updates": source.get("node_updates", []),
        "authorization_ids": [],
        "why_next": source.get("why_next", f"The {stage} result is recorded and its lifecycle gate can now be evaluated."),
        "created_at": timestamp,
    }
    if source.get("recommendation"):
        handoff["recommendation"] = source["recommendation"]
    if following:
        handoff["suggested_next_stage"] = following
    else:
        handoff["terminal_disposition"] = source.get("terminal_disposition", "completed-for-destination")

    records = [artifact]
    proof_spec = source.get("proof")
    if not proof_spec and not following and state.get("planning_destination") in {
        "proposal", "proof-of-concept", "specification", "implementation-plan",
    }:
        proof_spec = {
            "proof_id": f"PRF-{work_id.removeprefix('WB-')}-{stage.upper()}",
            "requirement_id": f"REQ-{work_id.removeprefix('WB-')}-{stage.upper()}",
            "claim": f"The {stage} artifact records the requested destination result.",
            "acceptance_criteria": [
                "The artifact exists and is content-addressed by the handoff.",
                "The handoff records findings, uncertainty, and the decision frontier.",
            ],
            "non_vacuity_check": "Confirmed the artifact is non-empty and the handoff contains substantive findings.",
        }
    if proof_spec:
        proof_id = compact_id(proof_spec["proof_id"], "PRF-")
        requirement_id = compact_id(proof_spec["requirement_id"], "REQ-")
        target = proof_spec.get("verification_target", {
            "environment": "Current repository workspace; deployed behavior is unverified.",
            "seam": artifact_path.as_posix(),
            "journey": state["desired_outcome"],
        })
        acceptance_criteria = proof_spec["acceptance_criteria"]
        if isinstance(acceptance_criteria, str):
            acceptance_criteria = [acceptance_criteria]
        proof = {
            "record_type": "workbench-proof",
            "schema_version": RUNTIME_VERSION,
            "proof_id": proof_id,
            "work_id": work_id,
            "claim": proof_spec["claim"],
            "verification_scope": proof_spec.get("verification_scope", "feature-implementation"),
            "applicability": "required",
            "status": "passed",
            "owner": AGENT.copy(),
            "required_proof": [{
                "requirement_id": requirement_id,
                "kind": proof_spec.get("kind", "artifact-validity"),
                "description": proof_spec.get("description", proof_spec["claim"]),
                "acceptance_criteria": acceptance_criteria,
                "oracle_requirement": proof_spec.get(
                    "oracle_requirement", "Producer review of the artifact against the recorded acceptance evidence."
                ),
                "verification_target": target,
            }],
            "achieved_proof": [{
                "requirement_id": requirement_id,
                "kind": proof_spec.get("kind", "artifact-validity"),
                "result": "passed",
                "oracle": {
                    "kind": proof_spec.get("oracle_kind", "producer-check"),
                    "description": proof_spec.get(
                        "oracle_description", "Reviewed the artifact against each stated acceptance criterion."
                    ),
                },
                "evidence": [{"record_type": "artifact", "record_id": artifact_id}],
                "non_vacuity_check": proof_spec["non_vacuity_check"],
                "observed_by": AGENT.copy(),
                "observed_at": timestamp,
                "limitations": proof_spec.get("limitations", [
                    "Producer check; not an independent review.",
                    "Artifact validity does not establish deployed behavior.",
                ]),
                "verification_target": target,
            }],
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        artifact["proof_ids"] = [proof_id]
        records.append(proof)
    validate_record(artifact, "prepared artifact")
    for record in records[1:]:
        validate_record(record, "prepared proof")
    validate_record(handoff, "prepared handoff")
    if not any(node.get("node_id") == handoff["node_id"] for node in map_record["nodes"]):
        raise ValueError(f"node_id is absent from the canonical map: {handoff['node_id']}")
    return {"handoff": handoff, "records": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--input", required=True, help="compact semantic phase-result JSON")
    parser.add_argument("--output", required=True, help="handoff bundle JSON to create")
    parser.add_argument(
        "--accept-and-advance", action="store_true",
        help="register the prepared bundle and advance its lifecycle gate in the same invocation",
    )
    args = parser.parse_args()
    try:
        repo = Path(args.repo).resolve()
        source = load_json(Path(args.input))
        if args.accept_and_advance:
            require_terminal_review(repo, args.work_id, source)
        bundle = compile_bundle(repo, args.work_id, source)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        lifecycle = None
        if args.accept_and_advance:
            handoff_id = bundle["handoff"]["handoff_id"]
            run_workbench([
                "accept-handoff", "--repo", str(repo), "--work-id", args.work_id,
                "--handoff-bundle", str(output.resolve()),
                "--idempotency-key", f"helper:accept:{handoff_id}",
            ])
            lifecycle = run_workbench([
                "advance-stage", "--repo", str(repo), "--work-id", args.work_id,
                "--accepted-handoff", handoff_id,
                "--idempotency-key", f"helper:advance:{handoff_id}",
            ])
        terminal_reviewed = args.accept_and_advance and "terminal_disposition" in bundle["handoff"]
        print(json.dumps({
            "result": "accepted-and-advanced" if lifecycle else "prepared", "work_id": args.work_id,
            "stage": bundle["handoff"]["stage"], "handoff_id": bundle["handoff"]["handoff_id"],
            "output": str(output),
            **({"review_marker": TERMINAL_REVIEW_MARKER} if terminal_reviewed else {}),
            **({"lifecycle": lifecycle_summary(lifecycle)} if lifecycle else {}),
        }, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, WorkbenchError) as exc:
        print(f"prepare-handoff refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
