"""Regression tests for Workbench v0.5 reasoning continuity."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from conftest import WorkbenchCLI, assert_rejected, assert_succeeded, persisted_bytes
from test_workbench_v03 import artifact, canonical_digest, routed_repo


WORK_ID = "WB-INTAKE-001"


def proposed_decision(timestamp: str) -> dict:
    return {
        "record_type": "workbench-decision",
        "schema_version": "0.5.0",
        "decision_id": "DEC-V05-DIRECTION",
        "work_id": WORK_ID,
        "question": "Which system should own the expanded domain?",
        "materiality": "consequential",
        "authority": "user-owned",
        "state": "proposed",
        "owner": {"actor_id": "human:runtime-test", "kind": "human"},
        "next_action": {
            "description": "Choose the system boundary after reviewing the evidence.",
            "owner": {"actor_id": "human:runtime-test", "kind": "human"},
            "target_type": "decision",
            "target_id": "DEC-V05-DIRECTION",
        },
        "options": [
            {
                "option_id": "OPT-V05-EXTEND",
                "name": "Extend this system",
                "benefits": ["One system of record."],
                "costs": ["Larger migration."],
                "risks": ["Broader coupling."],
            },
            {
                "option_id": "OPT-V05-SEPARATE",
                "name": "Use a separate system",
                "benefits": ["Narrower current application."],
                "costs": ["Integration contract."],
                "risks": ["Split identity."],
            },
        ],
        "provenance": {
            "artifact_inputs": [],
            "evidence": [],
            "prior_decisions": [],
            "assumptions": [],
            "policy_versions": {"workbench": "0.5.0"},
        },
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def handoff_bundle(artifact_record: dict, *, workbench_policy: str = "0.5.0") -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    inputs = [{"record_type": "work", "record_id": WORK_ID}]
    policies = {"workbench": workbench_policy}
    decision = proposed_decision(timestamp)
    handoff = {
        "record_type": "workbench-handoff",
        "schema_version": "0.5.0",
        "handoff_id": "HO-V05-REASONING",
        "work_id": WORK_ID,
        "node_id": "O-INTAKE-001",
        "stage": "outcome-framing",
        "specialist": "data-model-audit",
        "status": "completed",
        "owner": {"actor_id": "agent:workbench", "kind": "agent"},
        "idempotency_key": "runtime-test:v05-handoff:001",
        "input_fingerprint": {
            "algorithm": "sha256",
            "value": canonical_digest({"inputs_used": inputs, "policy_versions": policies}),
        },
        "inputs_used": inputs,
        "applicability": {"applied": ["data-model-audit"], "skipped": [], "could_not_determine": []},
        "policy_versions": policies,
        "findings": ["The existing tables do not enforce tenant ownership consistently."],
        "uncertainties": [
            {
                "description": "Live row populations and active writers are not yet known.",
                "owner": {"actor_id": "agent:workbench", "kind": "agent"},
                "next_action": {
                    "description": "Inspect live-safe schema metadata and writer paths.",
                    "owner": {"actor_id": "agent:workbench", "kind": "agent"},
                    "target_type": "evidence",
                    "target_id": WORK_ID,
                },
            }
        ],
        "options": [],
        "decisions_required": [
            {"decision_id": decision["decision_id"], "question": decision["question"]}
        ],
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
        "why_next": "The human can decide the system boundary while evidence work continues.",
        "created_at": timestamp,
    }
    return {"handoff": handoff, "records": [artifact_record, decision]}


def accept_bundle(cli: WorkbenchCLI, repo: Path, path: Path):
    return cli.invoke(
        "accept-handoff",
        repo,
        (
            "--work-id", WORK_ID,
            "--handoff-bundle", str(path),
            "--idempotency-key", "runtime-test:v05-accept:001",
            "--expected-revision", "1",
            "--actor", "agent:workbench",
            "--json",
        ),
    )


def test_accepted_handoff_projects_reasoning_into_resume(tmp_path: Path, workbench_cli: WorkbenchCLI) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    bundle_path = tmp_path / "v05-handoff.json"
    bundle_path.write_text(json.dumps(handoff_bundle(artifact(repo)), indent=2) + "\n", encoding="utf-8")

    accepted = accept_bundle(workbench_cli, repo, bundle_path)

    assert_succeeded(accepted)
    view = json.loads(accepted.stdout)
    assert [item["title"] for item in view["human_control"]["learned"]] == [
        "The existing tables do not enforce tenant ownership consistently."
    ]
    assert view["human_control"]["decisions"] == [
        {
            "node_id": view["human_control"]["decisions"][0]["node_id"],
            "question": "Which system should own the expanded domain?",
            "status": "ready",
        }
    ]
    assert view["human_control"]["uncertainties"][0]["description"] == (
        "Live row populations and active writers are not yet known."
    )
    resumed = workbench_cli.invoke("resume", repo, ("--work-id", WORK_ID, "--json"))
    assert_succeeded(resumed)
    assert json.loads(resumed.stdout)["human_control"] == view["human_control"]


def test_v05_handoff_rejects_stale_workbench_policy_atomically(
    tmp_path: Path, workbench_cli: WorkbenchCLI
) -> None:
    repo = routed_repo(tmp_path, workbench_cli)
    bundle = handoff_bundle(artifact(repo), workbench_policy="0.3.0")
    path = tmp_path / "stale-policy.json"
    path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    before = persisted_bytes(repo)

    rejected = accept_bundle(workbench_cli, repo, path)

    assert_rejected(rejected)
    assert "policy_versions.workbench" in rejected.output
    assert persisted_bytes(repo) == before
