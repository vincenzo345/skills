#!/usr/bin/env python3
"""Validate the first Workbench contract-and-fixture slice.

This checks structural and cross-file invariants only. It deliberately does not
claim that the future Workbench runtime, specialist behavior, or human
comprehension has been proven.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - dependency failure path
    raise SystemExit(
        "Validation requires the 'jsonschema' package (including 'referencing')."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
PACKAGED_SCHEMAS = (
    ROOT / "skills" / "workbench" / "references" / "schemas"
)
SCENARIOS = ROOT / "tests" / "scenarios"
COMPARISON = ROOT / "tests" / "comparison"

EXPECTED_SCHEMA_FILES = {
    "workbench-common.schema.json",
    "workbench-intake.schema.json",
    "workbench-routing-receipt.schema.json",
    "workbench-lifecycle.schema.json",
    "workbench-state.schema.json",
    "workbench-event.schema.json",
    "workbench-map.schema.json",
    "workbench-artifact.schema.json",
    "workbench-decision.schema.json",
    "workbench-proof.schema.json",
    "workbench-authorization.schema.json",
    "workbench-handoff.schema.json",
}

EXPECTED_ENTRANCES = {
    "existing-process",
    "unproven-process",
    "brownfield-feature",
    "proposal-only",
    "small-change-fast-lane",
}


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.counts: Counter[str] = Counter()

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def passed(self, category: str) -> None:
        self.counts[category] += 1


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc


def iter_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                refs.append(child)
            else:
                refs.extend(iter_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(iter_refs(child))
    return refs


def resolve_json_pointer(document: Any, fragment: str) -> Any:
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise KeyError(f"unsupported non-pointer fragment #{fragment}")
    current = document
    for raw_part in fragment[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def validate_schemas(check: Check) -> tuple[dict[str, Any], Registry[Any]]:
    paths = sorted(SCHEMAS.glob("*.json"))
    actual_names = {path.name for path in paths}
    check.require(
        actual_names == EXPECTED_SCHEMA_FILES,
        "schemas: expected exactly the lifecycle/common schemas and ten planned record schemas; "
        f"missing={sorted(EXPECTED_SCHEMA_FILES - actual_names)}, "
        f"extra={sorted(actual_names - EXPECTED_SCHEMA_FILES)}",
    )

    documents: dict[str, Any] = {}
    by_id: dict[str, Any] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for path in paths:
        try:
            schema = load_json(path)
            Draft202012Validator.check_schema(schema)
            schema_id = schema["$id"]
            check.require(schema_id not in by_id, f"{path.name}: duplicate $id {schema_id}")
            documents[path.name] = schema
            by_id[schema_id] = schema
            resources.append((schema_id, Resource.from_contents(schema)))
            check.passed("schemas")
        except (KeyError, ValueError, TypeError) as exc:
            check.errors.append(f"{path.relative_to(ROOT)}: {exc}")

        packaged_path = PACKAGED_SCHEMAS / path.name
        check.require(
            packaged_path.is_file(),
            f"packaged schemas: missing {packaged_path.relative_to(ROOT)}",
        )
        if packaged_path.is_file():
            check.require(
                packaged_path.read_bytes() == path.read_bytes(),
                f"packaged schemas: {path.name} differs from the canonical root schema",
            )

    registry = Registry().with_resources(resources)
    for name, schema in documents.items():
        base = schema["$id"]
        for ref in iter_refs(schema):
            resolved = urljoin(base, ref)
            document_uri, fragment = urldefrag(resolved)
            check.require(
                document_uri in by_id,
                f"schemas/{name}: unresolved schema document in $ref {ref}",
            )
            if document_uri not in by_id:
                continue
            try:
                resolve_json_pointer(by_id[document_uri], fragment)
                registry.get_or_retrieve(document_uri)
            except Exception as exc:  # registry/pointer diagnostics are user-facing
                check.errors.append(f"schemas/{name}: unresolved $ref {ref}: {exc}")

        # Constructing a validator with the closed registry catches dialect and
        # registry wiring problems without pretending an empty instance is valid.
        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())

    lifecycle = documents.get("workbench-lifecycle.schema.json", {})
    vocabulary = lifecycle.get("$defs", {})
    machine_registry = lifecycle.get("x-workbench", {})
    stage_ids = set(vocabulary.get("stageId", {}).get("enum", []))
    phase_ids = set(vocabulary.get("phaseId", {}).get("enum", []))
    route_ids = set(vocabulary.get("routeKind", {}).get("enum", []))
    destination_ids = set(vocabulary.get("planningDestination", {}).get("enum", []))
    work_statuses = set(vocabulary.get("workStatus", {}).get("enum", []))
    registered_stages = {item.get("id") for item in machine_registry.get("stages", [])}
    registered_phases = {item.get("id") for item in machine_registry.get("phases", [])}
    registered_routes = {item.get("id") for item in machine_registry.get("routes", [])}
    registered_destinations = {
        item.get("id") for item in machine_registry.get("destinations", [])
    }
    registered_statuses = {item.get("id") for item in machine_registry.get("work_statuses", [])}
    check.require(stage_ids == registered_stages, "lifecycle: stage enum and registry differ")
    check.require(phase_ids == registered_phases, "lifecycle: phase enum and registry differ")
    check.require(route_ids == registered_routes, "lifecycle: route enum and registry differ")
    check.require(
        destination_ids == registered_destinations,
        "lifecycle: planning-destination enum and registry differ",
    )
    check.require(work_statuses == registered_statuses, "lifecycle: work-status enum and registry differ")
    check.require(
        "data-model-design" in stage_ids,
        "lifecycle: data-model-design is not a first-class activity",
    )
    phase_memberships: Counter[str] = Counter()
    phase_for_stage: dict[str, str] = {}
    for phase in machine_registry.get("phases", []):
        phase_id = phase.get("id", "<missing>")
        activities = phase.get("activities", [])
        check.require(bool(activities), f"lifecycle phase {phase_id}: no activities")
        check.require(
            len(activities) == len(set(activities)),
            f"lifecycle phase {phase_id}: duplicate activities",
        )
        check.require(
            set(activities) <= stage_ids,
            f"lifecycle phase {phase_id}: unknown activity stage",
        )
        check.require(
            phase.get("default_checkpoint") in activities,
            f"lifecycle phase {phase_id}: default checkpoint is not a phase activity",
        )
        for activity in activities:
            phase_memberships[activity] += 1
            phase_for_stage[activity] = phase_id
    check.require(
        set(phase_memberships) == stage_ids,
        "lifecycle: every activity stage must belong to a phase",
    )
    check.require(
        all(count == 1 for count in phase_memberships.values()),
        "lifecycle: every activity stage must belong to exactly one phase",
    )
    for route in machine_registry.get("routes", []):
        route_id = route.get("id", "<missing>")
        sequence = set(route.get("ordered_stages", []))
        check.require(sequence <= stage_ids, f"lifecycle route {route_id}: unknown stage")
        check.require(
            set(route.get("conditional_stages", [])) <= sequence,
            f"lifecycle route {route_id}: conditional stage is not on the route",
        )
        check.require(
            set(route.get("allowed_destinations", [])) <= destination_ids,
            f"lifecycle route {route_id}: unknown planning destination",
        )
        check.require(
            bool(route.get("ordered_stages")) and route["ordered_stages"][0] == "intake",
            f"lifecycle route {route_id}: route must start at intake",
        )
    for stage in machine_registry.get("stages", []):
        check.require(
            all(
                stage.get(field)
                for field in (
                    "id",
                    "phase_id",
                    "applicability_rule",
                    "entry_gate",
                    "exit_gate",
                )
            ),
            f"lifecycle stage {stage.get('id', '<missing>')}: incomplete executable registry entry",
        )
        check.require(
            stage.get("phase_id") == phase_for_stage.get(stage.get("id")),
            f"lifecycle stage {stage.get('id', '<missing>')}: phase assignment differs from phase registry",
        )
    proof_kinds = set(
        documents.get("workbench-proof.schema.json", {})
        .get("$defs", {})
        .get("proofKind", {})
        .get("enum", [])
    )
    artifact_kinds = set(
        documents.get("workbench-artifact.schema.json", {})
        .get("properties", {})
        .get("artifact_kind", {})
        .get("enum", [])
    )
    check.require(
        "data-model" in artifact_kinds,
        "artifact contract: data-model is not a first-class artifact kind",
    )
    for destination in machine_registry.get("destinations", []):
        destination_id = destination.get("id", "<missing>")
        check.require(
            destination.get("completion_stage") in stage_ids,
            f"lifecycle destination {destination_id}: unknown completion stage",
        )
        check.require(
            destination.get("completion_status")
            in {"completed-for-destination", "completed-for-outcome"},
            f"lifecycle destination {destination_id}: invalid completion status",
        )
        check.require(
            destination.get("required_proof_kind") in proof_kinds,
            f"lifecycle destination {destination_id}: unknown proof kind",
        )

    return documents, registry


def workflow_stage_ids() -> list[str]:
    text = (ROOT / "docs" / "workbench" / "WORKFLOW.md").read_text(encoding="utf-8")
    heading = "## Canonical activity registry"
    if heading not in text:
        heading = "## Canonical stage registry"
    section = text.split(heading, 1)[1].split("## Canonical routes", 1)[0]
    return re.findall(r"^\| `([a-z][a-z0-9-]+)` \|", section, flags=re.MULTILINE)


def validate_scenarios(
    check: Check, schemas: dict[str, Any], registry: Registry[Any]
) -> None:
    schema = load_json(SCENARIOS / "scenario.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema, registry=registry, format_checker=FormatChecker()
    )
    scenario_paths = sorted(SCENARIOS.glob("*/scenario.json"))
    check.require(len(scenario_paths) == 5, "scenarios: expected exactly five route fixtures")

    lifecycle = schemas["workbench-lifecycle.schema.json"]
    stage_enum = lifecycle["$defs"]["stageId"]["enum"]
    documented_stages = workflow_stage_ids()
    check.require(len(documented_stages) == len(set(documented_stages)), "workflow: duplicate stage IDs")
    check.require(
        set(stage_enum) == set(documented_stages),
        "scenario schema: stage enum differs from the canonical workflow registry",
    )

    route_values = set(lifecycle["$defs"]["routeKind"]["enum"])
    check.require(
        route_values == EXPECTED_ENTRANCES,
        "common schema: routeKind must represent all five canonical entrances",
    )

    machine_routes = {
        route["id"]: route for route in lifecycle["x-workbench"]["routes"]
    }
    terminal_statuses = {
        item["id"]
        for item in lifecycle["x-workbench"]["work_statuses"]
        if item["terminal"]
    }

    def is_subsequence(values: list[str], canonical: list[str]) -> bool:
        iterator = iter(canonical)
        return all(any(candidate == value for candidate in iterator) for value in values)

    seen_entrances: set[str] = set()
    seen_authorization_actions: set[str] = set()
    for path in scenario_paths:
        try:
            scenario = load_json(path)
        except ValueError as exc:
            check.errors.append(str(exc))
            continue
        errors = sorted(validator.iter_errors(scenario), key=lambda error: list(error.path))
        for error in errors:
            pointer = "/".join(str(part) for part in error.path) or "<root>"
            check.errors.append(f"{path.relative_to(ROOT)}:{pointer}: {error.message}")
        if errors:
            continue

        entrance = scenario["entrance"]
        seen_entrances.add(entrance)
        route = scenario["expected"]["route"]
        given = scenario["given"]
        expected = scenario["expected"]
        prefix = str(path.relative_to(ROOT))

        check.require(route[0] == "intake", f"{prefix}: every route must start at intake")
        check.require(
            expected["valid_stop_after"] == route[-1],
            f"{prefix}: valid_stop_after must equal the fixture's final route stage",
        )
        check.require(
            set(expected["required_artifacts"]).isdisjoint(expected["must_not_create"]),
            f"{prefix}: an artifact is both required and forbidden",
        )
        authorized_actions = set(given["authorized_actions"])
        check.require(
            "implementation" in authorized_actions or "implementation" not in route,
            f"{prefix}: implementation appears without implementation authorization",
        )
        check.require(
            "deployment" in authorized_actions or "release" not in route,
            f"{prefix}: release appears without deployment authorization",
        )
        check.require(
            entrance != "proposal-only" or route[-1] == "proposal",
            f"{prefix}: proposal-only must stop at proposal",
        )
        check.require(
            entrance != "unproven-process" or "process-validation" in route,
            f"{prefix}: unproven-process must include process-validation",
        )
        check.require(
            entrance not in {"brownfield-feature", "small-change-fast-lane"}
            or "brownfield-reconnaissance" in route,
            f"{prefix}: codebase entrances require brownfield reconnaissance",
        )
        check.require(
            entrance != "small-change-fast-lane" or "standards-resolution" in route,
            f"{prefix}: the fast lane still requires standards resolution",
        )
        check.require(
            scenario["planning_destination"]
            in machine_routes[entrance]["allowed_destinations"],
            f"{prefix}: planning destination is not allowed for {entrance}",
        )
        check.require(
            expected["terminal_disposition"] in terminal_statuses,
            f"{prefix}: terminal_disposition is not terminal",
        )
        if entrance != "unproven-process":
            check.require(
                is_subsequence(route, machine_routes[entrance]["ordered_stages"]),
                f"{prefix}: expected route order contradicts the lifecycle registry",
            )
        else:
            unproven_prefix = machine_routes[entrance]["ordered_stages"]
            check.require(
                route[: len(unproven_prefix)] == unproven_prefix,
                f"{prefix}: unproven route does not begin with its canonical validation path",
            )
            last_validation = len(route) - 1 - route[::-1].index("process-validation")
            post_validation = route[last_validation + 1 :]
            check.require(
                is_subsequence(post_validation, machine_routes["existing-process"]["ordered_stages"]),
                f"{prefix}: supported unproven route does not hand off to existing-process order",
            )
        expected_node_ids = {
            item["node_id"] for item in expected["required_map_nodes"]
        }
        for node in expected["required_map_nodes"]:
            check.require(
                set(node["depends_on"]) <= expected_node_ids,
                f"{prefix}: {node['node_id']} depends on an unregistered expected node",
            )
        check.require(
            len({item["decision_id"] for item in expected["decisions"]})
            == len(expected["decisions"]),
            f"{prefix}: duplicate decision expectation IDs",
        )
        for authorization in expected["authorizations"]:
            action = authorization["action"]
            seen_authorization_actions.add(action)
            if authorization["status"] == "granted":
                check.require(
                    action in authorized_actions,
                    f"{prefix}: {action} is expected granted but absent from given authorization",
                )
            else:
                check.require(
                    action not in authorized_actions,
                    f"{prefix}: {action} is {authorization['status']} but marked authorized",
                )
        check.passed("scenarios")

    check.require(
        seen_entrances == EXPECTED_ENTRANCES,
        f"scenarios: entrance coverage differs; seen={sorted(seen_entrances)}",
    )
    required_boundaries = {
        "repository-mutation",
        "tracker-publication",
        "implementation",
        "commit",
        "deployment",
        "closure",
    }
    check.require(
        required_boundaries <= seen_authorization_actions,
        "scenarios: the suite does not exercise every authorization boundary",
    )


def validate_record_fixture(
    check: Check, schemas: dict[str, Any], registry: Registry[Any]
) -> None:
    folder = ROOT / "tests" / "records" / "proposal-only-checkpoint"
    record_schemas = {
        "state.json": "workbench-state.schema.json",
        "event.json": "workbench-event.schema.json",
        "map.json": "workbench-map.schema.json",
        "artifact.json": "workbench-artifact.schema.json",
        "decision.json": "workbench-decision.schema.json",
        "proof.json": "workbench-proof.schema.json",
        "authorization.json": "workbench-authorization.schema.json",
        "handoff.json": "workbench-handoff.schema.json",
    }
    records: dict[str, Any] = {}
    for filename, schema_name in record_schemas.items():
        path = folder / filename
        check.require(path.is_file(), f"record fixture: missing {path.relative_to(ROOT)}")
        if not path.is_file():
            continue
        record = load_json(path)
        records[filename] = record
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            pointer = "/".join(str(part) for part in error.path) or "<root>"
            check.errors.append(f"{path.relative_to(ROOT)}:{pointer}: {error.message}")
        check.passed("record instances")

    if len(records) != len(record_schemas):
        return
    work_ids = {record["work_id"] for record in records.values()}
    check.require(len(work_ids) == 1, "record fixture: records have different work IDs")
    state = records["state.json"]
    map_record = records["map.json"]
    event = records["event.json"]
    check.require(
        state["current_stage"] in {stage["stage_id"] for stage in state["stages"]},
        "record fixture: current stage is absent from stage state",
    )
    node_ids = {node["node_id"] for node in map_record["nodes"]}
    check.require(
        map_record["desired_outcome_node_id"] in node_ids,
        "record fixture: desired outcome node is missing",
    )
    for edge in map_record["edges"]:
        check.require(
            {edge["from_node_id"], edge["to_node_id"]} <= node_ids,
            f"record fixture: edge {edge['edge_id']} has a dangling node",
        )
    check.require(
        event["state_revision_after"] == event["state_revision_before"] + 1,
        "record fixture: event revision is not a single increment",
    )
    check.require(
        state["latest_event_id"] == event["event_id"],
        "record fixture: latest event pointer does not match",
    )
    check.require(
        records["artifact.json"]["artifact_id"] in state["artifact_ids"],
        "record fixture: artifact is absent from state registry pointers",
    )
    check.require(
        records["decision.json"]["decision_id"] in state["decision_ids"],
        "record fixture: decision is absent from state registry pointers",
    )
    check.require(
        records["proof.json"]["proof_id"] in state["proof_ids"],
        "record fixture: proof is absent from state registry pointers",
    )
    check.require(
        records["authorization.json"]["authorization_id"]
        in state["authorization_ids"],
        "record fixture: authorization is absent from state registry pointers",
    )
    check.require(
        records["handoff.json"]["handoff_id"] in state["handoff_ids"],
        "record fixture: handoff is absent from state registry pointers",
    )

    contract_cases = ROOT / "tests" / "records" / "contract-cases"
    schema_by_record_type = {
        "workbench-decision": "workbench-decision.schema.json",
        "workbench-authorization": "workbench-authorization.schema.json",
    }
    positive_cases: dict[str, Any] = {}
    for path in sorted(contract_cases.glob("*.json")):
        record = load_json(path)
        positive_cases[path.name] = record
        schema_name = schema_by_record_type.get(record.get("record_type"))
        check.require(schema_name is not None, f"{path.relative_to(ROOT)}: unknown record type")
        if schema_name is None:
            continue
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        errors = list(validator.iter_errors(record))
        check.require(not errors, f"{path.relative_to(ROOT)}: positive contract case is invalid")
        check.passed("record instances")

    def rejects(schema_name: str, instance: Any, name: str) -> None:
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        check.require(bool(list(validator.iter_errors(instance))), f"negative contract case passed: {name}")
        check.passed("negative contract cases")

    confirmed = positive_cases.get("confirmed-decision.json")
    delegation = positive_cases.get("delegation-authorization.json")
    delegated_decision = positive_cases.get("delegated-decision.json")
    if confirmed is not None:
        missing_receipt = deepcopy(confirmed)
        missing_receipt.pop("consequence_receipt", None)
        rejects(
            "workbench-decision.schema.json",
            missing_receipt,
            "confirmed consequential decision without consequence receipt",
        )

        factual = deepcopy(confirmed)
        factual["decision_id"] = "DEC-FACT-001"
        factual["question"] = "Did the proposal completeness proof pass?"
        factual["materiality"] = "routine"
        factual["authority"] = "factual"
        factual.pop("options", None)
        factual.pop("recommendation", None)
        factual.pop("consequence_receipt", None)
        factual["resolution"]["basis"] = "factual-evidence"
        factual["resolution"].pop("selected_option_id", None)
        factual_validator = Draft202012Validator(
            schemas["workbench-decision.schema.json"],
            registry=registry,
            format_checker=FormatChecker(),
        )
        check.require(
            not list(factual_validator.iter_errors(factual)),
            "positive contract case is invalid: factual determination without choice options",
        )
        check.passed("record instances")

    if delegation is not None:
        missing_bounds = deepcopy(delegation)
        missing_bounds.pop("delegation", None)
        rejects(
            "workbench-authorization.schema.json",
            missing_bounds,
            "decision delegation without delegation bounds",
        )

    if delegated_decision is not None:
        wrong_basis = deepcopy(delegated_decision)
        wrong_basis["resolution"]["basis"] = "factual-evidence"
        wrong_basis["resolution"].pop("selected_option_id", None)
        rejects(
            "workbench-decision.schema.json",
            wrong_basis,
            "delegable decision resolved as a factual determination",
        )

        delegated_map = deepcopy(map_record)
        delegated_node = next(
            node for node in delegated_map["nodes"] if node["node_id"] == "D-PROP-001"
        )
        delegated_node["status"] = "decided"
        delegated_node.pop("next_action", None)
        delegated_node["resolution"] = {
            "basis": "delegated-agent-decision",
            "rationale": "A bounded delegation settled the technical choice.",
            "resolved_at": "2026-09-14T11:40:00-05:00",
            "resolved_by": {
                "actor_id": "agent:solution-architect",
                "kind": "agent",
            },
            "references": [
                {
                    "record_type": "decision",
                    "record_id": "DEC-TECH-001",
                }
            ],
        }
        map_validator = Draft202012Validator(
            schemas["workbench-map.schema.json"],
            registry=registry,
            format_checker=FormatChecker(),
        )
        check.require(
            not list(map_validator.iter_errors(delegated_map)),
            "positive contract case is invalid: delegated map-node decision",
        )
        check.passed("record instances")

    contradictory_proof = deepcopy(records["proof.json"])
    contradictory_proof["applicability"] = "not-applicable"
    rejects(
        "workbench-proof.schema.json",
        contradictory_proof,
        "not-applicable proof reported as passed",
    )

    terminal_handoff = deepcopy(records["handoff.json"])
    terminal_handoff["handoff_id"] = "HO-PROP-TERMINAL"
    terminal_handoff["status"] = "completed"
    terminal_handoff.pop("next_action", None)
    terminal_handoff["decisions_required"] = []
    terminal_handoff["artifacts_produced"] = [
        {
            "record_type": "artifact",
            "record_id": "ART-PROP-001",
            "path": "proposals/scheduling-discovery.md",
        }
    ]
    terminal_handoff["terminal_disposition"] = "completed-for-destination"
    terminal_handoff["why_next"] = "The authorized proposal destination is complete."
    handoff_validator = Draft202012Validator(
        schemas["workbench-handoff.schema.json"],
        registry=registry,
        format_checker=FormatChecker(),
    )
    check.require(
        not list(handoff_validator.iter_errors(terminal_handoff)),
        "positive contract case is invalid: completed terminal handoff",
    )
    check.passed("record instances")

    terminal_without_destination = deepcopy(terminal_handoff)
    terminal_without_destination.pop("terminal_disposition", None)
    rejects(
        "workbench-handoff.schema.json",
        terminal_without_destination,
        "completed handoff without next stage or terminal disposition",
    )
    terminal_with_two_destinations = deepcopy(terminal_handoff)
    terminal_with_two_destinations["suggested_next_stage"] = "experience-design"
    rejects(
        "workbench-handoff.schema.json",
        terminal_with_two_destinations,
        "completed handoff with both next stage and terminal disposition",
    )

    closure_without_destination = deepcopy(records["authorization.json"])
    closure_without_destination["scope"]["targets"][0].pop(
        "planning_destination", None
    )
    rejects(
        "workbench-authorization.schema.json",
        closure_without_destination,
        "closure authorization without planning destination",
    )

    event_without_changes = deepcopy(event)
    event_without_changes.pop("changes", None)
    rejects(
        "workbench-event.schema.json",
        event_without_changes,
        "event without replayable changes",
    )

    handoff_without_key = deepcopy(records["handoff.json"])
    handoff_without_key.pop("idempotency_key", None)
    rejects(
        "workbench-handoff.schema.json",
        handoff_without_key,
        "handoff without idempotency key",
    )

    unknown_stage = deepcopy(state)
    unknown_stage["current_stage"] = "architecture"
    rejects(
        "workbench-state.schema.json",
        unknown_stage,
        "state using a noncanonical stage ID",
    )


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
RAW_SEGMENT_RE = re.compile(
    r"(?:^|\s+-\s+)\(([^)]+)\)\s*(.*?)(?=\s+-\s+\([^)]+\)\s*|$)"
)
NORMALIZED_UTTERANCE_RE = re.compile(
    r"^(?:>\s*)?(?:\[\d{1,2}:\d{2}(?::\d{2})?\]\s*)?\*\*([^*]+):\*\*\s*(.+)$"
)


def tokens(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in WORD_RE.findall(text))


def raw_utterances(path: Path) -> list[tuple[str, tuple[str, ...]]]:
    utterances: list[tuple[str, tuple[str, ...]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        for match in RAW_SEGMENT_RE.finditer(line):
            utterances.append((match.group(1).strip(), tokens(match.group(2))))
    return utterances


def normalized_utterances(path: Path) -> list[tuple[str, tuple[str, ...]]]:
    utterances: list[tuple[str, tuple[str, ...]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = NORMALIZED_UTTERANCE_RE.match(line.strip())
        if match:
            utterances.append((match.group(1).strip(), tokens(match.group(2))))
    return utterances


def unresolved_flag_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    try:
        flags = text.split("# Flags", 1)[1].split("---", 1)[0]
    except IndexError:
        return -1
    return sum(1 for line in flags.splitlines() if line.lstrip().startswith("- "))


def validate_evidence_fixture(check: Check) -> None:
    folder = COMPARISON / "evidence-intake"
    expected = load_json(folder / "expected.json")
    source_path = folder / expected["source"]
    check.require(source_path.is_file(), "evidence fixture: source file does not exist")
    source = raw_utterances(source_path)
    source_words = tuple(word for _, utterance in source for word in utterance)
    source_multiset = Counter(source_words)
    source_speakers = {utterance: speaker for speaker, utterance in source}

    for case in expected["cases"]:
        artifact_path = folder / case["artifact"]
        check.require(artifact_path.is_file(), f"evidence fixture: missing {case['artifact']}")
        if not artifact_path.is_file():
            continue
        actual = normalized_utterances(artifact_path)
        actual_words = tuple(word for _, utterance in actual for word in utterance)
        actual_values = {
            "word_multiset_preserved": Counter(actual_words) == source_multiset,
            "token_order_preserved": actual_words == source_words,
            "speaker_attribution_valid": all(
                source_speakers.get(utterance) == speaker for speaker, utterance in actual
            )
            and len(actual) == len(source),
            "unresolved_defects": unresolved_flag_count(artifact_path),
        }
        check.require(
            actual_values == case["expected"],
            f"evidence fixture {case['artifact']}: computed {actual_values}, "
            f"expected {case['expected']}",
        )
        check.passed("comparison cases")


def validate_process_fixture(check: Check) -> None:
    folder = COMPARISON / "process-model"
    expected = load_json(folder / "expected.json")
    for source in expected["sources"]:
        check.require((folder / source).is_file(), f"process fixture: missing source {source}")
    required_dimensions = {
        "external_trigger",
        "desired_outcome",
        "actors",
        "systems",
        "manual_steps_include",
        "branches_include",
        "controls_include",
        "waits_include",
        "unresolved_questions_include",
        "evidence_tasks_include",
    }
    check.require(
        required_dimensions <= set(expected["expected_model"]),
        "process fixture: expected model is missing a required process dimension",
    )
    check.passed("comparison cases")


def validate_decision_fixture(check: Check) -> None:
    session = load_json(COMPARISON / "informed-decision" / "session.json")
    state = "proposed"
    saw_confusion = False
    saw_receipt = False
    for turn in session["turns"]:
        if turn["kind"] == "confusion":
            saw_confusion = True
        elif turn["kind"] == "consequence-receipt":
            saw_receipt = True
        elif turn["kind"] == "confirmation" and saw_receipt:
            state = "confirmed"
        if "expected_decision_state_after_turn" in turn:
            check.require(
                turn["expected_decision_state_after_turn"] == state,
                "decision fixture: confusion or confirmation expectation contradicts policy",
            )
    check.require(saw_confusion and saw_receipt, "decision fixture: missing confusion or receipt")
    check.passed("comparison cases")


def validate_coverage_fixture(check: Check) -> None:
    fixture = load_json(COMPARISON / "coverage-and-proof" / "cases.json")
    requirement_ids = {item["id"] for item in fixture["requirements"]}
    required_proof = {item["id"]: item["required_proof"] for item in fixture["requirements"]}
    for case in fixture["ticket_sets"]:
        covered = {requirement for ticket in case["tickets"] for requirement in ticket["covers"]}
        valid = covered == requirement_ids
        check.require(valid == case["expected_coverage_valid"], f"coverage fixture {case['name']}: bad oracle")
        check.passed("comparison cases")

    ranks = {"local-implementation": 1, "deployed-behavior": 2}
    for case in fixture["proof_cases"]:
        valid = (
            case["actual_population"] > 0
            and case["reported_status"] == "passed"
            and ranks[case["achieved_proof"]] >= ranks[required_proof[case["criterion"]]]
        )
        check.require(valid == case["expected_valid"], f"proof fixture {case['name']}: bad oracle")
        check.passed("comparison cases")


def validate_uncertainty_fixture(check: Check) -> None:
    fixture = load_json(COMPARISON / "uncertainty-map" / "case.json")
    node_ids = {node["node_id"] for node in fixture["nodes"]}
    check.require(len(node_ids) == len(fixture["nodes"]), "uncertainty fixture: duplicate node IDs")
    check.require(fixture["initial_fog"], "uncertainty fixture: fog must be observable before it is clarified")
    required_events = {
        "fog-recorded",
        "question-formed",
        "evidence-task-created",
        "evidence-attached",
        "decision-confirmed",
        "obligation-created",
        "deliverable-created",
        "evidence-invalidated",
    }
    check.require(
        required_events <= set(fixture["events"]),
        "uncertainty fixture: the preservation sequence is incomplete",
    )
    for edge in fixture["dependencies"]:
        check.require(
            {edge["from"], edge["to"]} <= node_ids,
            "uncertainty fixture: dependency references an unknown node",
        )
    checkpoints = {item["name"]: item for item in fixture["checkpoints"]}
    for checkpoint in checkpoints.values():
        frontier_ids = {
            node_id
            for owner_nodes in checkpoint["ready_frontier"].values()
            for node_id in owner_nodes
        }
        check.require(
            frontier_ids <= node_ids,
            f"uncertainty fixture {checkpoint['name']}: frontier has an unknown node",
        )
        check.require(
            set(checkpoint["blocked"]) <= node_ids,
            f"uncertainty fixture {checkpoint['name']}: blocker has an unknown node",
        )
    check.require(
        checkpoints["after-question-formation"]["ready_frontier"]["agent"]
        == ["E-OBSERVE-001"],
        "uncertainty fixture: question formation must expose the evidence task",
    )
    check.require(
        checkpoints["after-evidence"]["ready_frontier"]["user"]
        == ["D-PROCESS-001"],
        "uncertainty fixture: evidence must expose the human decision",
    )
    check.require(
        checkpoints["after-invalidation"]["ready_frontier"]["agent"]
        == ["E-OBSERVE-001"],
        "uncertainty fixture: invalidation must reopen the evidence dependency",
    )
    check.passed("comparison cases")

def validate_comparison_fixtures(check: Check) -> None:
    validate_evidence_fixture(check)
    validate_process_fixture(check)
    validate_decision_fixture(check)
    validate_coverage_fixture(check)
    validate_uncertainty_fixture(check)


def main() -> int:
    check = Check()
    try:
        schemas, registry = validate_schemas(check)
        validate_scenarios(check, schemas, registry)
        validate_record_fixture(check, schemas, registry)
        validate_comparison_fixtures(check)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        check.errors.append(f"validation setup: {exc}")

    if check.errors:
        print("Workbench foundation validation FAILED:")
        for error in check.errors:
            print(f"- {error}")
        return 1

    summary = ", ".join(f"{count} {name}" for name, count in sorted(check.counts.items()))
    print(f"Workbench foundation validation passed: {summary}.")
    print("Claim boundary: this validator proves contract/fixture coherence only; runtime proof is reported by the separate black-box suite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
