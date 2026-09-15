#!/usr/bin/env python3
"""Render a read-only status projection from persisted Workbench records.

This command intentionally does not replay events, prove transitions, grant an
authorization, or mutate its inputs.  It performs only the structural and
cross-reference checks needed to avoid presenting an obviously incoherent
checkpoint as a trustworthy status view.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - dependency failure path
    raise SystemExit(
        "Status projection requires the 'jsonschema' package (including 'referencing')."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIFECYCLE = ROOT / "schemas" / "workbench-lifecycle.schema.json"

RECORD_ID_FIELDS = {
    "workbench-state": "work_id",
    "workbench-event": "event_id",
    "workbench-map": "map_id",
    "workbench-artifact": "artifact_id",
    "workbench-decision": "decision_id",
    "workbench-proof": "proof_id",
    "workbench-authorization": "authorization_id",
    "workbench-handoff": "handoff_id",
}

SCHEMA_FILE_BY_RECORD_TYPE = {
    record_type: f"{record_type}.schema.json" for record_type in RECORD_ID_FIELDS
}

REFERENCE_TYPE_TO_RECORD_TYPE = {
    "event": "workbench-event",
    "map": "workbench-map",
    "artifact": "workbench-artifact",
    "decision": "workbench-decision",
    "proof": "workbench-proof",
    "authorization": "workbench-authorization",
    "handoff": "workbench-handoff",
}

STATE_POINTERS = {
    "artifact_ids": "workbench-artifact",
    "decision_ids": "workbench-decision",
    "proof_ids": "workbench-proof",
    "authorization_ids": "workbench-authorization",
    "handoff_ids": "workbench-handoff",
}

TERMINAL_NODE_STATUSES = {
    "evidence-established",
    "decided",
    "completed",
    "excluded",
    "superseded",
}


class ProjectionError(ValueError):
    """Raised when a checkpoint cannot be projected safely."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProjectionError(message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProjectionError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ProjectionError(f"invalid JSON in {path}: {exc}") from exc
    require(isinstance(value, dict), f"{path}: expected a JSON object")
    return value


def display_path(raw: str | Path) -> str:
    return Path(raw).as_posix()


def actor_label(actor: Any) -> str:
    if not isinstance(actor, dict):
        return "unknown owner"
    return str(actor.get("display_name") or actor.get("actor_id") or "unknown owner")


def detail(record: dict[str, Any]) -> dict[str, str]:
    return {
        "label": record["record_type"].removeprefix("workbench-").replace("-", " "),
        "path": record["_display_path"],
    }


def load_records(record_dir: Path, shown_record_dir: str) -> list[dict[str, Any]]:
    require(record_dir.is_dir(), f"record directory does not exist: {record_dir}")
    paths = sorted(record_dir.glob("*.json"), key=lambda item: item.name)
    require(paths, f"record directory contains no JSON records: {record_dir}")

    records: list[dict[str, Any]] = []
    for path in paths:
        record = load_object(path)
        record_type = record.get("record_type")
        require(
            record_type in RECORD_ID_FIELDS,
            f"{path.name}: missing or unknown record_type {record_type!r}",
        )
        id_field = RECORD_ID_FIELDS[record_type]
        require(
            isinstance(record.get(id_field), str) and record[id_field],
            f"{path.name}: missing non-empty {id_field}",
        )
        record["_filename"] = path.name
        record["_display_path"] = f"{shown_record_dir.rstrip('/')}/{path.name}"
        records.append(record)
    return records


