#!/usr/bin/env python3
"""Compile compact routing semantics before Workbench route-and-start.

This helper owns the routing input's mechanical completeness. The runtime still
builds, fingerprints, compiles, and validates the immutable routing receipt.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_workbench(arguments: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("workbench.py")), *arguments, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise ValueError(detail or f"Workbench command failed: {arguments[0]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Workbench command returned invalid JSON: {arguments[0]}") from exc


ACTIONS = {
    "decision-delegation", "repository-mutation", "tracker-publication",
    "implementation", "commit", "deployment", "closure",
}
BUSINESS_BASES = {"hypothesis", "operating-process", "supplied-requirements", "technical-only"}
SOLUTION_CONTEXTS = {"greenfield", "brownfield", "process-only", "undetermined"}
ENGAGEMENT_INTENTS = {"explore", "plan", "implement", "release"}
DESTINATIONS = {
    "proposal", "proof-of-concept", "specification", "implementation-plan",
    "locally-verified-implementation", "released-software", "business-outcome",
}
STAGES = {
    "intake", "evidence-intake", "process-model", "process-validation", "outcome-framing",
    "proposal", "experience-design", "solution-architecture", "data-model-design",
    "brownfield-reconnaissance", "standards-resolution", "specification", "delivery-planning",
    "implementation", "local-verification", "release", "deployed-verification",
    "outcome-verification",
}
ROUTING_FIELDS = {
    "title", "desired_outcome", "business_basis", "solution_context",
    "engagement_intent", "planning_destination", "execution_lane",
    "runtime_route", "rationale", "evidence_references", "facts",
    "constraints", "acceptance_evidence", "assumptions",
    "unresolved_questions", "stage_recommendations",
    "authorization_boundary", "recommendation",
}


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
    return summary


def actor(value: str | dict | None) -> dict:
    if isinstance(value, dict):
        return {
            key: item for key, item in value.items()
            if key in {"actor_id", "kind", "display_name"}
        }
    if isinstance(value, str) and value not in {"human", "agent"}:
        return {"actor_id": value, "kind": "human"}
    if value == "agent":
        return {"actor_id": "agent:workbench", "kind": "agent"}
    return {"actor_id": "user:local", "kind": "human"}


def short(value: str) -> str:
    return value if len(value) <= 256 else value[:253].rstrip() + "..."


def canonical_choice(value: object, allowed: set[str], aliases: dict[str, str], default: str) -> str:
    text = str(value or "").strip().lower()
    if text in allowed:
        return text
    for token, choice in aliases.items():
        if token in text:
            return choice
    return default


def normalize(value: dict) -> dict:
    result = {key: item for key, item in value.items() if key in ROUTING_FIELDS}
    result.setdefault("title", "Workbench item")
    result.setdefault("desired_outcome", result["title"])
    result["business_basis"] = canonical_choice(
        result.get("business_basis"), BUSINESS_BASES,
        {"hypoth": "hypothesis", "process": "operating-process", "require": "supplied-requirements",
         "technical": "technical-only", "efficien": "technical-only", "engineering": "technical-only"},
        "technical-only",
    )
    context_text = str(result.get("solution_context", "")).strip().lower()
    if context_text in SOLUTION_CONTEXTS:
        result["solution_context"] = context_text
    elif "greenfield" in context_text or "new application" in context_text:
        result["solution_context"] = "greenfield"
    elif any(token in context_text for token in ("process-only", "business process", "operating process", "workflow-only")):
        result["solution_context"] = "process-only"
    elif "undetermined" in context_text or "unknown context" in context_text:
        result["solution_context"] = "undetermined"
    else:
        # Free-form descriptions of a repository, service, platform, or request
        # path are existing-software context, even when they use words such as
        # "processing".
        result["solution_context"] = "brownfield"
    result["planning_destination"] = canonical_choice(
        result.get("planning_destination"), DESTINATIONS,
        {"business": "business-outcome", "release": "released-software",
         "local": "locally-verified-implementation", "implementation plan": "implementation-plan",
         "delivery plan": "implementation-plan", "spec": "specification",
         "proof": "proof-of-concept", "prototype": "proof-of-concept",
         "option": "proposal", "recommend": "proposal", "proposal": "proposal"},
        "proposal",
    )
    lane = str(result.get("execution_lane", "")).lower()
    result["execution_lane"] = "fast" if any(token in lane for token in ("fast", "small")) else "full"
    result["engagement_intent"] = canonical_choice(
        result.get("engagement_intent"), ENGAGEMENT_INTENTS,
        {"release": "release", "implement": "implement", "fix": "implement", "plan": "plan",
         "option": "explore", "investig": "explore", "explore": "explore"},
        "explore",
    )
    result.setdefault("rationale", "Use the smallest lifecycle that reaches the requested destination.")
    if result["solution_context"] == "brownfield" and result["planning_destination"] == "proposal":
        # The legacy fast-lane route has no proposal destination. A read-only
        # brownfield proposal therefore uses the compiled full profile without
        # implying implementation scope.
        result["execution_lane"] = "full"
    for field in ("constraints", "acceptance_evidence", "assumptions", "facts"):
        result.setdefault(field, [])
    if not result["acceptance_evidence"]:
        result["acceptance_evidence"] = [f"Evidence demonstrates: {result['desired_outcome']}"]
    context = result.get("solution_context")
    lane = result.get("execution_lane")
    basis = result.get("business_basis")
    if context == "brownfield":
        result["runtime_route"] = "small-change-fast-lane" if lane == "fast" else "brownfield-feature"
    elif context == "process-only":
        result["runtime_route"] = "unproven-process" if basis == "hypothesis" else "existing-process"
    else:
        result["runtime_route"] = None
    if isinstance(result.get("title"), str):
        result["title"] = short(result["title"])
    recommendation = result.get("recommendation")
    if isinstance(recommendation, dict) and isinstance(recommendation.get("choice"), str):
        recommendation = dict(recommendation)
        recommendation["choice"] = short(recommendation["choice"])
        result["recommendation"] = recommendation
    normalized_facts = []
    for fact in result.get("facts", []):
        if isinstance(fact, dict):
            sources = fact.get(
                "source_references", fact.get("sources", fact.get("source_reference", []))
            )
            if isinstance(sources, str):
                sources = [sources]
            normalized_facts.append({
                "statement": fact["statement"],
                "source_references": sources or ["captured-intake"],
            })
        else:
            normalized_facts.append({"statement": fact, "source_references": ["captured-intake"]})
    result["facts"] = normalized_facts
    evidence = result.get("evidence_references", [])
    if not evidence:
        evidence = [source for fact in normalized_facts for source in fact["source_references"]]
    result["evidence_references"] = list(dict.fromkeys(evidence))

    # In a compact input, an open question is a proposal uncertainty unless it
    # explicitly says that lifecycle work cannot start without the answer.
    blockers = []
    assumptions = list(result["assumptions"])
    for item in value.get("unresolved_questions", []):
        if isinstance(item, str):
            assumptions.append(f"Open but non-blocking: {item}")
            continue
        question = item.get("question", item.get("description"))
        if not question:
            continue
        if not item.get("blocks_start", False):
            material = item.get("why_material")
            assumptions.append(
                f"Open but non-blocking: {question}" + (f" ({material})" if material else "")
            )
            continue
        blockers.append({
            "question": question,
            "why_material": item.get("why_material", "The answer changes lifecycle routing or authorization."),
            "owner": actor(item.get("owner")),
        })
    result["assumptions"] = list(dict.fromkeys(assumptions))
    result["unresolved_questions"] = blockers

    recommendations = []
    for item in result.get("stage_recommendations", []):
        if not isinstance(item, dict):
            continue
        stage_id = item.get("stage_id", item.get("stage"))
        if stage_id not in STAGES:
            continue
        recommendations.append({
            "stage_id": stage_id,
            "applicability": item.get("applicability", "applicable"),
            "reason": item.get("reason", "Explicitly selected by the compact routing input."),
            "evidence_references": item.get("evidence_references", []),
        })
    if result["solution_context"] in {"brownfield", "greenfield"} and not any(
        item["stage_id"] == "data-model-design" for item in recommendations
    ):
        recommendations.append({
            "stage_id": "data-model-design",
            "applicability": "not-applicable" if result["planning_destination"] == "proposal" else "undetermined",
            "reason": (
                "No implementation or persisted-data change is authorized at this options-only destination."
                if result["planning_destination"] == "proposal"
                else "Persisted-data impact was not classified in the compact routing input."
            ),
            "evidence_references": [],
        })
    if not recommendations:
        recommendations.append({
            "stage_id": "process-model" if result["solution_context"] == "process-only" else "outcome-framing",
            "applicability": "applicable",
            "reason": "Required to keep the compact routing input schema-valid for the selected context.",
            "evidence_references": [],
        })
    result["stage_recommendations"] = recommendations
    boundary = dict(result.get("authorization_boundary", {}))
    granted = set(boundary.get("granted_actions", [])) & ACTIONS
    boundary["granted_actions"] = sorted(granted)
    boundary["withheld_actions"] = sorted(ACTIONS - granted)
    result["authorization_boundary"] = boundary
    recommendation = result.get("recommendation")
    if isinstance(recommendation, str):
        recommendation = {
            "choice": short(recommendation),
            "rationale": result["rationale"],
            "assumptions": [],
            "tradeoffs": ["The recommendation remains conditional on its recorded assumptions."],
            "confidence": "medium",
        }
    elif not isinstance(recommendation, dict):
        recommendation = {
            "choice": "Proceed to the selected planning destination.",
            "rationale": result["rationale"],
            "assumptions": [],
            "tradeoffs": ["The route preserves unresolved implementation choices."],
            "confidence": "medium",
        }
    recommendation.setdefault("rationale", result["rationale"])
    recommendation.setdefault("assumptions", [])
    recommendation.setdefault("tradeoffs", ["The route preserves unresolved implementation choices."])
    recommendation.setdefault("confidence", "medium")
    result["recommendation"] = recommendation
    result.pop("compiled_plan", None)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--capture-and-start", action="store_true",
        help="capture source.request and route-and-start the normalized record in the same invocation",
    )
    args = parser.parse_args()
    try:
        repo = Path(args.repo).resolve()
        value = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.capture_and_start:
            request = value.get("request")
            if not isinstance(request, str) or not request.strip():
                raise ValueError("compact routing input needs non-empty request for --capture-and-start")
            run_workbench([
                "capture-intake", "--repo", str(repo), "--work-id", args.work_id,
                "--request", request, "--idempotency-key", f"helper:capture:{args.work_id}",
            ])
        work_dir = repo / ".workbench" / "work" / args.work_id
        unexpected = sorted(path.name for path in work_dir.iterdir() if path.name != "intake.json")
        if unexpected:
            raise ValueError(
                "pre-start work directory may contain only intake.json; move analysis artifacts elsewhere first: "
                + ", ".join(unexpected)
            )
        output = Path(args.output)
        output.write_text(json.dumps(normalize(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        lifecycle = None
        if args.capture_and_start:
            lifecycle = run_workbench([
                "route-and-start", "--repo", str(repo), "--work-id", args.work_id,
                "--routing-input", str(output.resolve()),
                "--idempotency-key", f"helper:start:{args.work_id}",
            ])
        print(json.dumps({
            "result": "captured-and-started" if lifecycle else "prepared",
            "output": str(output),
            **({"lifecycle": lifecycle_summary(lifecycle)} if lifecycle else {}),
        }, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"prepare-routing refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