def validate_record_schemas(
    records: list[dict[str, Any]], schema_dir: Path
) -> None:
    schema_paths = sorted(schema_dir.glob("workbench-*.schema.json"))
    require(schema_paths, f"no Workbench schemas found beside lifecycle: {schema_dir}")
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for path in schema_paths:
        schema = load_object(path)
        Draft202012Validator.check_schema(schema)
        require(isinstance(schema.get("$id"), str), f"{path.name}: missing schema $id")
        schemas[path.name] = schema
        resources.append((schema["$id"], Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)

    for record in records:
        schema_name = SCHEMA_FILE_BY_RECORD_TYPE[record["record_type"]]
        require(schema_name in schemas, f"missing record schema: {schema_name}")
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        serialized_record = {
            key: value for key, value in record.items() if not key.startswith("_")
        }
        errors = sorted(
            validator.iter_errors(serialized_record), key=lambda item: list(item.path)
        )
        if errors:
            error = errors[0]
            pointer = "/".join(str(part) for part in error.path) or "<root>"
            raise ProjectionError(
                f"{record['_filename']} fails {schema_name} at {pointer}: {error.message}"
            )


def index_records(
    records: Iterable[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_type = record["record_type"]
        record_id = record[RECORD_ID_FIELDS[record_type]]
        require(record_id not in by_id, f"duplicate record ID: {record_id}")
        by_type[record_type].append(record)
        by_id[record_id] = record
    return dict(by_type), by_id


def validate_checkpoint(
    records: list[dict[str, Any]], lifecycle: dict[str, Any]
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    by_type, by_id = index_records(records)
    require(
        len(by_type.get("workbench-state", [])) == 1,
        "checkpoint must contain exactly one workbench-state record",
    )
    require(
        len(by_type.get("workbench-map", [])) == 1,
        "checkpoint must contain exactly one workbench-map record",
    )
    state = by_type["workbench-state"][0]
    map_record = by_type["workbench-map"][0]

    work_id = state["work_id"]
    mismatches = sorted(
        record["_filename"]
        for record in records
        if record.get("work_id") != work_id
    )
    require(not mismatches, f"records with a different work_id: {', '.join(mismatches)}")
    require(state.get("map_id") == map_record.get("map_id"), "state map_id does not match map record")

    registry = lifecycle.get("x-workbench")
    require(isinstance(registry, dict), "lifecycle is missing x-workbench registry")
    routes = {
        route.get("id"): route
        for route in registry.get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }
    stages = {
        stage.get("id"): stage
        for stage in registry.get("stages", [])
        if isinstance(stage, dict) and isinstance(stage.get("id"), str)
    }
    route_selection = state.get("route_selection")
    require(isinstance(route_selection, dict), "state route_selection must be an object")
    route_id = route_selection.get("route")
    require(route_id in routes, f"state references unknown lifecycle route: {route_id!r}")
    current_stage = state.get("current_stage")
    require(current_stage in stages, f"state references unknown lifecycle stage: {current_stage!r}")

    stage_states = state.get("stages")
    require(isinstance(stage_states, list) and stage_states, "state stages must be a non-empty array")
    stage_ids = [stage.get("stage_id") for stage in stage_states if isinstance(stage, dict)]
    require(len(stage_ids) == len(stage_states), "each state stage must be an object with stage_id")
    require(len(stage_ids) == len(set(stage_ids)), "state contains duplicate stage IDs")
    require(current_stage in stage_ids, "current_stage has no corresponding state stage")
    unknown_stages = sorted(set(stage_ids) - set(stages))
    require(not unknown_stages, f"state contains unknown lifecycle stages: {', '.join(unknown_stages)}")
    route_order = routes[route_id].get("ordered_stages", [])
    require(
        all(stage_id in route_order for stage_id in stage_ids),
        "state contains stages outside its lifecycle route",
    )
    require(
        state.get("planning_destination") in routes[route_id].get("allowed_destinations", []),
        "planning destination is not allowed by the selected lifecycle route",
    )

    for pointer_field, target_type in STATE_POINTERS.items():
        pointers = state.get(pointer_field)
        require(isinstance(pointers, list), f"state {pointer_field} must be an array")
        for record_id in pointers:
            require(record_id in by_id, f"state {pointer_field} has dangling ID: {record_id}")
            require(
                by_id[record_id]["record_type"] == target_type,
                f"state {pointer_field} points to wrong record type: {record_id}",
            )

    if state.get("latest_event_id") is not None:
        latest_event_id = state["latest_event_id"]
        require(latest_event_id in by_id, f"state latest_event_id is dangling: {latest_event_id}")
        require(
            by_id[latest_event_id]["record_type"] == "workbench-event",
            "state latest_event_id does not point to an event",
        )

    nodes = map_record.get("nodes")
    require(isinstance(nodes, list) and nodes, "map nodes must be a non-empty array")
    node_by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        require(isinstance(node, dict), "each map node must be an object")
        node_id = node.get("node_id")
        require(isinstance(node_id, str) and node_id, "each map node needs a non-empty node_id")
        require(node_id not in node_by_id, f"duplicate map node ID: {node_id}")
        node_by_id[node_id] = node
    require(
        map_record.get("desired_outcome_node_id") in node_by_id,
        "map desired_outcome_node_id is dangling",
    )
    edges = map_record.get("edges")
    require(isinstance(edges, list), "map edges must be an array")
    for edge in edges:
        require(isinstance(edge, dict), "each map edge must be an object")
        for endpoint in ("from_node_id", "to_node_id"):
            require(edge.get(endpoint) in node_by_id, f"map edge has dangling {endpoint}: {edge.get(endpoint)!r}")

    def validate_record_refs(value: Any, source: str) -> None:
        if isinstance(value, dict):
            reference_type = value.get("record_type")
            if reference_type in REFERENCE_TYPE_TO_RECORD_TYPE:
                record_id = value.get("record_id")
                require(record_id in by_id, f"{source} has dangling {reference_type} reference: {record_id}")
                require(
                    by_id[record_id]["record_type"]
                    == REFERENCE_TYPE_TO_RECORD_TYPE[reference_type],
                    f"{source} has wrong record type for reference: {record_id}",
                )
            elif reference_type == "work":
                require(
                    value.get("record_id") == work_id,
                    f"{source} references a different work item: {value.get('record_id')}",
                )
            elif reference_type == "node":
                require(
                    value.get("record_id") in node_by_id,
                    f"{source} has dangling node reference: {value.get('record_id')}",
                )
            for child in value.values():
                validate_record_refs(child, source)
        elif isinstance(value, list):
            for child in value:
                validate_record_refs(child, source)

    for record in records:
        validate_record_refs(record, record["_filename"])

    for artifact in by_type.get("workbench-artifact", []):
        for proof_id in artifact.get("proof_ids", []):
            require(
                proof_id in by_id and by_id[proof_id]["record_type"] == "workbench-proof",
                f"artifact {artifact['artifact_id']} has dangling proof ID: {proof_id}",
            )
        for node_id in artifact.get("obligation_node_ids", []):
            require(
                node_id in node_by_id and node_by_id[node_id].get("kind") == "obligation",
                f"artifact {artifact['artifact_id']} has invalid obligation node: {node_id}",
            )

    for proof in by_type.get("workbench-proof", []):
        if proof.get("status") != "passed":
            continue
        required_ids = {item.get("requirement_id") for item in proof.get("required_proof", [])}
        passed_ids = {
            item.get("requirement_id")
            for item in proof.get("achieved_proof", [])
            if item.get("result") == "passed"
        }
        require(
            required_ids and required_ids == passed_ids,
            f"passed proof {proof['proof_id']} does not cover every required proof item",
        )

    for decision in by_type.get("workbench-decision", []):
        node_id = decision.get("node_id")
        if node_id is not None:
            require(node_id in node_by_id, f"decision {decision['decision_id']} has dangling node_id")
            require(node_by_id[node_id].get("kind") == "decision", f"decision {decision['decision_id']} points to a non-decision node")
    for authorization in by_type.get("workbench-authorization", []):
        decision_id = authorization.get("decision_id")
        if decision_id is not None:
            require(decision_id in by_id, f"authorization {authorization['authorization_id']} has dangling decision_id")
            require(by_id[decision_id]["record_type"] == "workbench-decision", f"authorization {authorization['authorization_id']} points to a non-decision record")

    return by_type, by_id, state, map_record, routes[route_id]


def make_projection(
    by_type: dict[str, list[dict[str, Any]]],
    by_id: dict[str, dict[str, Any]],
    state: dict[str, Any],
    map_record: dict[str, Any],
    route: dict[str, Any],
    lifecycle_path: str,
) -> dict[str, Any]:
    stage_states = state["stages"]
    stage_counts: dict[str, int] = defaultdict(int)
    for stage in stage_states:
        stage_counts[str(stage.get("status", "unknown"))] += 1
    current_stage = next(
        stage for stage in stage_states if stage["stage_id"] == state["current_stage"]
    )
    nodes = map_record["nodes"]
    node_by_id = {node["node_id"]: node for node in nodes}

    learned: list[dict[str, Any]] = []
    for handoff in sorted(by_type.get("workbench-handoff", []), key=lambda item: item["handoff_id"]):
        for finding in handoff.get("findings", []):
            learned.append(
                {
                    "statement": finding,
                    "basis": "specialist finding",
                    "source_id": handoff["handoff_id"],
                    "path": handoff["_display_path"],
                }
            )
    for proof in sorted(by_type.get("workbench-proof", []), key=lambda item: item["proof_id"]):
        if proof.get("status") == "passed":
            learned.append(
                {
                    "statement": proof.get("claim", "Unnamed claim"),
                    "basis": "passed proof record",
                    "source_id": proof["proof_id"],
                    "path": proof["_display_path"],
                }
            )

    decisions: list[dict[str, Any]] = []
    for decision in sorted(by_type.get("workbench-decision", []), key=lambda item: item["decision_id"]):
        recommendation = decision.get("recommendation") or {}
        resolution = decision.get("resolution") or {}
        receipt = decision.get("consequence_receipt") or {}
        decisions.append(
            {
                "decision_id": decision["decision_id"],
                "question": decision.get("question", "Unnamed decision"),
                "state": decision.get("state", "unknown"),
                "authority": decision.get("authority", "unknown"),
                "owner": actor_label(decision.get("owner")),
                "recommendation": recommendation.get("choice"),
                "recommendation_rationale": recommendation.get("rationale"),
                "selected_option_id": resolution.get("selected_option_id"),
                "consequence_summary": receipt.get("consequence_summary"),
                "rejected_alternatives": receipt.get("alternatives_not_selected", []),
                "alternatives": [
                    {
                        "option_id": option.get("option_id"),
                        "name": option.get("name", "Unnamed option"),
                        "benefits": option.get("benefits", []),
                        "costs": option.get("costs", []),
                        "risks": option.get("risks", []),
                    }
                    for option in decision.get("options", [])
                    if isinstance(option, dict)
                ],
                "path": decision["_display_path"],
            }
        )

    state_next = state.get("next_action") or {}
    target = node_by_id.get(state_next.get("target_id"), {})
    if not target and state_next.get("target_id") in by_id:
        target_record = by_id[state_next["target_id"]]
        node_id = target_record.get("node_id")
        target = node_by_id.get(node_id, {})
    why_next = {
        "action": state_next.get("description", "No next action is recorded."),
        "owner": actor_label(state_next.get("owner")),
        "reason": target.get("why_it_matters") or state["route_selection"].get("rationale"),
        "target_type": state_next.get("target_type"),
        "target_id": state_next.get("target_id"),
    }

    uncertainties: list[dict[str, Any]] = []
    for fog in map_record.get("fog", []):
        if fog.get("status") == "unresolved":
            uncertainties.append(
                {
                    "kind": "fog",
                    "id": fog.get("fog_id"),
                    "description": fog.get("description"),
                    "owner": actor_label(fog.get("owner")),
                    "path": map_record["_display_path"],
                }
            )
    for node in nodes:
        if node.get("status") not in TERMINAL_NODE_STATUSES:
            uncertainties.append(
                {
                    "kind": node.get("kind", "node"),
                    "id": node["node_id"],
                    "description": node.get("question") or node.get("title"),
                    "owner": actor_label(node.get("owner")),
                    "status": node.get("status"),
                    "path": map_record["_display_path"],
                }
            )

    def frontier_item(node: dict[str, Any]) -> dict[str, Any]:
        next_action = node.get("next_action") or {}
        return {
            "node_id": node["node_id"],
            "kind": node.get("kind"),
            "title": node.get("title"),
            "status": node.get("status"),
            "owner": actor_label(node.get("owner")),
            "next_action": next_action.get("description"),
            "path": map_record["_display_path"],
        }

    agent_ready = [
        frontier_item(node)
        for node in nodes
        if node.get("status") in {"ready", "in-progress", "evidence-blocked"}
        and (node.get("owner") or {}).get("kind") == "agent"
    ]
    user_decisions = [
        frontier_item(node)
        for node in nodes
        if node.get("kind") == "decision"
        and node.get("status") == "waiting-for-human"
    ]
    external_blockers = [
        frontier_item(node)
        for node in nodes
        if node.get("status") == "external-blocked"
        or (
            node.get("status") == "evidence-blocked"
            and (node.get("owner") or {}).get("kind") == "external"
        )
    ]

    authorizations: list[dict[str, Any]] = []
    active_grants: list[str] = []
    for authorization in sorted(
        by_type.get("workbench-authorization", []),
        key=lambda item: item["authorization_id"],
    ):
        status = authorization.get("status", "unknown")
        action = authorization.get("action", "unknown")
        if status == "granted":
            active_grants.append(action)
        authorizations.append(
            {
                "authorization_id": authorization["authorization_id"],
                "action": action,
                "status": status,
                "authority": actor_label(authorization.get("authority")),
                "constraints": (authorization.get("scope") or {}).get("constraints", []),
                "path": authorization["_display_path"],
            }
        )

    claim_boundaries: list[dict[str, str]] = []
    for proof in sorted(by_type.get("workbench-proof", []), key=lambda item: item["proof_id"]):
        for result in proof.get("achieved_proof", []):
            for limitation in result.get("limitations", []):
                claim_boundaries.append(
                    {
                        "statement": limitation,
                        "source_id": proof["proof_id"],
                        "path": proof["_display_path"],
                    }
                )
    for artifact in sorted(by_type.get("workbench-artifact", []), key=lambda item: item["artifact_id"]):
        for defect in artifact.get("known_defects", []):
            statement = defect if isinstance(defect, str) else json.dumps(defect, sort_keys=True)
            claim_boundaries.append(
                {
                    "statement": statement,
                    "source_id": artifact["artifact_id"],
                    "path": artifact["_display_path"],
                }
            )
    for authorization in authorizations:
        for constraint in authorization["constraints"]:
            claim_boundaries.append(
                {
                    "statement": constraint,
                    "source_id": authorization["authorization_id"],
                    "path": authorization["path"],
                }
            )

    return {
        "projection": {
            "kind": "read-only-status",
            "structural_checks": "schema-and-cross-reference-passed",
            "event_replay": "not-performed",
            "transition_proof": "not-performed",
            "mutation": "none",
        },
        "work": {
            "work_id": state["work_id"],
            "title": state.get("title", "Untitled work"),
            "desired_outcome": state.get("desired_outcome"),
            "route": state["route_selection"]["route"],
            "route_rationale": state["route_selection"].get("rationale"),
            "planning_destination": state.get("planning_destination"),
            "status": state.get("status"),
            "owner": actor_label(state.get("owner")),
        },
        "where": {
            "current_stage": state["current_stage"],
            "current_stage_status": current_stage.get("status"),
            "stage_counts": dict(sorted(stage_counts.items())),
            "route_stage_count": len(route.get("ordered_stages", [])),
            "recorded_stage_count": len(stage_states),
            "state_revision": state.get("state_revision"),
            "updated_at": state.get("updated_at"),
            "path": state["_display_path"],
        },
        "learned": learned,
        "decisions": decisions,
        "why_next": why_next,
        "uncertainty": uncertainties,
        "frontier": {
            "agent_ready": agent_ready,
            "user_decisions": user_decisions,
            "external_blockers": external_blockers,
        },
        "authorization_boundary": {
            "active_grants": active_grants,
            "records": authorizations,
        },
        "claim_boundaries": claim_boundaries,
        "details": [detail(record) for record in sorted(records_for_details(by_type), key=lambda item: item["_filename"])]
        + [{"label": "lifecycle registry", "path": lifecycle_path}],
    }


def records_for_details(
    by_type: dict[str, list[dict[str, Any]]]
) -> Iterable[dict[str, Any]]:
    for records in by_type.values():
        yield from records


def markdown_link(label: str, path: str) -> str:
    return f"[{label}]({path.replace(' ', '%20')})"


def render_markdown(view: dict[str, Any]) -> str:
    work = view["work"]
    where = view["where"]
    lines = [
        "> **Read-only projection.** This summarizes persisted records after structural checks. "
        "It is not event replay, transition proof, a new authorization, or completion proof.",
        "",
        f"# Workbench status — {work['title']}",
        "",
        "## Where am I?",
        "",
        f"- Work: `{work['work_id']}` — {work['status']} on the `{work['route']}` route, targeting `{work['planning_destination']}`.",
        f"- Current stage: `{where['current_stage']}` ({where['current_stage_status']}); revision {where['state_revision']} as of {where['updated_at']}.",
        f"- Recorded progress: {where['recorded_stage_count']} of {where['route_stage_count']} route stages represented; "
        + ", ".join(f"{count} {status}" for status, count in where["stage_counts"].items())
        + ".",
        f"- Desired outcome: {work['desired_outcome']}",
        f"- Detail: {markdown_link('state', where['path'])}",
        "",
        "## What have we learned?",
        "",
    ]
    if view["learned"]:
        lines.extend(
            f"- {item['statement']} ({item['basis']}; {markdown_link(item['source_id'], item['path'])})"
            for item in view["learned"]
        )
    else:
        lines.append("- No persisted specialist findings or passed proof claims are available.")

    lines.extend(["", "## What did we decide, and which alternatives were rejected?", ""])
    if view["decisions"]:
        for decision in view["decisions"]:
            lines.append(
                f"- **{decision['decision_id']} ({decision['state']}, {decision['authority']}):** "
                f"{decision['question']} Owner: {decision['owner']}. {markdown_link('details', decision['path'])}"
            )
            if decision["state"] == "confirmed":
                lines.append(f"  - Selected: `{decision['selected_option_id'] or 'factual determination'}`.")
                if decision["consequence_summary"]:
                    lines.append(f"  - Consequence: {decision['consequence_summary']}")
                for rejected in decision["rejected_alternatives"]:
                    lines.append(
                        f"  - Rejected `{rejected['option_id']}`: {rejected['reason']}"
                    )
            else:
                lines.append("  - No option has been confirmed.")
            if decision["recommendation"]:
                lines.append(
                    f"  - Recommendation: {decision['recommendation']} — {decision['recommendation_rationale']}"
                )
            for option in decision["alternatives"]:
                lines.append(f"  - Option `{option['option_id']}`: {option['name']}")
    else:
        lines.append("- No decision records are present.")

    why_next = view["why_next"]
    lines.extend(
        [
            "",
            "## Why is this next?",
            "",
            f"- Next action: {why_next['action']}",
            f"- Owner: {why_next['owner']}.",
            f"- Reason: {why_next['reason']}",
            "",
            "## What is still uncertain?",
            "",
        ]
    )
    if view["uncertainty"]:
        lines.extend(
            f"- `{item['id']}` ({item.get('status', item['kind'])}): {item['description']} "
            f"Owner: {item['owner']}. {markdown_link('map', item['path'])}"
            for item in view["uncertainty"]
        )
    else:
        lines.append("- No unresolved fog or nonterminal map nodes are recorded.")

    lines.extend(["", "## Ready frontier", ""])
    frontier_labels = (
        ("Agent-ready", "agent_ready"),
        ("User decisions", "user_decisions"),
        ("External blockers", "external_blockers"),
    )
    for label, key in frontier_labels:
        items = view["frontier"][key]
        if not items:
            lines.append(f"- {label}: none.")
            continue
        summary = "; ".join(
            f"`{item['node_id']}` {item['title']} — {item['next_action'] or 'no next action recorded'}"
            for item in items
        )
        lines.append(f"- {label}: {summary}")

    boundary = view["authorization_boundary"]
    lines.extend(["", "## Authorization and claim boundaries", ""])
    if boundary["active_grants"]:
        lines.append(f"- Active granted actions: {', '.join(f'`{item}`' for item in boundary['active_grants'])}.")
    else:
        lines.append("- Active granted actions: none. A requested authorization is not permission to act.")
    for authorization in boundary["records"]:
        lines.append(
            f"- `{authorization['authorization_id']}`: `{authorization['action']}` is `{authorization['status']}`; "
            f"authority: {authorization['authority']}. {markdown_link('details', authorization['path'])}"
        )
    if view["claim_boundaries"]:
        for claim in view["claim_boundaries"]:
            lines.append(
                f"- Claim boundary: {claim['statement']} ({markdown_link(claim['source_id'], claim['path'])})"
            )
    else:
        lines.append("- No explicit proof limitation, artifact defect, or authorization constraint is recorded.")

    lines.extend(["", "## Detail paths", ""])
    for item in view["details"]:
        lines.append(f"- {markdown_link(item['label'], item['path'])}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a read-only projection of a Workbench checkpoint."
    )
    parser.add_argument("record_dir", help="directory containing one work checkpoint")
    parser.add_argument(
        "--lifecycle",
        default=str(DEFAULT_LIFECYCLE),
        help="machine-readable lifecycle registry (default: repository schema)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit deterministic JSON instead of Markdown",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    record_dir = Path(args.record_dir)
    lifecycle_path = Path(args.lifecycle)
    try:
        records = load_records(record_dir, display_path(args.record_dir))
        lifecycle = load_object(lifecycle_path)
        validate_record_schemas(records, lifecycle_path.parent)
        by_type, by_id, state, map_record, route = validate_checkpoint(records, lifecycle)
        view = make_projection(
            by_type,
            by_id,
            state,
            map_record,
            route,
            display_path(args.lifecycle),
        )
    except ProjectionError as exc:
        print(f"Cannot render Workbench status: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(view, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_markdown(view), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
