#!/usr/bin/env python3
"""Small event-sourced runtime for the Workbench skill (Python 3 stdlib only)."""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

if os.name == "nt":
    import msvcrt
else:
    import fcntl


HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE.parent / "references" / "schemas"
LIFECYCLE_PATH = SCHEMA_DIR / "workbench-lifecycle.schema.json"
RUNTIME_VERSION = "0.4.0"
WORK_ID_RE = re.compile(r"^WB-[A-Z0-9][A-Z0-9._-]{1,63}$")
BLOCKING = {"waiting-for-human", "external-blocked", "evidence-blocked"}
LEGAL_CHANGE_PREFIXES = {
    "work-started": {"work": ("/document",), "map": ("/document",)},
    "stage-completed": {
        "work": (
            "/stages/", "/current_stage", "/state_revision", "/updated_at",
            "/latest_event_id", "/next_action", "/status", "/completion",
            "/proof_ids", "/authorization_ids",
        ),
        "map": ("/nodes/", "/updated_at"),
    },
    "handoff-accepted": {
        "work": (
            "/artifact_ids", "/decision_ids", "/proof_ids",
            "/authorization_ids", "/handoff_ids", "/stages/",
            "/state_revision", "/updated_at", "/latest_event_id",
            "/next_action", "/status",
        ),
        "map": ("/nodes/", "/updated_at"),
    },
}
SCHEMA_BY_RECORD_TYPE = {
    "workbench-intake": "workbench-intake.schema.json",
    "workbench-routing-receipt": "workbench-routing-receipt.schema.json",
    "workbench-state": "workbench-state.schema.json",
    "workbench-event": "workbench-event.schema.json",
    "workbench-map": "workbench-map.schema.json",
    "workbench-artifact": "workbench-artifact.schema.json",
    "workbench-decision": "workbench-decision.schema.json",
    "workbench-proof": "workbench-proof.schema.json",
    "workbench-authorization": "workbench-authorization.schema.json",
    "workbench-handoff": "workbench-handoff.schema.json",
}
SEMANTIC_VERSION_RE = re.compile(
    r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
ACTOR_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:@/-]+$")
PROOF_ID_RE = re.compile(r"^PRF-[A-Z0-9][A-Z0-9._-]{1,63}$")
AUTHORIZATION_ID_RE = re.compile(r"^AUTH-[A-Z0-9][A-Z0-9._-]{1,63}$")
REQUIREMENT_ID_RE = re.compile(r"^REQ-[A-Z0-9][A-Z0-9._-]{1,63}$")
ARTIFACT_ID_RE = re.compile(r"^ART-[A-Z0-9][A-Z0-9._-]{1,63}$")
DECISION_ID_RE = re.compile(r"^DEC-[A-Z0-9][A-Z0-9._-]{1,63}$")
HANDOFF_ID_RE = re.compile(r"^HO-[A-Z0-9][A-Z0-9._-]{1,63}$")
PROOF_KINDS = {
    "packaging", "artifact-validity", "local-implementation", "integration",
    "deployed-behavior", "security", "performance", "accessibility",
    "recovery", "business-outcome", "manual-observation", "other",
}
AUTHORIZATION_ACTIONS = {
    "decision-delegation", "repository-mutation", "tracker-publication",
    "implementation", "commit", "deployment", "closure",
}
AUTHORIZATION_TARGET_KINDS = {
    "work", "stage", "artifact", "decision", "repository", "tracker",
    "environment", "external-system", "other",
}
ROUTING_INPUT_FIELDS = {
    "title", "desired_outcome", "business_basis", "solution_context",
    "engagement_intent", "planning_destination", "execution_lane",
    "runtime_route", "rationale", "evidence_references", "facts",
    "constraints", "acceptance_evidence", "assumptions",
    "unresolved_questions", "stage_recommendations",
    "authorization_boundary", "recommendation",
}
ROUTING_REVISION_FIELDS = {
    "revision_reason", "resolved_questions",
}
_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


class WorkbenchError(RuntimeError):
    pass


def fail(condition: bool, message: str) -> None:
    if not condition:
        raise WorkbenchError(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkbenchError(f"cannot read {path}: {exc}") from exc
    fail(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def schema_document(filename: str) -> dict[str, Any]:
    if filename not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[filename] = load_json(SCHEMA_DIR / filename)
    return _SCHEMA_CACHE[filename]


def schema_pointer(document: Any, fragment: str, label: str) -> Any:
    current = document
    if not fragment:
        return current
    fail(fragment.startswith("/"), f"{label} has unsupported schema reference fragment #{fragment}")
    for raw in fragment[1:].split("/"):
        part = raw.replace("~1", "/").replace("~0", "~")
        fail(isinstance(current, dict) and part in current,
             f"{label} schema reference points to missing component {part!r}")
        current = current[part]
    return current


def json_type_matches(value: Any, expected: str) -> bool:
    return {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }.get(expected, lambda _item: False)(value)


def schema_matches(value: Any, schema: Any, root_filename: str) -> bool:
    try:
        validate_schema_value(value, schema, root_filename, "$candidate")
    except WorkbenchError:
        return False
    return True


def validate_schema_value(value: Any, schema: Any, root_filename: str, label: str) -> None:
    """Validate the JSON Schema subset used by the bundled Workbench schemas."""
    if isinstance(schema, bool):
        fail(schema, f"{label} is rejected by schema")
        return
    fail(isinstance(schema, dict), f"{label} has an invalid bundled schema")

    reference = schema.get("$ref")
    if reference is not None:
        fail(isinstance(reference, str), f"{label} has an invalid schema reference")
        filename, separator, fragment = reference.partition("#")
        referenced_filename = filename or root_filename
        referenced_document = schema_document(referenced_filename)
        target_schema = schema_pointer(referenced_document, fragment if separator else "", label)
        validate_schema_value(value, target_schema, referenced_filename, label)

    expected_types = schema.get("type")
    if expected_types is not None:
        types = [expected_types] if isinstance(expected_types, str) else expected_types
        fail(isinstance(types, list) and types
             and all(isinstance(item, str) for item in types), f"{label} has invalid schema types")
        fail(any(json_type_matches(value, item) for item in types),
             f"{label} must have JSON type {' or '.join(types)}")
    if "const" in schema:
        fail(value == schema["const"], f"{label} must equal {schema['const']!r}")
    if "enum" in schema:
        fail(value in schema["enum"], f"{label} is not an allowed value")

    if isinstance(value, str):
        if "minLength" in schema:
            fail(len(value) >= schema["minLength"], f"{label} is too short")
        if "maxLength" in schema:
            fail(len(value) <= schema["maxLength"], f"{label} is too long")
        if "pattern" in schema:
            fail(re.search(schema["pattern"], value) is not None,
                 f"{label} does not match the required pattern")
        if schema.get("format") == "date-time":
            parse_time(value, label)
        elif schema.get("format") == "uri-reference":
            fail(not any(character.isspace() or ord(character) < 32 for character in value),
                 f"{label} is not a valid URI reference")
            try:
                urlsplit(value)
            except ValueError as exc:
                raise WorkbenchError(f"{label} is not a valid URI reference") from exc

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema:
            fail(value >= schema["minimum"], f"{label} is below its minimum")
        if "maximum" in schema:
            fail(value <= schema["maximum"], f"{label} is above its maximum")

    if isinstance(value, list):
        if "minItems" in schema:
            fail(len(value) >= schema["minItems"], f"{label} has too few items")
        if "maxItems" in schema:
            fail(len(value) <= schema["maxItems"], f"{label} has too many items")
        if schema.get("uniqueItems"):
            serialized = [canonical(item) for item in value]
            fail(len(serialized) == len(set(serialized)), f"{label} contains duplicate items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema_value(item, schema["items"], root_filename, f"{label}[{index}]")
        if "contains" in schema:
            matches = sum(schema_matches(item, schema["contains"], root_filename) for item in value)
            fail(matches >= schema.get("minContains", 1), f"{label} does not contain a required item")
            if "maxContains" in schema:
                fail(matches <= schema["maxContains"], f"{label} contains too many matching items")

    if isinstance(value, dict):
        if "minProperties" in schema:
            fail(len(value) >= schema["minProperties"], f"{label} has too few properties")
        if "maxProperties" in schema:
            fail(len(value) <= schema["maxProperties"], f"{label} has too many properties")
        required = schema.get("required", [])
        fail(all(item in value for item in required),
             f"{label} is missing fields: {', '.join(item for item in required if item not in value)}")
        properties = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key, item in value.items():
            matched = False
            if key in properties:
                validate_schema_value(item, properties[key], root_filename, f"{label}.{key}")
                matched = True
            for pattern, pattern_schema in patterns.items():
                if re.search(pattern, key):
                    validate_schema_value(item, pattern_schema, root_filename, f"{label}.{key}")
                    matched = True
            if not matched and "additionalProperties" in schema:
                additional = schema["additionalProperties"]
                fail(additional is not False, f"{label} has unsupported field {key!r}")
                if isinstance(additional, dict):
                    validate_schema_value(item, additional, root_filename, f"{label}.{key}")
        if "propertyNames" in schema:
            for key in value:
                validate_schema_value(key, schema["propertyNames"], root_filename, f"{label} property {key!r}")

    for subschema in schema.get("allOf", []):
        validate_schema_value(value, subschema, root_filename, label)
    if "anyOf" in schema:
        fail(any(schema_matches(value, item, root_filename) for item in schema["anyOf"]),
             f"{label} does not match any allowed schema")
    if "oneOf" in schema:
        matches = sum(schema_matches(value, item, root_filename) for item in schema["oneOf"])
        fail(matches == 1, f"{label} must match exactly one allowed schema")
    if "not" in schema:
        fail(not schema_matches(value, schema["not"], root_filename),
             f"{label} matches a forbidden schema")
    if "if" in schema:
        branch = "then" if schema_matches(value, schema["if"], root_filename) else "else"
        if branch in schema:
            validate_schema_value(value, schema[branch], root_filename, label)


def validate_against_bundled_schema(record: dict[str, Any], filename: str, label: str) -> None:
    validate_schema_value(record, schema_document(filename), filename, label)


def require_shape(value: Any, required: set[str], allowed: set[str], label: str) -> dict[str, Any]:
    fail(isinstance(value, dict), f"{label} must be an object")
    missing = required - set(value)
    extra = set(value) - allowed
    fail(not missing, f"{label} is missing fields: {', '.join(sorted(missing))}")
    fail(not extra, f"{label} has unsupported fields: {', '.join(sorted(extra))}")
    return value


def require_nonempty(value: Any, label: str) -> str:
    fail(isinstance(value, str) and bool(value.strip()), f"{label} must be a non-empty string")
    return value


def validate_actor(value: Any, label: str) -> None:
    actor_value = require_shape(
        value, {"actor_id", "kind"}, {"actor_id", "kind", "display_name"}, label
    )
    actor_id = actor_value["actor_id"]
    fail(isinstance(actor_id, str) and ACTOR_ID_RE.fullmatch(actor_id) is not None,
         f"{label}.actor_id is invalid")
    fail(actor_value["kind"] in {"human", "agent", "system", "external"},
         f"{label}.kind is invalid")
    if "display_name" in actor_value:
        require_nonempty(actor_value["display_name"], f"{label}.display_name")


def validate_record_ref(value: Any, label: str) -> None:
    reference = require_shape(
        value, {"record_type", "record_id"}, {"record_type", "record_id", "path", "uri"}, label
    )
    fail(reference["record_type"] in {
        "work", "event", "map", "node", "artifact", "decision", "proof",
        "authorization", "handoff", "external",
    }, f"{label}.record_type is invalid")
    require_nonempty(reference["record_id"], f"{label}.record_id")


def validate_proof_record(record: dict[str, Any], label: str) -> None:
    required = {
        "record_type", "schema_version", "proof_id", "work_id", "claim",
        "applicability", "status", "owner", "required_proof", "achieved_proof",
        "created_at", "updated_at",
    }
    allowed = required | {
        "verification_scope", "next_action", "blockers", "failure_summary",
        "not_applicable_reason",
    }
    value = require_shape(record, required, allowed, label)
    fail(value["record_type"] == "workbench-proof", f"{label}.record_type is invalid")
    fail(isinstance(value["schema_version"], str)
         and SEMANTIC_VERSION_RE.fullmatch(value["schema_version"]) is not None,
         f"{label}.schema_version is invalid")
    fail(isinstance(value["proof_id"], str) and PROOF_ID_RE.fullmatch(value["proof_id"]) is not None,
         f"{label}.proof_id is invalid")
    fail(isinstance(value["work_id"], str) and WORK_ID_RE.fullmatch(value["work_id"]) is not None,
         f"{label}.work_id is invalid")
    require_nonempty(value["claim"], f"{label}.claim")
    validate_actor(value["owner"], f"{label}.owner")
    fail(isinstance(value["required_proof"], list), f"{label}.required_proof must be an array")
    fail(isinstance(value["achieved_proof"], list), f"{label}.achieved_proof must be an array")
    is_v03 = tuple(int(part) for part in value["schema_version"].split("-")[0].split(".")[:3]) >= (0, 3, 0)
    if is_v03:
        fail(isinstance(value.get("verification_scope"), str),
             f"{label}.verification_scope is required for v0.3 proof")
    required_ids: set[str] = set()
    required_kinds: dict[str, str] = {}
    required_targets: dict[str, dict[str, Any] | None] = {}
    for index, item in enumerate(value["required_proof"]):
        item_label = f"{label}.required_proof[{index}]"
        requirement = require_shape(
            item,
            {"requirement_id", "kind", "description", "acceptance_criteria", "oracle_requirement"},
            {"requirement_id", "kind", "custom_kind", "description", "acceptance_criteria", "oracle_requirement", "verification_target"},
            item_label,
        )
        requirement_id = requirement["requirement_id"]
        fail(isinstance(requirement_id, str) and REQUIREMENT_ID_RE.fullmatch(requirement_id) is not None,
             f"{item_label}.requirement_id is invalid")
        fail(requirement_id not in required_ids, f"{label} has duplicate requirement_id {requirement_id}")
        required_ids.add(requirement_id)
        fail(requirement["kind"] in PROOF_KINDS, f"{item_label}.kind is invalid")
        required_kinds[requirement_id] = requirement["kind"]
        if requirement["kind"] == "other":
            require_nonempty(requirement.get("custom_kind"), f"{item_label}.custom_kind")
        require_nonempty(requirement["description"], f"{item_label}.description")
        fail(isinstance(requirement["acceptance_criteria"], list)
             and requirement["acceptance_criteria"]
             and all(isinstance(item, str) and item.strip() for item in requirement["acceptance_criteria"]),
             f"{item_label}.acceptance_criteria must contain non-empty strings")
        require_nonempty(requirement["oracle_requirement"], f"{item_label}.oracle_requirement")
        target = requirement.get("verification_target")
        if is_v03:
            fail(isinstance(target, dict), f"{item_label}.verification_target is required for v0.3 proof")
        if target is not None:
            checked_target = require_shape(
                target, {"environment", "seam", "journey"},
                {"environment", "seam", "journey"}, f"{item_label}.verification_target",
            )
            for field in ("environment", "seam", "journey"):
                require_nonempty(checked_target[field], f"{item_label}.verification_target.{field}")
        required_targets[requirement_id] = copy.deepcopy(target)
    achieved_ids: set[str] = set()
    for index, item in enumerate(value["achieved_proof"]):
        item_label = f"{label}.achieved_proof[{index}]"
        achieved = require_shape(
            item,
            {"requirement_id", "kind", "result", "oracle", "evidence", "observed_by", "observed_at", "limitations"},
            {"requirement_id", "kind", "result", "oracle", "evidence", "observed_by", "observed_at", "limitations", "non_vacuity_check", "verification_target"},
            item_label,
        )
        requirement_id = achieved["requirement_id"]
        fail(requirement_id in required_ids and requirement_id not in achieved_ids,
             f"{item_label}.requirement_id is missing, unknown, or duplicated")
        achieved_ids.add(requirement_id)
        fail(achieved["kind"] == required_kinds[requirement_id],
             f"{item_label} proof kind differs from its requirement")
        target = achieved.get("verification_target")
        if is_v03:
            fail(isinstance(target, dict), f"{item_label}.verification_target is required for v0.3 proof")
        if required_targets[requirement_id] is not None:
            fail(target == required_targets[requirement_id],
                 f"{item_label} verification target does not match its required environment, seam, and journey")
        oracle = require_shape(achieved["oracle"], {"kind", "description"}, {"kind", "description"}, f"{item_label}.oracle")
        fail(oracle["kind"] in {"automated-independent", "human-independent", "external-system", "producer-check"},
             f"{item_label}.oracle.kind is invalid")
        require_nonempty(oracle["description"], f"{item_label}.oracle.description")
        fail(isinstance(achieved["evidence"], list), f"{item_label}.evidence must be an array")
        if achieved["result"] == "passed":
            fail(achieved["evidence"], f"{item_label}.evidence must be non-empty when passed")
        for ref_index, reference in enumerate(achieved["evidence"]):
            validate_record_ref(reference, f"{item_label}.evidence[{ref_index}]")
        if achieved["result"] == "passed":
            require_nonempty(achieved["non_vacuity_check"], f"{item_label}.non_vacuity_check")
        validate_actor(achieved["observed_by"], f"{item_label}.observed_by")
        parse_time(achieved["observed_at"], f"{item_label}.observed_at")
        fail(isinstance(achieved["limitations"], list)
             and all(isinstance(item, str) and item.strip() for item in achieved["limitations"]),
             f"{item_label}.limitations must contain strings")
    status = value["status"]
    if status == "passed":
        fail(value["applicability"] == "required" and required_ids,
             f"{label} passed proof must be required and contain requirements")
        fail(required_ids <= achieved_ids, f"{label} does not achieve every required proof")
        fail(all(item.get("result") == "passed" for item in value["achieved_proof"]),
             f"{label} passed proof contains a non-passing achieved result")
    elif status == "failed":
        fail(any(item.get("result") == "failed" for item in value["achieved_proof"]),
             f"{label} failed proof needs a failed achieved result")
    elif status == "blocked":
        fail(not value["achieved_proof"] or any(item.get("result") == "blocked" for item in value["achieved_proof"]),
             f"{label} blocked proof may contain only a blocked disposition")
    elif status == "not-applicable":
        fail(value["applicability"] == "not-applicable" and not required_ids and not achieved_ids,
             f"{label} not-applicable proof cannot contain proof requirements or results")
    parse_time(value["created_at"], f"{label}.created_at")
    parse_time(value["updated_at"], f"{label}.updated_at")


def validate_authorization_record(record: dict[str, Any], label: str) -> None:
    required = {
        "record_type", "schema_version", "authorization_id", "work_id", "action",
        "status", "scope", "requested_by", "authority", "requested_at", "grant",
    }
    allowed = required | {
        "next_action", "status_reason", "consumption", "decision_id", "delegation",
    }
    value = require_shape(record, required, allowed, label)
    fail(value["record_type"] == "workbench-authorization", f"{label}.record_type is invalid")
    fail(isinstance(value["schema_version"], str)
         and SEMANTIC_VERSION_RE.fullmatch(value["schema_version"]) is not None,
         f"{label}.schema_version is invalid")
    fail(isinstance(value["authorization_id"], str)
         and AUTHORIZATION_ID_RE.fullmatch(value["authorization_id"]) is not None,
         f"{label}.authorization_id is invalid")
    fail(isinstance(value["work_id"], str) and WORK_ID_RE.fullmatch(value["work_id"]) is not None,
         f"{label}.work_id is invalid")
    fail(value["action"] in AUTHORIZATION_ACTIONS, f"{label}.action is invalid")
    fail(value["status"] == "granted", f"{label} supplied to a gate must be granted")
    scope = require_shape(value["scope"], {"targets", "constraints"}, {"targets", "constraints", "environment"}, f"{label}.scope")
    fail(isinstance(scope["targets"], list) and scope["targets"], f"{label}.scope.targets must be non-empty")
    for index, item in enumerate(scope["targets"]):
        target = require_shape(
            item, {"kind", "target_id"},
            {"kind", "target_id", "qualifier", "planning_destination", "stage_id"},
            f"{label}.scope.targets[{index}]",
        )
        fail(target["kind"] in AUTHORIZATION_TARGET_KINDS,
             f"{label}.scope.targets[{index}].kind is invalid")
        require_nonempty(target["target_id"], f"{label}.scope.targets[{index}].target_id")
        if value["action"] == "closure":
            fail(target["kind"] == "work" and isinstance(target.get("planning_destination"), str),
                 f"{label} closure targets must name a work planning destination")
    fail(isinstance(scope["constraints"], list)
         and all(isinstance(item, str) and item.strip() for item in scope["constraints"]),
         f"{label}.scope.constraints must contain strings")
    validate_actor(value["requested_by"], f"{label}.requested_by")
    validate_actor(value["authority"], f"{label}.authority")
    parse_time(value["requested_at"], f"{label}.requested_at")
    grant = require_shape(value["grant"], {"granted_by", "granted_at"}, {"granted_by", "granted_at", "expires_at"}, f"{label}.grant")
    validate_actor(grant["granted_by"], f"{label}.grant.granted_by")
    parse_time(grant["granted_at"], f"{label}.grant.granted_at")
    if "expires_at" in grant:
        parse_time(grant["expires_at"], f"{label}.grant.expires_at")


def validate_record(record: dict[str, Any], label: str) -> None:
    record_type = record.get("record_type")
    fail(record_type in SCHEMA_BY_RECORD_TYPE,
         f"{label} has unsupported record_type {record_type!r}")
    validate_against_bundled_schema(record, SCHEMA_BY_RECORD_TYPE[record_type], label)
    if record_type == "workbench-proof":
        validate_proof_record(record, label)
    elif record_type == "workbench-authorization":
        validate_authorization_record(record, label)


def record_identity(record: dict[str, Any]) -> tuple[str, str, str]:
    mapping = {
        "workbench-artifact": ("artifact", "artifact_id"),
        "workbench-decision": ("decision", "decision_id"),
        "workbench-proof": ("proof", "proof_id"),
        "workbench-authorization": ("authorization", "authorization_id"),
        "workbench-handoff": ("handoff", "handoff_id"),
    }
    record_type = record.get("record_type")
    fail(record_type in mapping, f"record type cannot be registered: {record_type!r}")
    reference_type, id_field = mapping[record_type]
    record_id = record.get(id_field)
    fail(isinstance(record_id, str) and record_id, f"{record_type} has no {id_field}")
    return reference_type, id_field, record_id


def record_reference(record: dict[str, Any]) -> dict[str, str]:
    reference_type, _, record_id = record_identity(record)
    return {"record_type": reference_type, "record_id": record_id}


def validated_workspace_artifact(store: "Store", record: dict[str, Any]) -> None:
    if record.get("record_type") != "workbench-artifact" or record.get("status") not in {"current", "superseded"}:
        return
    location = record.get("location") or {}
    integrity = record.get("content_integrity") or {}
    fail(integrity.get("algorithm") == "sha256", "artifact content integrity must use sha256")
    if location.get("kind") == "workspace-path":
        raw = Path(location.get("value", ""))
        fail(not raw.is_absolute(), "workspace artifact location must be repository-relative")
        path = (store.repo / raw).resolve()
        fail(path == store.repo or store.repo in path.parents,
             f"artifact location escapes repository: {raw}")
        fail(path.is_file(), f"registered artifact does not exist: {raw.as_posix()}")
        fail(file_digest(path) == integrity.get("value"),
             f"artifact content digest does not match: {raw.as_posix()}")
    elif location.get("kind") == "embedded":
        expected = hashlib.sha256(str(location.get("value", "")).encode("utf-8")).hexdigest()
        fail(expected == integrity.get("value"), "embedded artifact content digest does not match")
    else:
        fail(False, "v0.3 can register current artifacts only when workspace-path or embedded content is locally verifiable")


def read_events(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise WorkbenchError(f"cannot read {path}: {exc}") from exc
    events = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise WorkbenchError(f"invalid event JSON at line {number}: {exc}") from exc
        fail(isinstance(event, dict), f"event line {number} is not an object")
        events.append(event)
    fail(events, "event journal is empty")
    return events


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def encode_events(events: list[dict[str, Any]]) -> bytes:
    return b"".join(canonical(event) + b"\n" for event in events)


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Store:
    def __init__(self, repo: Path):
        self.repo = repo.resolve()
        self.root = self.repo / ".workbench"
        self.work_root = self.root / "work"
        self.lock_path = self.root / ".lock"
        self.journal_path = self.root / ".transaction.json"

    def work_dir(self, work_id: str) -> Path:
        fail(WORK_ID_RE.fullmatch(work_id) is not None, "work_id must match WB-<readable-token>")
        folder = (self.work_root / work_id).resolve()
        work_root = self.work_root.resolve()
        fail(work_root in folder.parents, f"work_id escapes Workbench work root: {work_id}")
        return folder

    @contextlib.contextmanager
    def locked(self) -> Iterator[None]:
        self.root.mkdir(parents=True, exist_ok=True)
        lock_file = self.lock_path.open("a+b")
        try:
            if os.name == "nt":
                lock_file.seek(0, os.SEEK_END)
                if lock_file.tell() == 0:
                    lock_file.write(b"\0")
                    lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            lock_file.close()
            raise WorkbenchError(f"Workbench is locked: {self.lock_path}") from exc
        try:
            self.recover()
            yield
        finally:
            try:
                if os.name == "nt":
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            finally:
                lock_file.close()

    def recover(self) -> None:
        if not self.journal_path.exists():
            return
        journal = load_json(self.journal_path)
        require_shape(journal, {"version", "transaction_id", "files"},
                      {"version", "transaction_id", "files"}, "transaction journal")
        fail(journal["version"] == 1, "unknown transaction journal version")
        transaction_id = journal.get("transaction_id")
        fail(isinstance(transaction_id, str) and re.fullmatch(r"[0-9a-f]{32}", transaction_id) is not None,
             "invalid transaction journal ID")
        entries = journal.get("files")
        fail(isinstance(entries, list) and entries, "transaction journal has no file entries")
        plan: list[tuple[str, Path, Path]] = []
        targets: set[Path] = set()
        temporaries: set[Path] = set()
        for index, entry in enumerate(entries):
            require_shape(
                entry,
                {"target", "temporary", "before_sha256", "after_sha256"},
                {"target", "temporary", "before_sha256", "after_sha256"},
                f"transaction journal entry {index}",
            )
            fail(isinstance(entry.get("target"), str) and isinstance(entry.get("temporary"), str), "invalid transaction paths")
            target = (self.root / entry["target"]).resolve()
            temporary = (self.root / entry["temporary"]).resolve()
            fail(self.root in target.parents, f"journal target escapes Workbench root: {target}")
            fail(self.root in temporary.parents, f"journal temporary escapes Workbench root: {temporary}")
            fail(target != temporary, "journal target and temporary path are identical")
            fail(target.parent == temporary.parent
                 and temporary.name == f".{target.name}.{transaction_id}.tmp",
                 "journal temporary path does not match its target and transaction")
            expected = entry.get("after_sha256")
            before = entry.get("before_sha256")
            fail(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                 "invalid transaction after digest")
            fail(before is None or isinstance(before, str) and re.fullmatch(r"[0-9a-f]{64}", before) is not None,
                 "invalid transaction before digest")
            fail(target not in targets, f"transaction journal repeats target: {target}")
            fail(temporary not in temporaries, f"transaction journal repeats temporary: {temporary}")
            targets.add(target)
            temporaries.add(temporary)
            current = file_digest(target)
            if current == expected:
                temporary_digest = file_digest(temporary)
                fail(temporary_digest in {None, expected},
                     f"settled transaction has a conflicting temporary: {temporary}")
                plan.append(("settled", target, temporary))
            else:
                fail(current == before, f"transaction target changed outside recovery: {target}")
                fail(file_digest(temporary) == expected, f"cannot recover transaction target {target}")
                plan.append(("replace", target, temporary))
        fail(targets.isdisjoint(temporaries),
             "transaction journal reuses a path as both target and temporary")
        for action, target, temporary in plan:
            if action == "replace":
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporary, target)
            else:
                with contextlib.suppress(FileNotFoundError):
                    temporary.unlink()
        self.journal_path.unlink()

    def transaction(self, writes: dict[Path, bytes]) -> None:
        transaction_id = uuid.uuid4().hex
        entries = []
        for target, content in sorted(writes.items(), key=lambda item: str(item[0])):
            target = target.resolve()
            fail(target == self.root or self.root in target.parents, f"write escapes Workbench root: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.{transaction_id}.tmp")
            with temporary.open("wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            entries.append({
                "target": target.relative_to(self.root).as_posix(),
                "temporary": temporary.relative_to(self.root).as_posix(),
                "before_sha256": file_digest(target),
                "after_sha256": hashlib.sha256(content).hexdigest(),
            })
        journal = {"version": 1, "transaction_id": transaction_id, "files": entries}
        journal_tmp = self.journal_path.with_suffix(f".{transaction_id}.tmp")
        journal_tmp.write_bytes(encode_json(journal))
        os.replace(journal_tmp, self.journal_path)
        self.recover()


def lifecycle() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    data = load_json(LIFECYCLE_PATH)
    registry = data.get("x-workbench", {})
    routes = {item["id"]: item for item in registry.get("routes", [])}
    stages = {item["id"]: item for item in registry.get("stages", [])}
    destinations = {item["id"]: item for item in registry.get("destinations", [])}
    phases = registry.get("phases", [])
    fail(routes and stages and destinations and phases, "bundled lifecycle registry is incomplete")
    return routes, stages, destinations, phases


def pointer_parts(pointer: str) -> list[str]:
    fail(pointer.startswith("/"), f"illegal JSON pointer: {pointer}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def get_pointer(document: Any, pointer: str) -> tuple[bool, Any]:
    if pointer == "/document":
        return (document is not None, copy.deepcopy(document))
    current = document
    for part in pointer_parts(pointer):
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return False, None
            if index < 0 or index >= len(current):
                return False, None
            current = current[index]
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False, None
    return True, copy.deepcopy(current)


def set_pointer(document: Any, pointer: str, after: dict[str, Any]) -> Any:
    if pointer == "/document":
        return copy.deepcopy(after["value"]) if after["present"] else None
    parts = pointer_parts(pointer)
    current = document
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    leaf = parts[-1]
    if isinstance(current, list):
        index = int(leaf)
        fail(0 <= index < len(current), f"list pointer is out of range: {pointer}")
        if after["present"]:
            current[index] = copy.deepcopy(after["value"])
        else:
            current.pop(index)
    elif after["present"]:
        current[leaf] = copy.deepcopy(after["value"])
    else:
        current.pop(leaf, None)
    return document


def target_kind(change: dict[str, Any]) -> str:
    record_type = change.get("target", {}).get("record_type")
    return {"work": "work", "map": "map"}.get(record_type, "")


def allowed_pointer(pointer: str, prefixes: tuple[str, ...]) -> bool:
    return any(
        pointer == prefix or prefix.endswith("/") and pointer.startswith(prefix)
        for prefix in prefixes
    )


def replay_events(events: list[dict[str, Any]], expected_work_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    state: dict[str, Any] | None = None
    map_record: dict[str, Any] | None = None
    previous_revision = 0
    keys: dict[str, str] = {}
    for expected_sequence, event in enumerate(events, 1):
        validate_record(event, f"event {expected_sequence}")
        fail(event.get("sequence") == expected_sequence, f"event sequence discontinuity at {expected_sequence}")
        fail(event.get("work_id") == expected_work_id, f"event {expected_sequence} has wrong work_id")
        fail(event.get("state_revision_before") == previous_revision, f"event {expected_sequence} has wrong before revision")
        fail(event.get("state_revision_after") == previous_revision + 1, f"event {expected_sequence} revision is not +1")
        current_event_id = event.get("event_id")
        fail(current_event_id == event_id(expected_work_id, expected_sequence),
             f"event {expected_sequence} has invalid event_id")
        key = event.get("idempotency_key")
        fingerprint = (event.get("input_fingerprint") or {}).get("value")
        fail(isinstance(key, str) and key, f"event {expected_sequence} lacks idempotency key")
        fail(isinstance(fingerprint, str) and len(fingerprint) == 64, f"event {expected_sequence} has invalid fingerprint")
        if key in keys:
            fail(keys[key] == fingerprint, f"idempotency key conflict in journal: {key}")
            raise WorkbenchError(f"duplicate idempotency key in journal: {key}")
        keys[key] = fingerprint
        fp_input = (event.get("payload") or {}).get("fingerprint_input")
        fail(fp_input is not None and digest(fp_input) == fingerprint, f"event {expected_sequence} fingerprint does not match payload")
        event_type = event.get("event_type")
        fail(event_type in LEGAL_CHANGE_PREFIXES, f"unsupported replay event type: {event_type}")
        payload = event.get("payload")
        expected_payload = {"fingerprint_input": fp_input}
        if event_type == "stage-completed":
            expected_payload["gate_receipt"] = fp_input.get("gate_receipt")
        fail(payload == expected_payload,
             f"event {expected_sequence} payload is noncanonical or contradicts its fingerprinted input")
        expected_command = {
            "work-started": "start",
            "stage-completed": "advance-stage",
            "handoff-accepted": "accept-handoff",
        }.get(event_type)
        fail(expected_command is not None, f"unsupported replay event type: {event_type}")
        fail(fp_input.get("command") == expected_command,
             f"event {expected_sequence} command does not match event type")
        fail((expected_sequence == 1) == (event_type == "work-started"),
             "work-started must be the first and only initial event")
        expected_actor_id = fp_input.get("owner") if event_type == "work-started" else fp_input.get("actor")
        fail(isinstance(expected_actor_id, str) and event.get("actor") == actor(expected_actor_id),
             f"event {expected_sequence} actor does not match its fingerprinted input")
        expected_outputs = [{"record_type": "work", "record_id": expected_work_id}]
        if event_type == "handoff-accepted":
            expected_outputs.extend(copy.deepcopy(fp_input.get("record_refs", [])))
        fail(event.get("outputs") == expected_outputs,
             f"event {expected_sequence} has noncanonical outputs")
        expected_inputs = copy.deepcopy(fp_input.get("inputs_used", [])) if event_type == "handoff-accepted" else []
        if event_type == "work-started":
            for field in ("intake_reference", "routing_reference"):
                reference = fp_input.get(field)
                if isinstance(reference, dict):
                    expected_inputs.append(reference)
        fail(event.get("inputs") == expected_inputs,
             f"event {expected_sequence} has noncanonical input provenance")
        expected_description = {
            "work-started": "Start Workbench work item.",
            "stage-completed": f"Complete stage {(fp_input.get('gate_receipt') or {}).get('stage_id')}.",
            "handoff-accepted": f"Accept specialist handoff {fp_input.get('handoff_id')}.",
        }[event_type]
        expected_cause_kind = "specialist-output" if event_type == "handoff-accepted" else "user-request"
        fail(event.get("cause") == {
            "kind": expected_cause_kind, "description": expected_description,
            "references": expected_inputs,
        }, f"event {expected_sequence} has noncanonical cause metadata")
        changes = event.get("changes")
        fail(isinstance(changes, list) and changes, f"event {expected_sequence} has no changes")
        for change in changes:
            kind = target_kind(change)
            fail(kind in {"work", "map"}, f"event {expected_sequence} targets a noncanonical record")
            target_id = (change.get("target") or {}).get("record_id")
            expected_target_id = expected_work_id if kind == "work" else f"MAP-{expected_work_id.removeprefix('WB-')}"
            fail(target_id == expected_target_id,
                 f"event {expected_sequence} targets wrong {kind} record ID: {target_id!r}")
            pointer = change.get("path", "")
            prefixes = LEGAL_CHANGE_PREFIXES[event_type].get(kind, ())
            fail(allowed_pointer(pointer, prefixes), f"illegal {event_type} target path: {kind}{pointer}")
            target = state if kind == "work" else map_record
            before = change.get("before")
            after = change.get("after")
            fail(isinstance(before, dict) and isinstance(before.get("present"), bool), "invalid before value state")
            fail(isinstance(after, dict) and isinstance(after.get("present"), bool), "invalid after value state")
            try:
                present, value = get_pointer(target, pointer)
            except (IndexError, KeyError, TypeError, ValueError) as exc:
                raise WorkbenchError(
                    f"event {expected_sequence} cannot read {kind}{pointer}: {exc}"
                ) from exc
            fail(present == before["present"], f"before-presence mismatch at {kind}{pointer}")
            if present:
                fail(value == before.get("value"), f"before-value mismatch at {kind}{pointer}")
            try:
                updated = set_pointer(target, pointer, after)
            except (IndexError, KeyError, TypeError, ValueError) as exc:
                raise WorkbenchError(
                    f"event {expected_sequence} cannot apply {kind}{pointer}: {exc}"
                ) from exc
            if kind == "work":
                state = updated
            else:
                map_record = updated
        previous_revision += 1
        fail(state is not None and state.get("state_revision") == previous_revision, f"event {expected_sequence} did not establish matching state revision")
        fail(state.get("latest_event_id") == current_event_id, f"event {expected_sequence} did not establish latest_event_id")
    fail(state is not None and map_record is not None, "journal did not reconstruct state and map")
    validate_record(state, "replayed state")
    validate_record(map_record, "replayed map")
    return state, map_record


def checked_checkpoint(store: Store, work_id: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    folder = store.work_dir(work_id)
    events = read_events(folder / "events.jsonl")
    state, map_record = replay_events(events, work_id)
    start_input = (events[0].get("payload") or {}).get("fingerprint_input") or {}
    if "intake_reference" in start_input or "intake_sha256" in start_input:
        expected_reference = intake_reference(work_id)
        fail(start_input.get("intake_reference") == expected_reference,
             "start event has noncanonical captured-intake provenance")
        intake_path = folder / "intake.json"
        fail(intake_path.is_file(), "start event references a missing captured intake")
        validate_intake(load_json(intake_path))
        fail(file_digest(intake_path) == start_input.get("intake_sha256"),
             "captured intake changed after the work item was started")
    if "routing_reference" in start_input or "routing_sha256" in start_input:
        fail("intake_reference" in start_input and "intake_sha256" in start_input,
             "routing-bound start is missing captured-intake provenance")
        intake = load_json(folder / "intake.json")
        routing, routing_path, history = current_routing(store, work_id, intake)
        revision = routing_revision(routing)
        fail(start_input.get("routing_reference") == routing_reference(work_id, revision),
             "start event has noncanonical routing-receipt provenance")
        fail(file_digest(routing_path) == start_input.get("routing_sha256"),
             "routing receipt changed after the work item was started")
        fail((routing.get("intake") or {}).get("sha256", {}).get("value")
             == start_input.get("intake_sha256"),
             "routing receipt is not bound to the start event's captured intake")
        expected_route = "profile-compiled" if routing.get("compiled_plan") is not None else routing.get("runtime_route")
        fail(expected_route == start_input.get("route"),
             "routing receipt runtime route differs from the start event")
        fail(routing.get("planning_destination") == start_input.get("destination"),
             "routing receipt destination differs from the start event")
        fail(routing.get("title") == start_input.get("title"),
             "routing receipt title differs from the start event")
        fail(routing.get("desired_outcome") == start_input.get("desired_outcome"),
             "routing receipt desired outcome differs from the start event")
        fail(routing_is_ready(routing),
             "routing receipt is no longer ready for lifecycle execution")
        fail(len(history) == revision,
             "routing history does not end at the receipt bound to lifecycle start")
    elif (folder / "routing.json").exists():
        fail(False, "unbound routing receipt exists beside the routed checkpoint")
    fail(load_json(folder / "state.json") == state, "state snapshot is stale or corrupt relative to replay")
    fail(load_json(folder / "map.json") == map_record, "map snapshot is stale or corrupt relative to replay")
    accepted_digests: dict[str, str] = {}
    for event in events:
        fp_input = ((event.get("payload") or {}).get("fingerprint_input") or {})
        event_records: dict[str, str] = {}
        if event.get("event_type") == "handoff-accepted":
            handoff_id = fp_input.get("handoff_id")
            handoff_digest = fp_input.get("handoff_sha256")
            if isinstance(handoff_id, str) and isinstance(handoff_digest, str):
                event_records[handoff_id] = handoff_digest
            event_records.update(fp_input.get("record_digests") or {})
        elif event.get("event_type") == "stage-completed":
            receipt = fp_input.get("gate_receipt") or {}
            for record in [
                *(receipt.get("proof_records") or []),
                *(receipt.get("authorization_records") or []),
            ]:
                if isinstance(record, dict):
                    _, _, record_id = record_identity(record)
                    event_records[record_id] = digest(record)
        for record_id, expected_digest in event_records.items():
            fail(isinstance(record_id, str) and isinstance(expected_digest, str),
                 "event contains an invalid accepted-record digest")
            fail(record_id not in accepted_digests
                 or accepted_digests[record_id] == expected_digest,
                 f"record {record_id} was accepted with conflicting digests")
            accepted_digests[record_id] = expected_digest
    is_v03_state = tuple(
        int(part) for part in state["schema_version"].split("-")[0].split(".")[:3]
    ) >= (0, 3, 0)
    for field, record_type, id_field in (
        ("artifact_ids", "workbench-artifact", "artifact_id"),
        ("decision_ids", "workbench-decision", "decision_id"),
        ("proof_ids", "workbench-proof", "proof_id"),
        ("authorization_ids", "workbench-authorization", "authorization_id"),
        ("handoff_ids", "workbench-handoff", "handoff_id"),
    ):
        for record_id in state.get(field, []):
            record_path = folder / "records" / f"{record_id}.json"
            fail(record_path.is_file(), f"state references missing record: {record_id}")
            record = load_json(record_path)
            validate_record(record, f"record {record_id}")
            fail(record.get("record_type") == record_type, f"record {record_id} has wrong type")
            fail(record.get(id_field) == record_id, f"record filename/ID mismatch: {record_id}")
            fail(record.get("work_id") == work_id, f"record {record_id} has wrong work_id")
            if is_v03_state:
                fail(record_id in accepted_digests,
                     f"v0.3 record has no immutable acceptance digest: {record_id}")
            if record_id in accepted_digests:
                fail(digest(record) == accepted_digests[record_id],
                     f"record changed after acceptance: {record_id}")
            validated_workspace_artifact(store, record)
    return state, map_record, events


def value_state(present: bool, value: Any = None) -> dict[str, Any]:
    result = {"present": present}
    if present:
        result["value"] = copy.deepcopy(value)
    return result


def change(kind: str, record_id: str, pointer: str, before: tuple[bool, Any], after: tuple[bool, Any]) -> dict[str, Any]:
    return {
        "target": {"record_type": kind, "record_id": record_id},
        "path": pointer,
        "before": value_state(*before),
        "after": value_state(*after),
    }


def event_id(work_id: str, sequence: int) -> str:
    token = work_id.removeprefix("WB-")
    return f"EVT-{token[:57]}-{sequence:06d}"


def actor(actor_id: str) -> dict[str, str]:
    return {"actor_id": actor_id, "kind": "human" if actor_id.startswith(("user:", "human:")) else "agent"}


def make_event(work_id: str, sequence: int, event_type: str, actor_id: str, key: str,
               fp_input: dict[str, Any], changes: list[dict[str, Any]], description: str,
               receipt: dict[str, Any] | None = None,
               inputs: list[dict[str, Any]] | None = None,
               outputs: list[dict[str, Any]] | None = None,
               cause_kind: str = "user-request") -> dict[str, Any]:
    payload: dict[str, Any] = {"fingerprint_input": fp_input}
    if receipt is not None:
        payload["gate_receipt"] = receipt
    references = copy.deepcopy(inputs) if inputs is not None else []
    if inputs is None:
        for field in ("intake_reference", "routing_reference"):
            reference = fp_input.get(field)
            if isinstance(reference, dict):
                references.append(copy.deepcopy(reference))
    return {
        "record_type": "workbench-event", "schema_version": "0.1.0",
        "event_id": event_id(work_id, sequence), "work_id": work_id,
        "sequence": sequence, "event_type": event_type, "occurred_at": now(),
        "actor": actor(actor_id),
        "cause": {"kind": cause_kind, "description": description, "references": references},
        "inputs": copy.deepcopy(references), "outputs": copy.deepcopy(outputs) if outputs is not None else [{"record_type": "work", "record_id": work_id}],
        "state_revision_before": sequence - 1, "state_revision_after": sequence,
        "idempotency_key": key,
        "input_fingerprint": {"algorithm": "sha256", "value": digest(fp_input)},
        "changes": changes, "payload": payload,
    }


def active_work(store: Store, explicit: str | None) -> str:
    if explicit:
        return explicit
    data = load_json(store.root / "active-work.json")
    work_id = data.get("work_id")
    fail(isinstance(work_id, str), "active-work.json has no work_id")
    return work_id


def intake_next_action(work_id: str) -> dict[str, Any]:
    return {
        "description": "Inspect the repository and accessible references, synthesize what is known, then ask only for material decisions that cannot be determined.",
        "owner": {"actor_id": "agent:workbench", "kind": "agent"},
        "target_type": "evidence",
        "target_id": f"INTAKE-{work_id}",
    }


def intake_fingerprint_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in record.items() if key != "input_fingerprint"}


def validate_intake(record: dict[str, Any], label: str = "captured intake") -> None:
    validate_record(record, label)
    fail(record.get("owner") == actor(record.get("owner", {}).get("actor_id", "")),
         f"{label} owner kind is not canonical")
    fail(record.get("next_action") == intake_next_action(record.get("work_id", "")),
         f"{label} next_action is not canonical")
    expected = digest(intake_fingerprint_payload(record))
    actual = (record.get("input_fingerprint") or {}).get("value")
    fail(actual == expected, f"{label} input fingerprint does not match its immutable content")


def intake_reference(work_id: str) -> dict[str, str]:
    return {"record_type": "external", "record_id": f"INTAKE-{work_id}", "uri": "intake.json"}


def intake_summary(record: dict[str, Any]) -> dict[str, Any]:
    next_action = copy.deepcopy(record["next_action"])
    return {
        "runtime_version": RUNTIME_VERSION,
        "work_id": record["work_id"],
        "status": "intake-draft",
        "route": "undetermined",
        "planning_destination": "undetermined",
        "current_stage": "intake",
        "current_stage_status": "draft",
        "state_revision": 0,
        "next_action": next_action,
        "source_references": copy.deepcopy(record["source_references"]),
        "human_control": {
            "where": {"route": "undetermined", "stage": "intake", "status": "intake-draft"},
            "learned": [],
            "decisions": [],
            "why_next": next_action["description"],
            "uncertainties": [{
                "id": "intake-route-outcome",
                "description": "The outcome, route, destination, constraints, and authorization boundary have not yet been synthesized.",
                "status": "unresolved",
            }],
        },
        "frontier": {
            "agent_ready": [{
                "node_id": next_action["target_id"],
                "title": next_action["description"],
                "status": "ready",
            }],
            "user_decisions": [],
            "external_blockers": [],
        },
        "projection_boundary": "captured intake only; route, destination, scope, and authorization remain uncommitted",
    }


def capture_intake(args: argparse.Namespace, store: Store) -> dict[str, Any]:
    fail(WORK_ID_RE.fullmatch(args.work_id) is not None, "work_id must match WB-<readable-token>")
    fail(isinstance(args.request, str) and args.request.strip(), "request must contain non-whitespace text")
    references = list(args.reference or [])
    fail(len(references) == len(set(references)), "source references must be unique")
    timestamp = now()
    record: dict[str, Any] = {
        "record_type": "workbench-intake",
        "schema_version": "0.1.0",
        "work_id": args.work_id,
        "status": "captured",
        "raw_request": args.request,
        "source_references": references,
        "route": None,
        "planning_destination": None,
        "owner": actor(args.owner),
        "next_action": intake_next_action(args.work_id),
        "idempotency_key": args.idempotency_key,
        "created_at": timestamp,
    }
    record["input_fingerprint"] = {
        "algorithm": "sha256",
        "value": digest(intake_fingerprint_payload(record)),
    }
    validate_intake(record, "new captured intake")
    with store.locked():
        folder = store.work_dir(args.work_id)
        path = folder / "intake.json"
        if path.exists():
            existing = load_json(path)
            validate_intake(existing)
            same_key = existing.get("idempotency_key") == args.idempotency_key
            same_input = all(existing.get(field) == record.get(field) for field in (
                "work_id", "raw_request", "source_references", "owner"
            ))
            fail(same_key and same_input,
                 f"captured intake already exists with different input or idempotency key: {args.work_id}")
            return {"result": "idempotent", **intake_summary(existing)}
        fail(not (folder / "events.jsonl").exists(),
             f"work already started without a captured intake: {args.work_id}")
        fail(not folder.exists(),
             f"work directory exists without a valid intake or event journal; recovery is required: {folder}")
        store.transaction({
            path: encode_json(record),
            store.root / "active-work.json": encode_json({"work_id": args.work_id}),
        })
        return {"result": "captured", **intake_summary(record)}


def routing_revision(record: dict[str, Any]) -> int:
    """Return the explicit revision, treating pre-v0.4 receipts as revision one."""

    value = record.get("routing_revision", 1)
    fail(isinstance(value, int) and not isinstance(value, bool) and value >= 1,
         "routing receipt has an invalid routing_revision")
    return value


def routing_id(work_id: str, revision: int = 1) -> str:
    token = work_id.removeprefix("WB-")
    if revision == 1:
        return f"RTR-{token}"
    suffix = f"-R{revision:06d}"
    return f"RTR-{token[:64 - len(suffix)]}{suffix}"


def routing_relative_path(revision: int) -> str:
    return "routing.json" if revision == 1 else f"routing-revisions/{revision:06d}.json"


def routing_reference(work_id: str, revision: int = 1) -> dict[str, str]:
    return {
        "record_type": "external",
        "record_id": routing_id(work_id, revision),
        "uri": routing_relative_path(revision),
    }


def routing_fingerprint_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in record.items()
        if key not in {"created_at", "input_fingerprint"}
    }


def compile_stage_plan(record: dict[str, Any], phases: list[dict[str, Any]],
                       destinations: dict[str, Any], *,
                       compiler_version: str = RUNTIME_VERSION) -> dict[str, Any] | None:
    """Compile domain activities into one operational checkpoint per applicable phase."""

    if (record.get("solution_context") == "undetermined"
            or record.get("unresolved_questions")
            or any(item.get("applicability") == "undetermined"
                   for item in record.get("stage_recommendations", []))):
        return None
    destination_id = record.get("planning_destination")
    fail(destination_id in destinations, f"unknown planning destination: {destination_id}")
    destination_stage = destinations[destination_id]["completion_stage"]
    ordered_activities = [stage_id for phase in phases for stage_id in phase["activities"]]
    fail(destination_stage in ordered_activities,
         f"destination stage is absent from phase registry: {destination_stage}")
    cutoff = ordered_activities.index(destination_stage)
    in_scope = set(ordered_activities[:cutoff + 1])

    context = record.get("solution_context")
    basis = record.get("business_basis")
    lane = record.get("execution_lane")
    intent = record.get("engagement_intent")
    destination_index = ordered_activities.index(destination_stage)
    required: set[str] = {"intake", "outcome-framing", destination_stage}
    if context == "brownfield" and destination_index >= ordered_activities.index("implementation"):
        required.add("brownfield-reconnaissance")
    if context == "greenfield" and destination_index >= ordered_activities.index("specification"):
        required.update({"solution-architecture", "specification", "delivery-planning"})
    if context == "process-only" or basis in {"hypothesis", "operating-process"}:
        required.update({"evidence-intake", "process-model"})
    if basis == "hypothesis":
        required.add("process-validation")
    if destination_id == "proposal":
        required.add("proposal")
    if destination_id in {"implementation-plan"}:
        required.update({"specification", "delivery-planning"})
    if context in {"brownfield", "greenfield"} and destination_id in {
        "locally-verified-implementation", "released-software", "business-outcome",
    }:
        required.update({"implementation", "local-verification"})
    if context in {"brownfield", "greenfield"} and destination_id in {"released-software", "business-outcome"}:
        required.update({"release", "deployed-verification"})
    if destination_id == "business-outcome":
        required.add("outcome-verification")
    if intent in {"implement", "release"}:
        required.add("standards-resolution")
    if lane == "full" and context in {"brownfield", "greenfield"} and destination_index >= ordered_activities.index("implementation"):
        required.update({"solution-architecture", "specification", "delivery-planning"})

    recommendations = {
        item["stage_id"]: item for item in record.get("stage_recommendations", [])
    }
    compiled_phases: list[dict[str, Any]] = []
    for phase in phases:
        activities: list[dict[str, Any]] = []
        applicable_ids: list[str] = []
        for stage_id in phase["activities"]:
            if stage_id not in in_scope:
                continue
            recommendation = recommendations.get(stage_id)
            recommended = recommendation.get("applicability") if recommendation else None
            if stage_id in required:
                fail(recommended != "not-applicable",
                     f"stage recommendation cannot skip required activity {stage_id}")
                applicability = "applicable"
                reason = (recommendation or {}).get("reason") or "Required by the routing profile or selected destination."
            elif recommended == "applicable":
                applicability = "applicable"
                reason = recommendation["reason"]
            else:
                applicability = "not-applicable"
                reason = ((recommendation or {}).get("reason")
                          or "No profile fact or explicit recommendation makes this activity necessary.")
            activities.append({
                "stage_id": stage_id,
                "applicability": applicability,
                "reason": reason,
            })
            if applicability == "applicable":
                applicable_ids.append(stage_id)
        if applicable_ids:
            compiled_phases.append({
                "phase_id": phase["id"],
                "checkpoint_stage": applicable_ids[-1],
                "activities": activities,
            })
    fail(compiled_phases and compiled_phases[-1]["checkpoint_stage"] == destination_stage,
         "compiled plan does not end at the selected destination")
    return {
        "compiler_version": compiler_version,
        "destination_stage": destination_stage,
        "phases": compiled_phases,
    }


def validate_routing(record: dict[str, Any], intake: dict[str, Any] | None = None,
                     label: str = "routing receipt", intake_sha256: str | None = None) -> None:
    validate_record(record, label)
    work_id = record.get("work_id", "")
    revision = routing_revision(record)
    fail(record.get("routing_id") == routing_id(work_id, revision),
         f"{label} routing_id is not canonical")
    schema_version = tuple(int(part) for part in record["schema_version"].split("-")[0].split(".")[:3])
    if schema_version >= (0, 4, 0):
        fail("routing_revision" in record,
             f"{label} must declare routing_revision")
    if revision == 1:
        fail(not any(field in record for field in (*ROUTING_REVISION_FIELDS, "supersedes")),
             f"{label} revision one cannot contain supersession fields")
    else:
        fail(all(field in record for field in (*ROUTING_REVISION_FIELDS, "supersedes")),
             f"{label} revision {revision} is missing supersession fields")
        resolutions = record.get("resolved_questions", [])
        questions = [item.get("question") for item in resolutions]
        fail(len(questions) == len(set(questions)),
             f"{label} resolves the same question more than once")
    fail(record.get("owner") == actor(record.get("owner", {}).get("actor_id", "")),
         f"{label} owner kind is not canonical")
    expected_intake_reference = intake_reference(work_id)
    fail((record.get("intake") or {}).get("reference") == expected_intake_reference,
         f"{label} has noncanonical captured-intake reference")
    expected_fingerprint = digest(routing_fingerprint_payload(record))
    fail((record.get("input_fingerprint") or {}).get("value") == expected_fingerprint,
         f"{label} input fingerprint does not match its immutable content")

    recommendations = record.get("stage_recommendations", [])
    stage_ids = [item.get("stage_id") for item in recommendations]
    fail(len(stage_ids) == len(set(stage_ids)),
         f"{label} contains duplicate stage recommendations")

    boundary = record.get("authorization_boundary") or {}
    granted = set(boundary.get("granted_actions", []))
    withheld = set(boundary.get("withheld_actions", []))
    fail(granted.isdisjoint(withheld),
         f"{label} grants and withholds the same action")
    fail(not withheld or granted | withheld == AUTHORIZATION_ACTIONS,
         f"{label} authorization boundary must classify every capability action when withheld_actions is present")

    context = record.get("solution_context")
    basis = record.get("business_basis")
    lane = record.get("execution_lane")
    runtime_route = record.get("runtime_route")
    expected_route: str | None = None
    if context == "brownfield":
        expected_route = "small-change-fast-lane" if lane == "fast" else "brownfield-feature"
    elif context == "greenfield":
        expected_route = None
    elif context == "process-only":
        expected_route = "unproven-process" if basis == "hypothesis" else "existing-process"
    if runtime_route is not None:
        fail(runtime_route == expected_route,
             f"{label} runtime_route {runtime_route!r} does not match its routing profile; expected {expected_route!r}")
    if context == "greenfield":
        fail(runtime_route is None,
             f"{label} cannot force a greenfield profile into a legacy runtime route")

    if schema_version >= (0, 3, 0):
        _, _, destinations, phases = lifecycle()
        recorded_plan = record.get("compiled_plan")
        compiler_version = (
            recorded_plan.get("compiler_version", RUNTIME_VERSION)
            if isinstance(recorded_plan, dict) else RUNTIME_VERSION
        )
        expected_plan = compile_stage_plan(
            record, phases, destinations, compiler_version=compiler_version
        )
        fail(record.get("compiled_plan") == expected_plan,
             f"{label} compiled plan does not match its routing profile and stage recommendations")

    if intake is not None:
        validate_intake(intake)
        fail(intake.get("work_id") == work_id, f"{label} work_id does not match captured intake")
        if intake_sha256 is not None:
            fail((record.get("intake") or {}).get("sha256", {}).get("value") == intake_sha256,
                 f"{label} is not bound to the current captured-intake bytes")


def validate_routing_transition(previous: dict[str, Any], current: dict[str, Any],
                                previous_path: Path) -> None:
    previous_revision = routing_revision(previous)
    current_revision = routing_revision(current)
    fail(current_revision == previous_revision + 1,
         f"routing revision {current_revision} does not immediately follow {previous_revision}")
    expected_supersedes = {
        "reference": routing_reference(previous["work_id"], previous_revision),
        "sha256": {"algorithm": "sha256", "value": file_digest(previous_path)},
    }
    fail(current.get("supersedes") == expected_supersedes,
         f"routing revision {current_revision} does not bind the exact preceding receipt")

    previous_questions = {
        item["question"] for item in previous.get("unresolved_questions", [])
    }
    current_questions = {
        item["question"] for item in current.get("unresolved_questions", [])
    }
    resolved_questions = {
        item["question"] for item in current.get("resolved_questions", [])
    }
    removed_questions = previous_questions - current_questions
    fail(resolved_questions == removed_questions,
         "routing revision must record an answer for every removed unresolved question, and only those questions")


def routing_history(store: Store, work_id: str,
                    intake: dict[str, Any] | None = None) -> list[tuple[dict[str, Any], Path]]:
    folder = store.work_dir(work_id)
    intake_path = folder / "intake.json"
    first_path = folder / "routing.json"
    revisions_dir = folder / "routing-revisions"
    if not first_path.is_file():
        fail(not revisions_dir.exists(),
             f"routing revision history exists without routing.json: {revisions_dir}")
        return []
    if intake is None:
        fail(intake_path.is_file(), f"routing history is missing captured intake: {work_id}")
        intake = load_json(intake_path)
    intake_digest = file_digest(intake_path)

    paths = [first_path]
    if revisions_dir.exists():
        fail(revisions_dir.is_dir(), f"routing revision path is not a directory: {revisions_dir}")
        children = sorted(revisions_dir.iterdir())
        fail(all(item.is_file() and re.fullmatch(r"[0-9]{6}\.json", item.name)
                 for item in children),
             f"routing revision directory contains unexpected content: {revisions_dir}")
        paths.extend(children)

    history: list[tuple[dict[str, Any], Path]] = []
    for expected_revision, path in enumerate(paths, 1):
        record = load_json(path)
        validate_routing(
            record, intake, f"routing revision {expected_revision}",
            intake_sha256=intake_digest,
        )
        fail(routing_revision(record) == expected_revision,
             f"routing history is not contiguous at revision {expected_revision}")
        fail(path.relative_to(folder).as_posix() == routing_relative_path(expected_revision),
             f"routing revision {expected_revision} is stored at a noncanonical path")
        if history:
            validate_routing_transition(history[-1][0], record, history[-1][1])
        history.append((record, path))
    return history


def current_routing(store: Store, work_id: str,
                    intake: dict[str, Any] | None = None) -> tuple[dict[str, Any], Path, list[tuple[dict[str, Any], Path]]]:
    history = routing_history(store, work_id, intake)
    fail(bool(history), f"routing receipt is missing for {work_id}")
    record, path = history[-1]
    return record, path, history


def validate_routing_registry(record: dict[str, Any], routes: dict[str, Any],
                              destinations: dict[str, Any]) -> None:
    runtime_route = record["runtime_route"]
    if runtime_route is not None:
        fail(runtime_route in routes,
             f"routing receipt names unknown runtime route: {runtime_route}")
        fail(record["planning_destination"] in routes[runtime_route].get("allowed_destinations", []),
             f"destination {record['planning_destination']} is not allowed for runtime route {runtime_route}")
    fail(record["planning_destination"] in destinations,
         f"destination is absent from lifecycle registry: {record['planning_destination']}")


def prestart_entries(revision: int) -> set[str]:
    entries = {"intake.json", "routing.json"}
    if revision > 1:
        entries.add("routing-revisions")
    return entries


def routing_is_ready(record: dict[str, Any]) -> bool:
    return (
        record.get("compiled_plan") is not None
        and not record.get("unresolved_questions")
        and not any(
            item.get("applicability") == "undetermined"
            for item in record.get("stage_recommendations", [])
        )
    )


def routing_profile(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(record[key])
        for key in (
            "business_basis", "solution_context", "engagement_intent",
            "planning_destination", "execution_lane", "runtime_route",
        )
    }


def routing_summary(record: dict[str, Any],
                    history: list[tuple[dict[str, Any], Path]] | None = None) -> dict[str, Any]:
    ready = routing_is_ready(record)
    history = history or [(record, Path(routing_relative_path(routing_revision(record))))]
    questions = copy.deepcopy(record["unresolved_questions"])
    undetermined = [
        copy.deepcopy(item) for item in record["stage_recommendations"]
        if item["applicability"] == "undetermined"
    ]
    external_blockers: list[dict[str, Any]] = []
    agent_ready: list[dict[str, Any]] = []
    user_decisions: list[dict[str, Any]] = []

    for index, question in enumerate(questions, 1):
        item = {
            "decision_id": f"ROUTING-QUESTION-{index}",
            "question": question["question"],
            "why_material": question["why_material"],
            "owner": copy.deepcopy(question["owner"]),
            "status": "waiting-for-human" if question["owner"]["kind"] == "human" else "ready",
        }
        if question["owner"]["kind"] == "human":
            user_decisions.append(item)
        else:
            agent_ready.append(item)
    for item in undetermined:
        agent_ready.append({
            "stage_id": item["stage_id"],
            "title": f"Resolve whether {item['stage_id']} applies: {item['reason']}",
            "status": "ready",
        })
    if record.get("compiled_plan") is None and not questions and not undetermined:
        external_blockers.append({
            "kind": "unsupported-runtime-profile",
            "description": "The installed runtime cannot yet compile this profile into applicable stages.",
            "owner": {"actor_id": "system:workbench", "kind": "system"},
            "next_action": "Add and prove stage applicability before lifecycle start.",
        })

    if ready:
        next_action = {
            "description": "Start the lifecycle from this intake-bound routing receipt.",
            "owner": {"actor_id": "agent:workbench", "kind": "agent"},
            "target_type": "stage",
            "target_id": "intake",
        }
        agent_ready.append({
            "stage_id": "intake",
            "title": next_action["description"],
            "status": "ready",
        })
    elif questions:
        first = questions[0]
        next_action = {
            "description": first["question"],
            "owner": copy.deepcopy(first["owner"]),
            "target_type": "decision",
            "target_id": "ROUTING-QUESTION-1",
        }
    elif undetermined:
        next_action = {
            "description": f"Resolve whether {undetermined[0]['stage_id']} applies.",
            "owner": {"actor_id": "agent:workbench", "kind": "agent"},
            "target_type": "stage",
            "target_id": undetermined[0]["stage_id"],
        }
    else:
        next_action = {
            "description": "Add and prove stage applicability for this unsupported profile.",
            "owner": {"actor_id": "system:workbench", "kind": "system"},
            "target_type": "external",
            "target_id": "stage-applicability-compiler",
        }

    resolved_decisions = [
        {
            "decision_id": f"ROUTING-RESOLUTION-R{routing_revision(item):06d}-{index}",
            "question": resolution["question"],
            "answer": resolution["answer"],
            "source_references": copy.deepcopy(resolution["source_references"]),
            "recorded_by": copy.deepcopy(item["owner"]),
            "recorded_at": item["created_at"],
            "status": "resolved",
        }
        for item, _ in history
        for index, resolution in enumerate(item.get("resolved_questions", []), 1)
    ]
    lineage = [
        {
            "routing_revision": routing_revision(item),
            "routing_id": item["routing_id"],
            "uri": path.as_posix() if not path.is_absolute() else routing_relative_path(routing_revision(item)),
            "created_at": item["created_at"],
        }
        for item, path in history
    ]

    return {
        "runtime_version": RUNTIME_VERSION,
        "work_id": record["work_id"],
        "title": record["title"],
        "routing_revision": routing_revision(record),
        "routing_history": lineage,
        "status": "routing-ready" if ready else "routing-blocked",
        "route": "profile-compiled" if ready else (record["runtime_route"] or "undetermined"),
        "planning_destination": record["planning_destination"],
        "routing_profile": routing_profile(record),
        "compiled_plan": copy.deepcopy(record.get("compiled_plan")),
        "current_stage": "intake",
        "current_stage_status": "ready" if ready else "blocked",
        "state_revision": 0,
        "next_action": next_action,
        "authorization_boundary": copy.deepcopy(record["authorization_boundary"]),
        "blockers": [*questions, *undetermined, *external_blockers],
        "human_control": {
            "where": {
                "route": "profile-compiled" if ready else (record["runtime_route"] or "undetermined"),
                "stage": "intake",
                "status": "routing-ready" if ready else "routing-blocked",
            },
            "learned": copy.deepcopy(record["facts"]),
            "decisions": [*resolved_decisions, *user_decisions],
            "why_next": next_action["description"],
            "uncertainties": [
                {"description": item["question"], "status": "unresolved"}
                for item in questions
            ],
        },
        "frontier": {
            "agent_ready": agent_ready,
            "user_decisions": user_decisions,
            "external_blockers": external_blockers,
        },
        "projection_boundary": (
            "intake-bound routing recommendation only; lifecycle start, stage completion, "
            "implementation authorization records, and outcomes remain unproven"
        ),
    }


def build_routing_record(work_id: str, intake: dict[str, Any], intake_path: Path,
                         routing_input: dict[str, Any], owner_id: str,
                         idempotency_key: str, destinations: dict[str, Any],
                         phases: list[dict[str, Any]], *, revision: int = 1,
                         previous: tuple[dict[str, Any], Path] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "record_type": "workbench-routing-receipt",
        "schema_version": RUNTIME_VERSION,
        "routing_id": routing_id(work_id, revision),
        "routing_revision": revision,
        "work_id": work_id,
        "intake": {
            "reference": intake_reference(work_id),
            "sha256": {"algorithm": "sha256", "value": file_digest(intake_path)},
        },
        **copy.deepcopy(routing_input),
        "owner": actor(owner_id),
        "idempotency_key": idempotency_key,
        "created_at": now(),
    }
    if previous is not None:
        previous_record, previous_path = previous
        record["supersedes"] = {
            "reference": routing_reference(work_id, routing_revision(previous_record)),
            "sha256": {"algorithm": "sha256", "value": file_digest(previous_path)},
        }
    boundary = record["authorization_boundary"]
    if "withheld_actions" not in boundary:
        boundary["withheld_actions"] = sorted(
            AUTHORIZATION_ACTIONS - set(boundary["granted_actions"])
        )
    compiled_plan = compile_stage_plan(record, phases, destinations)
    if compiled_plan is not None:
        record["compiled_plan"] = compiled_plan
    record["input_fingerprint"] = {
        "algorithm": "sha256",
        "value": digest(routing_fingerprint_payload(record)),
    }
    validate_routing(
        record, intake, "new routing receipt",
        intake_sha256=file_digest(intake_path),
    )
    if previous is not None:
        validate_routing_transition(previous[0], record, previous[1])
    return record


def finalize_intake(args: argparse.Namespace, store: Store, routes: dict[str, Any],
                    destinations: dict[str, Any], phases: list[dict[str, Any]]) -> dict[str, Any]:
    fail(WORK_ID_RE.fullmatch(args.work_id) is not None, "work_id must match WB-<readable-token>")
    routing_input = load_json(Path(args.routing_input))
    require_shape(
        routing_input,
        ROUTING_INPUT_FIELDS,
        ROUTING_INPUT_FIELDS,
        "routing input",
    )
    with store.locked():
        folder = store.work_dir(args.work_id)
        intake_path = folder / "intake.json"
        fail(intake_path.is_file(), f"finalize-intake requires a captured intake for {args.work_id}")
        fail(not (folder / "events.jsonl").exists(),
             f"cannot finalize intake after work has started: {args.work_id}")
        intake = load_json(intake_path)
        validate_intake(intake)
        record = build_routing_record(
            args.work_id, intake, intake_path, routing_input, args.owner,
            args.idempotency_key, destinations, phases,
        )
        validate_routing_registry(record, routes, destinations)

        routing_path = folder / "routing.json"
        if routing_path.exists():
            history = routing_history(store, args.work_id, intake)
            first = history[0][0]
            fail(first.get("idempotency_key") == args.idempotency_key
                 and first.get("input_fingerprint") == record.get("input_fingerprint"),
                 f"routing receipt already exists with different input or idempotency key: {args.work_id}")
            return {"result": "idempotent", **routing_summary(history[-1][0], history)}
        fail({item.name for item in folder.iterdir()} == {"intake.json"},
             f"work directory contains unexpected pre-start content; recovery is required: {folder}")
        store.transaction({routing_path: encode_json(record)})
        return {"result": "finalized", **routing_summary(record, [(record, routing_path)])}


def revise_routing(args: argparse.Namespace, store: Store, routes: dict[str, Any],
                   destinations: dict[str, Any], phases: list[dict[str, Any]]) -> dict[str, Any]:
    """Append a corrected pre-start routing receipt under the same work ID."""

    fail(WORK_ID_RE.fullmatch(args.work_id) is not None,
         "work_id must match WB-<readable-token>")
    routing_input = load_json(Path(args.routing_input))
    require_shape(
        routing_input,
        ROUTING_INPUT_FIELDS | ROUTING_REVISION_FIELDS,
        ROUTING_INPUT_FIELDS | ROUTING_REVISION_FIELDS,
        "routing revision input",
    )
    with store.locked():
        folder = store.work_dir(args.work_id)
        intake_path = folder / "intake.json"
        fail(intake_path.is_file(),
             f"revise-routing requires a captured intake for {args.work_id}")
        fail(not (folder / "events.jsonl").exists(),
             f"cannot revise routing after work has started: {args.work_id}")
        intake = load_json(intake_path)
        validate_intake(intake)
        history = routing_history(store, args.work_id, intake)
        fail(bool(history),
             f"revise-routing requires a finalized routing receipt for {args.work_id}")
        fail(args.expected_routing_revision >= 1,
             "expected routing revision must be at least one")
        fail(args.expected_routing_revision <= len(history),
             f"stale expected routing revision {args.expected_routing_revision}; current is {len(history)}")

        base = history[args.expected_routing_revision - 1]
        candidate = build_routing_record(
            args.work_id, intake, intake_path, routing_input, args.owner,
            args.idempotency_key, destinations, phases,
            revision=args.expected_routing_revision + 1,
            previous=base,
        )
        validate_routing_registry(candidate, routes, destinations)

        if args.expected_routing_revision < len(history):
            existing = history[args.expected_routing_revision][0]
            fail(existing.get("idempotency_key") == args.idempotency_key
                 and existing.get("input_fingerprint") == candidate.get("input_fingerprint"),
                 f"routing revision {args.expected_routing_revision + 1} already exists with different input or idempotency key")
            return {"result": "idempotent", **routing_summary(history[-1][0], history)}

        fail(not any(item.get("idempotency_key") == args.idempotency_key for item, _ in history),
             f"idempotency key already used by an earlier routing receipt: {args.idempotency_key}")
        fail({item.name for item in folder.iterdir()} == prestart_entries(len(history)),
             f"work directory contains unexpected pre-start content; recovery is required: {folder}")
        revision_path = folder / routing_relative_path(len(history) + 1)
        fail(not revision_path.exists(),
             f"routing revision path already exists: {revision_path}")
        store.transaction({revision_path: encode_json(candidate)})
        updated_history = [*history, (candidate, revision_path)]
        return {"result": "revised", **routing_summary(candidate, updated_history)}


def route_and_start(args: argparse.Namespace, store: Store, routes: dict[str, Any],
                    stages: dict[str, Any], destinations: dict[str, Any],
                    phases: list[dict[str, Any]]) -> dict[str, Any]:
    fail(WORK_ID_RE.fullmatch(args.work_id) is not None, "work_id must match WB-<readable-token>")
    fail(len(args.idempotency_key) <= 240, "idempotency key is too long for atomic route-and-start")
    routing_input = load_json(Path(args.routing_input))
    require_shape(routing_input, ROUTING_INPUT_FIELDS, ROUTING_INPUT_FIELDS, "routing input")
    routing_key = f"{args.idempotency_key}:route"
    start_key = f"{args.idempotency_key}:start"
    with store.locked():
        folder = store.work_dir(args.work_id)
        intake_path = folder / "intake.json"
        routing_path = folder / "routing.json"
        fail(intake_path.is_file(), f"route-and-start requires a captured intake for {args.work_id}")
        intake = load_json(intake_path)
        validate_intake(intake)
        candidate = build_routing_record(
            args.work_id, intake, intake_path, routing_input, args.owner,
            routing_key, destinations, phases,
        )
        validate_routing_registry(candidate, routes, destinations)
        if (folder / "events.jsonl").exists():
            existing = load_json(routing_path)
            validate_routing(existing, intake, intake_sha256=file_digest(intake_path))
            fail(existing.get("input_fingerprint") == candidate.get("input_fingerprint"),
                 "route-and-start retry differs from the persisted routing input")
            state, map_record, events = checked_checkpoint(store, args.work_id)
            fail(any(event.get("idempotency_key") == start_key for event in events),
                 f"work already exists: {args.work_id}")
            return {"result": "idempotent", **summary(state, map_record, existing, store)}
        fail(not routing_path.exists(), f"routing receipt already exists; use start --from-routing for {args.work_id}")
        fail({item.name for item in folder.iterdir()} == {"intake.json"},
             f"work directory contains unexpected pre-start content; recovery is required: {folder}")
        fail(routing_is_ready(candidate),
             "routing receipt has unresolved questions or unresolved stage applicability")
        route_id = "profile-compiled"
        destination_id = candidate["planning_destination"]
        plan_phases = candidate["compiled_plan"]["phases"]
        sequence = [phase["checkpoint_stage"] for phase in plan_phases]
        phase_by_checkpoint = {phase["checkpoint_stage"]: phase for phase in plan_phases}
        routing_bytes = encode_json(candidate)
        fp_input = {
            "command": "start", "work_id": args.work_id,
            "title": candidate["title"], "desired_outcome": candidate["desired_outcome"],
            "route": route_id, "destination": destination_id, "owner": args.owner,
            "intake_reference": intake_reference(args.work_id),
            "intake_sha256": file_digest(intake_path),
            "routing_reference": routing_reference(args.work_id),
            "routing_sha256": hashlib.sha256(routing_bytes).hexdigest(),
        }
        state, map_record, event = build_start_documents(
            args.work_id, candidate["title"], candidate["desired_outcome"], route_id,
            destination_id, args.owner, sequence, phase_by_checkpoint, stages,
            start_key, fp_input, True,
        )
        for record, label in ((state, "new state"), (map_record, "new map"), (event, "new event")):
            validate_record(record, label)
        store.transaction({
            routing_path: routing_bytes,
            folder / "state.json": encode_json(state),
            folder / "map.json": encode_json(map_record),
            folder / "events.jsonl": encode_events([event]),
            store.root / "active-work.json": encode_json({"work_id": args.work_id}),
        })
        return {"result": "created", **summary(state, map_record, candidate, store)}


VERIFICATION_SCOPES = (
    "feature-implementation", "feature-focused", "integration-journey",
    "repository-health", "user-acceptance", "deployment-readiness",
    "deployed-behavior", "business-outcome",
)


def verification_summary(state: dict[str, Any], store: Store | None) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {scope: [] for scope in VERIFICATION_SCOPES}
    if store is not None:
        folder = store.work_dir(state["work_id"])
        for proof_id in state.get("proof_ids", []):
            record = load_json(folder / "records" / f"{proof_id}.json")
            scope = record.get("verification_scope")
            if scope is None:
                kinds = {
                    item.get("kind") for item in [*record.get("required_proof", []), *record.get("achieved_proof", [])]
                }
                if "business-outcome" in kinds:
                    scope = "business-outcome"
                elif "deployed-behavior" in kinds:
                    scope = "deployed-behavior"
                elif "integration" in kinds:
                    scope = "integration-journey"
                elif "local-implementation" in kinds:
                    scope = "feature-focused"
            if scope in grouped:
                grouped[scope].append(record)
    precedence = {"failed": 5, "blocked": 4, "pending": 3, "passed": 2, "not-applicable": 1}
    result: dict[str, Any] = {}
    for scope, proofs in grouped.items():
        status = max((proof.get("status", "pending") for proof in proofs),
                     key=lambda value: precedence.get(value, 0), default="not-recorded")
        result[scope] = {
            "status": status,
            "proof_ids": [proof["proof_id"] for proof in proofs],
        }
    return result


def summary(state: dict[str, Any], map_record: dict[str, Any],
            routing: dict[str, Any] | None = None, store: Store | None = None) -> dict[str, Any]:
    blockers = [
        {"node_id": node["node_id"], "status": node["status"], "title": node["title"]}
        for node in map_record["nodes"] if node.get("status") in BLOCKING
    ]
    current = next(item for item in state["stages"] if item["stage_id"] == state["current_stage"])
    learned = [
        {"node_id": node["node_id"], "title": node["title"], "evidence": node.get("evidence", [])}
        for node in map_record["nodes"] if node.get("status") == "evidence-established"
    ]
    decisions = [
        {"node_id": node["node_id"], "question": node.get("question", node["title"]), "status": node["status"]}
        for node in map_record["nodes"] if node.get("kind") == "decision"
        and node.get("status") in {"waiting-for-human", "decided"}
    ]
    uncertainties = [
        {"id": item.get("fog_id"), "description": item.get("description"), "status": item.get("status")}
        for item in map_record.get("fog", []) if item.get("status") == "unresolved"
    ]
    agent_ready = [
        {"node_id": node["node_id"], "title": node["title"], "status": node["status"]}
        for node in map_record["nodes"] if node.get("status") in {"ready", "in-progress"}
        and (node.get("owner") or {}).get("kind") == "agent"
    ]
    user_decisions = [item for item in decisions if item["status"] == "waiting-for-human"]
    external_blockers = [item for item in blockers if item["status"] in {"external-blocked", "evidence-blocked"}]
    if current.get("status") == "active" and (current.get("owner") or {}).get("kind") == "agent" and not blockers:
        agent_ready.append({"stage_id": current["stage_id"], "title": (current.get("next_action") or {}).get("description"), "status": "active"})
    result = {
        "runtime_version": RUNTIME_VERSION,
        "work_id": state["work_id"], "title": state["title"], "status": state["status"],
        "route": state["route_selection"]["route"], "planning_destination": state["planning_destination"],
        "current_stage": state["current_stage"], "current_stage_status": current["status"],
        "current_phase": current.get("phase_id"),
        "current_activities": copy.deepcopy(current.get("activity_stage_ids", [current["stage_id"]])),
        "state_revision": state["state_revision"], "next_action": state.get("next_action"),
        "blockers": blockers,
        "verification": verification_summary(state, store),
        "human_control": {
            "where": {"route": state["route_selection"]["route"], "phase": current.get("phase_id"),
                      "stage": state["current_stage"], "status": state["status"]},
            "learned": learned,
            "decisions": decisions,
            "why_next": (state.get("next_action") or {}).get("description"),
            "uncertainties": uncertainties,
        },
        "frontier": {"agent_ready": agent_ready, "user_decisions": user_decisions, "external_blockers": external_blockers},
        "projection_boundary": "replayed and snapshot-compared; not authorization or outcome proof",
    }
    if routing is not None:
        result["routing_profile"] = routing_profile(routing)
        result["routing_rationale"] = routing["rationale"]
        result["routing_revision"] = routing_revision(routing)
        result["authorization_boundary"] = copy.deepcopy(routing["authorization_boundary"])
    return result


def ensure_idempotency(events: list[dict[str, Any]], key: str, fp_input: dict[str, Any]) -> bool:
    expected = digest(fp_input)
    matches = [event for event in events if event.get("idempotency_key") == key]
    if not matches:
        return False
    fail(all((event.get("input_fingerprint") or {}).get("value") == expected for event in matches), f"idempotency key already used with different input: {key}")
    return True


def build_start_documents(work_id: str, title: str, outcome: str, route_id: str,
                          destination_id: str, owner_id: str, sequence: list[str],
                          phase_by_checkpoint: dict[str, dict[str, Any]],
                          stages: dict[str, Any], idempotency_key: str,
                          fp_input: dict[str, Any], routed: bool) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    timestamp = now()
    first = sequence[0]
    eid = event_id(work_id, 1)
    owner = actor(owner_id)
    stage_states = []
    for index, stage_id in enumerate(sequence):
        phase = phase_by_checkpoint.get(stage_id)
        item: dict[str, Any] = {
            "stage_id": stage_id,
            "applicability": "applicable",
            "status": "active" if index == 0 else "pending",
            "owner": {"actor_id": "agent:workbench", "kind": "agent"},
            "applicability_reason": (
                f"Checkpoint for the {phase['phase_id']} phase."
                if phase else f"Included by the {route_id} legacy lifecycle route."
            ),
            "output_artifact_ids": [],
        }
        if phase:
            item["phase_id"] = phase["phase_id"]
            item["activity_stage_ids"] = [
                activity["stage_id"] for activity in phase["activities"]
                if activity["applicability"] == "applicable"
            ]
        if index == 0:
            item["started_at"] = timestamp
            item["next_action"] = {
                "description": f"Satisfy the {stages[first]['exit_gate']} exit gate.",
                "owner": item["owner"], "target_type": "stage", "target_id": first,
            }
        stage_states.append(item)
    next_action = copy.deepcopy(stage_states[0]["next_action"])
    state = {
        "record_type": "workbench-state", "schema_version": RUNTIME_VERSION if routed else "0.1.0",
        "state_revision": 1, "work_id": work_id, "title": title,
        "desired_outcome": outcome, "planning_destination": destination_id,
        "route_selection": {
            "route": route_id,
            "rationale": ("Compiled from the intake-bound routing profile."
                          if routed else f"Selected by start command for destination {destination_id}."),
            "selected_by": owner, "selected_at": timestamp,
        },
        "current_stage": first, "stages": stage_states,
        "map_id": f"MAP-{work_id.removeprefix('WB-')}", "owner": owner,
        "status": "active", "next_action": next_action, "latest_event_id": eid,
        "artifact_ids": [], "decision_ids": [], "proof_ids": [],
        "authorization_ids": [], "handoff_ids": [],
        "created_at": timestamp, "updated_at": timestamp,
    }
    outcome_node = f"O-{work_id.removeprefix('WB-')}"
    map_record = {
        "record_type": "workbench-map", "schema_version": RUNTIME_VERSION if routed else "0.1.0",
        "map_id": state["map_id"], "work_id": work_id,
        "desired_outcome_node_id": outcome_node, "planning_destination": destination_id,
        "nodes": [{
            "node_id": outcome_node, "kind": "outcome", "title": title,
            "why_it_matters": outcome, "owner": owner, "status": "in-progress",
            "next_action": next_action,
            "done_when": [f"The {destination_id} destination is proven and authorized complete."],
            "evidence": [],
        }],
        "edges": [], "fog": [], "created_at": timestamp, "updated_at": timestamp,
    }
    changes = [
        change("work", work_id, "/document", (False, None), (True, state)),
        change("map", state["map_id"], "/document", (False, None), (True, map_record)),
    ]
    event = make_event(
        work_id, 1, "work-started", owner_id, idempotency_key,
        fp_input, changes, "Start Workbench work item.",
    )
    return state, map_record, event


def start(args: argparse.Namespace, store: Store, routes: dict[str, Any], stages: dict[str, Any],
          destinations: dict[str, Any]) -> dict[str, Any]:
    fail(WORK_ID_RE.fullmatch(args.work_id) is not None, "work_id must match WB-<readable-token>")
    with store.locked():
        folder = store.work_dir(args.work_id)
        intake_path = folder / "intake.json"
        routing_path = folder / "routing.json"
        intake: dict[str, Any] | None = None
        routing: dict[str, Any] | None = None
        if args.from_routing:
            fail(intake_path.is_file(), f"--from-routing requires a captured intake for {args.work_id}")
            fail(routing_path.is_file(), f"--from-routing requires a routing receipt for {args.work_id}")
            intake = load_json(intake_path)
            validate_intake(intake)
            routing, routing_path, _ = current_routing(
                store, args.work_id, intake
            )
            fail(routing_is_ready(routing),
                 "routing receipt has unresolved questions or unresolved stage applicability")
            route_id = "profile-compiled"
            destination_id = routing["planning_destination"]
            title = routing["title"]
            outcome = routing["desired_outcome"]
            owner_id = routing["owner"]["actor_id"]
            if args.route is not None:
                fail(args.route in {route_id, routing.get("runtime_route")},
                     "start route does not match routing receipt")
            for supplied, expected, label in (
                (args.destination, destination_id, "destination"),
                (args.title, title, "title"),
                (args.outcome, outcome, "outcome"),
                (args.owner, owner_id, "owner"),
            ):
                fail(supplied is None or supplied == expected,
                     f"start {label} does not match routing receipt")
            plan_phases = routing["compiled_plan"]["phases"]
            sequence = [phase["checkpoint_stage"] for phase in plan_phases]
            phase_by_checkpoint = {phase["checkpoint_stage"]: phase for phase in plan_phases}
        elif args.from_intake:
            fail(intake_path.is_file(), f"--from-intake requires a captured intake for {args.work_id}")
            fail(not routing_path.exists(),
                 f"routing receipt exists for {args.work_id}; use --from-routing to bind both records")
            intake = load_json(intake_path)
            validate_intake(intake)
            fail(args.route is not None and args.destination is not None
                 and args.title is not None and args.outcome is not None,
                 "legacy --from-intake start requires route, destination, title, and outcome")
            route_id = args.route
            destination_id = args.destination
            title = args.title
            outcome = args.outcome
            owner_id = args.owner or "user:local"
            fail(route_id in routes, f"unknown route: {route_id}")
            route = routes[route_id]
            fail(destination_id in route.get("allowed_destinations", []),
                 f"destination {destination_id} is not allowed for route {route_id}")
            sequence = list(route["ordered_stages"])
            phase_by_checkpoint = {}
        elif intake_path.exists() or routing_path.exists():
            fail(False, f"captured intake exists for {args.work_id}; use --from-routing when finalized, otherwise --from-intake")
        else:
            fail(args.route is not None and args.destination is not None
                 and args.title is not None and args.outcome is not None,
                 "direct start requires route, destination, title, and outcome")
            route_id = args.route
            destination_id = args.destination
            title = args.title
            outcome = args.outcome
            owner_id = args.owner or "user:local"
            fail(route_id in routes, f"unknown route: {route_id}")
            route = routes[route_id]
            fail(destination_id in route.get("allowed_destinations", []),
                 f"destination {destination_id} is not allowed for route {route_id}")
            sequence = list(route["ordered_stages"])
            phase_by_checkpoint = {}
        fail(destination_id in destinations,
             f"destination is absent from lifecycle registry: {destination_id}")
        fail(destinations[destination_id]["completion_stage"] == sequence[-1]
             if routing is not None else destinations[destination_id]["completion_stage"] in sequence,
             "destination completion stage is absent from the execution plan")
        fp_input = {
            "command": "start", "work_id": args.work_id, "title": title,
            "desired_outcome": outcome, "route": route_id,
            "destination": destination_id, "owner": owner_id,
        }
        if intake is not None:
            fp_input["intake_reference"] = intake_reference(args.work_id)
            fp_input["intake_sha256"] = file_digest(intake_path)
        if routing is not None:
            fp_input["routing_reference"] = routing_reference(
                args.work_id, routing_revision(routing)
            )
            fp_input["routing_sha256"] = file_digest(routing_path)
        if (folder / "events.jsonl").exists():
            state, map_record, events = checked_checkpoint(store, args.work_id)
            fail(ensure_idempotency(events, args.idempotency_key, fp_input), f"work already exists: {args.work_id}")
            return {"result": "idempotent", **summary(state, map_record, routing, store)}
        if folder.exists():
            expected_files = (
                prestart_entries(routing_revision(routing))
                if routing is not None else {"intake.json"}
            )
            fail(intake is not None and {item.name for item in folder.iterdir()} == expected_files,
                 f"work directory contains unexpected pre-start content; recovery is required: {folder}")
        state, map_record, event = build_start_documents(
            args.work_id, title, outcome, route_id, destination_id, owner_id,
            sequence, phase_by_checkpoint, stages, args.idempotency_key,
            fp_input, routing is not None,
        )
        validate_record(state, "new state")
        validate_record(map_record, "new map")
        validate_record(event, "new event")
        store.transaction({folder / "state.json": encode_json(state), folder / "map.json": encode_json(map_record),
                           folder / "events.jsonl": encode_events([event]),
                           store.root / "active-work.json": encode_json({"work_id": args.work_id})})
        return {"result": "created", **summary(state, map_record, routing, store)}


def parse_time(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise WorkbenchError(f"{label} is not a valid ISO timestamp") from exc
    fail(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def matching_authorization(record: dict[str, Any], action: str, state: dict[str, Any],
                           target_stage: str | None, operation_time: datetime) -> bool:
    if not (record.get("record_type") == "workbench-authorization"
            and record.get("action") == action and record.get("status") == "granted"
            and record.get("work_id") == state["work_id"]
            and isinstance(record.get("authorization_id"), str)):
        return False
    grant = record.get("grant") or {}
    if not (isinstance(grant.get("granted_by"), dict)
            and grant["granted_by"].get("kind") == "human"
            and isinstance(grant.get("granted_at"), str)
            and parse_time(grant["granted_at"], "authorization granted_at") <= operation_time):
        return False
    expires = grant.get("expires_at")
    if expires and parse_time(expires, "authorization expires_at") <= operation_time:
        return False
    targets = (record.get("scope") or {}).get("targets", [])
    for target in targets:
        if not isinstance(target, dict):
            continue
        if action == "closure":
            if target.get("kind") == "work" and target.get("target_id") == state["work_id"] and target.get("planning_destination") == state["planning_destination"]:
                return True
        elif target.get("kind") == "work" and target.get("target_id") == state["work_id"]:
            return True
        elif target.get("kind") == "stage" and target.get("target_id") == target_stage and target.get("stage_id", target_stage) == target_stage:
            return True
    return False


def validate_reference_resolution(reference: dict[str, Any], state: dict[str, Any],
                                  map_record: dict[str, Any], records: dict[str, dict[str, Any]],
                                  store: Store, label: str) -> None:
    validate_record_ref(reference, label)
    kind = reference["record_type"]
    record_id = reference["record_id"]
    if kind == "work":
        fail(record_id == state["work_id"], f"{label} points to another work item")
    elif kind == "map":
        fail(record_id == map_record["map_id"], f"{label} points to another map")
    elif kind == "node":
        fail(any(node["node_id"] == record_id for node in map_record["nodes"]),
             f"{label} points to a missing map node")
    elif kind in {"artifact", "decision", "proof", "authorization", "handoff"}:
        fail(record_id in records, f"{label} points to an unregistered record: {record_id}")
        if kind == "artifact" and reference.get("path"):
            artifact = records[record_id]
            location = artifact.get("location") or {}
            fail(location.get("kind") == "workspace-path"
                 and location.get("value") == reference["path"],
                 f"{label} artifact path differs from its registered location")
    elif kind == "external":
        uri = reference.get("uri")
        fail(isinstance(uri, str) and uri.strip(), f"{label} external reference needs a URI")
        parsed = urlsplit(uri)
        if not parsed.scheme:
            raw = Path(uri)
            fail(not raw.is_absolute(), f"{label} local external path must be repository-relative")
            path = (store.repo / raw).resolve()
            fail(path == store.repo or store.repo in path.parents,
                 f"{label} external path escapes the repository")
            fail(path.exists(), f"{label} external path does not exist: {uri}")


def accept_handoff(args: argparse.Namespace, store: Store) -> dict[str, Any]:
    bundle = load_json(Path(args.handoff_bundle))
    require_shape(bundle, {"handoff", "records"}, {"handoff", "records"}, "handoff bundle")
    handoff = bundle["handoff"]
    bundled_records = bundle["records"]
    fail(isinstance(handoff, dict), "handoff bundle handoff must be an object")
    fail(isinstance(bundled_records, list) and all(isinstance(item, dict) for item in bundled_records),
         "handoff bundle records must be objects")
    validate_record(handoff, "handoff")
    fail(handoff.get("record_type") == "workbench-handoff", "handoff bundle has the wrong primary record")
    fail(handoff.get("work_id") == args.work_id, "handoff work_id mismatch")
    all_new = [*bundled_records, handoff]
    refs: list[dict[str, str]] = []
    ids: set[str] = set()
    for index, record in enumerate(all_new):
        validate_record(record, f"handoff bundle record[{index}]")
        fail(record.get("work_id") == args.work_id,
             f"handoff bundle record[{index}] belongs to another work item")
        reference = record_reference(record)
        fail(reference["record_id"] not in ids,
             f"handoff bundle repeats record ID: {reference['record_id']}")
        ids.add(reference["record_id"])
        refs.append(reference)
    fail(all(record.get("record_type") in {
        "workbench-artifact", "workbench-decision", "workbench-proof", "workbench-authorization",
    } for record in bundled_records),
         "handoff bundle records may contain only artifacts, decisions, proofs, and authorizations")
    record_refs = [record_reference(handoff), *(record_reference(record) for record in bundled_records)]
    fp_input = {
        "command": "accept-handoff",
        "work_id": args.work_id,
        "handoff_id": handoff["handoff_id"],
        "handoff_sha256": digest(handoff),
        "record_digests": {record_reference(record)["record_id"]: digest(record) for record in bundled_records},
        "record_refs": record_refs,
        "inputs_used": copy.deepcopy(handoff["inputs_used"]),
        "actor": args.actor,
        "expected_revision": args.expected_revision,
    }
    with store.locked():
        state, map_record, events = checked_checkpoint(store, args.work_id)
        if ensure_idempotency(events, args.idempotency_key, fp_input):
            return {"result": "idempotent", **summary(state, map_record, store=store)}
        if args.expected_revision is not None:
            fail(args.expected_revision == state["state_revision"],
                 f"stale expected revision {args.expected_revision}; current is {state['state_revision']}")
        current = next(item for item in state["stages"] if item["stage_id"] == state["current_stage"])
        fail(handoff["stage"] == current["stage_id"],
             "handoff stage must match the current operational checkpoint")
        fail(any(node["node_id"] == handoff["node_id"] for node in map_record["nodes"]),
             "handoff node_id is absent from the canonical map")

        folder = store.work_dir(args.work_id)
        known_records: dict[str, dict[str, Any]] = {}
        for field in ("artifact_ids", "decision_ids", "proof_ids", "authorization_ids", "handoff_ids"):
            for record_id in state.get(field, []):
                known_records[record_id] = load_json(folder / "records" / f"{record_id}.json")
        for record in bundled_records:
            _, _, record_id = record_identity(record)
            known_records[record_id] = record
            validated_workspace_artifact(store, record)
        known_records[handoff["handoff_id"]] = handoff

        is_v03 = tuple(int(part) for part in handoff["schema_version"].split("-")[0].split(".")[:3]) >= (0, 3, 0)
        if is_v03:
            expected_input_fingerprint = digest({
                "inputs_used": handoff["inputs_used"],
                "policy_versions": handoff["policy_versions"],
            })
            fail((handoff.get("input_fingerprint") or {}).get("value") == expected_input_fingerprint,
                 "handoff input fingerprint does not match inputs_used and policy_versions")
        for index, reference in enumerate(handoff["inputs_used"]):
            validate_reference_resolution(reference, state, map_record, known_records, store,
                                          f"handoff.inputs_used[{index}]")

        produced_ids = {item["record_id"] for item in handoff["artifacts_produced"]}
        supplied_artifact_ids = {
            record["artifact_id"] for record in bundled_records
            if record.get("record_type") == "workbench-artifact"
        }
        fail(produced_ids == supplied_artifact_ids,
             "handoff artifacts_produced must exactly match bundled artifact records")
        for reference in handoff["artifacts_produced"]:
            validate_reference_resolution(reference, state, map_record, known_records, store,
                                          "handoff.artifacts_produced")
        decision_ids = {
            record["decision_id"] for record in bundled_records
            if record.get("record_type") == "workbench-decision"
        }
        fail({item["decision_id"] for item in handoff["decisions_required"]} <= decision_ids,
             "handoff decisions_required must be supplied as decision records")
        fail(set(handoff["authorization_ids"]) <= set(state.get("authorization_ids", [])) | {
            record["authorization_id"] for record in bundled_records
            if record.get("record_type") == "workbench-authorization"
        }, "handoff references an unregistered authorization")

        updated = copy.deepcopy(state)
        updated_map = copy.deepcopy(map_record)
        timestamp = now()
        new_revision = state["state_revision"] + 1
        eid = event_id(args.work_id, new_revision)
        fields = {
            "workbench-artifact": ("artifact_ids", "artifact_id"),
            "workbench-decision": ("decision_ids", "decision_id"),
            "workbench-proof": ("proof_ids", "proof_id"),
            "workbench-authorization": ("authorization_ids", "authorization_id"),
        }
        for record in bundled_records:
            field, id_field = fields[record["record_type"]]
            updated[field] = list(dict.fromkeys([*updated.get(field, []), record[id_field]]))
        updated["handoff_ids"] = list(dict.fromkeys([*updated.get("handoff_ids", []), handoff["handoff_id"]]))
        stage_index = next(index for index, item in enumerate(updated["stages"])
                           if item["stage_id"] == updated["current_stage"])
        updated["stages"][stage_index]["output_artifact_ids"] = list(dict.fromkeys([
            *updated["stages"][stage_index].get("output_artifact_ids", []), *sorted(produced_ids),
        ]))
        output_references = [record_reference(handoff), *(record_reference(record) for record in bundled_records)]
        final_basis = {
            "evidence-established": "evidence", "completed": "completion",
            "excluded": "exclusion", "superseded": "supersession",
        }
        for update in handoff["node_updates"]:
            node = next(node for node in updated_map["nodes"] if node["node_id"] == update["node_id"])
            node["status"] = update["proposed_status"]
            if update["proposed_status"] in {"draft", "ready", "in-progress", "waiting-for-human", "evidence-blocked", "external-blocked"}:
                fail("next_action" in handoff, "active or blocked node update requires handoff.next_action")
                node["next_action"] = copy.deepcopy(handoff["next_action"])
                node.pop("resolution", None)
            elif update["proposed_status"] == "decided":
                decision = next((record for record in bundled_records
                                 if record.get("record_type") == "workbench-decision"
                                 and record.get("node_id") == node["node_id"]
                                 and record.get("state") == "confirmed"), None)
                fail(decision is not None, "decided node update requires a confirmed bundled decision")
                node.pop("next_action", None)
                node["resolution"] = {
                    "basis": decision["resolution"]["basis"], "rationale": update["rationale"],
                    "resolved_at": timestamp, "resolved_by": copy.deepcopy(decision["resolution"]["resolved_by"]),
                    "references": [record_reference(decision)],
                }
            else:
                node.pop("next_action", None)
                resolution = {
                    "basis": final_basis[update["proposed_status"]],
                    "rationale": update["rationale"], "resolved_at": timestamp,
                    "resolved_by": actor(args.actor), "references": output_references,
                }
                if update["proposed_status"] == "superseded":
                    fail(False, "superseded node updates require the future route-correction command")
                node["resolution"] = resolution
        updated["state_revision"] = new_revision
        updated["latest_event_id"] = eid
        updated["updated_at"] = timestamp
        if handoff["node_updates"]:
            updated_map["updated_at"] = timestamp

        changes: list[dict[str, Any]] = []
        for pointer in ("/artifact_ids", "/decision_ids", "/proof_ids", "/authorization_ids", "/handoff_ids",
                        f"/stages/{stage_index}/output_artifact_ids", "/state_revision", "/latest_event_id", "/updated_at"):
            if get_pointer(state, pointer) != get_pointer(updated, pointer):
                changes.append(change("work", args.work_id, pointer,
                                      get_pointer(state, pointer), get_pointer(updated, pointer)))
        for index, _ in enumerate(map_record["nodes"]):
            for suffix in ("status", "next_action", "resolution"):
                pointer = f"/nodes/{index}/{suffix}"
                if get_pointer(map_record, pointer) != get_pointer(updated_map, pointer):
                    changes.append(change("map", map_record["map_id"], pointer,
                                          get_pointer(map_record, pointer), get_pointer(updated_map, pointer)))
        if map_record.get("updated_at") != updated_map.get("updated_at"):
            changes.append(change("map", map_record["map_id"], "/updated_at",
                                  get_pointer(map_record, "/updated_at"), get_pointer(updated_map, "/updated_at")))
        event = make_event(
            args.work_id, new_revision, "handoff-accepted", args.actor,
            args.idempotency_key, fp_input, changes,
            f"Accept specialist handoff {handoff['handoff_id']}.",
            inputs=handoff["inputs_used"],
            outputs=[{"record_type": "work", "record_id": args.work_id}, *record_refs],
            cause_kind="specialist-output",
        )
        validate_record(updated, "handoff-updated state")
        validate_record(updated_map, "handoff-updated map")
        validate_record(event, "handoff event")
        writes = {
            folder / "state.json": encode_json(updated),
            folder / "map.json": encode_json(updated_map),
            folder / "events.jsonl": encode_events([*events, event]),
        }
        for record in all_new:
            _, _, record_id = record_identity(record)
            path = folder / "records" / f"{record_id}.json"
            if path.exists():
                fail(load_json(path) == record, f"record ID already exists with different content: {record_id}")
            writes[path] = encode_json(record)
        store.transaction(writes)
        return {"result": "accepted", **summary(updated, updated_map, store=store)}


def verify_gate(receipt: dict[str, Any], state: dict[str, Any], map_record: dict[str, Any],
                stages: dict[str, Any], destination: dict[str, Any], entering_stage: str | None,
                store: Store) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stage_id = state["current_stage"]
    required = {"work_id", "state_revision", "stage_id", "exit_gate", "result", "evidence", "checked_at", "checked_by"}
    fail(required <= set(receipt), f"gate receipt missing: {', '.join(sorted(required - set(receipt)))}")
    fail(receipt["work_id"] == state["work_id"], "gate receipt work_id mismatch")
    fail(receipt["state_revision"] == state["state_revision"], "gate receipt state_revision is stale or mismatched")
    fail(receipt["stage_id"] == stage_id, "gate receipt stage_id mismatch")
    fail(receipt["exit_gate"] == stages[stage_id]["exit_gate"], "gate receipt exit_gate mismatch")
    fail(receipt["result"] == "passed", "gate receipt did not pass")
    fail(isinstance(receipt["evidence"], list) and receipt["evidence"], "gate receipt needs non-empty evidence")
    checked_at = parse_time(receipt["checked_at"], "gate receipt checked_at")
    operation_time = datetime.now(timezone.utc)
    fail(operation_time - timedelta(days=7) <= checked_at <= operation_time + timedelta(minutes=5),
         "gate receipt checked_at is stale or unreasonably in the future")
    checked_by = receipt["checked_by"]
    if isinstance(checked_by, str):
        fail(ACTOR_ID_RE.fullmatch(checked_by) is not None, "gate receipt checked_by is invalid")
    else:
        validate_actor(checked_by, "gate receipt checked_by")
    proofs = receipt.get("proof_records", [])
    auths = receipt.get("authorization_records", [])
    fail(isinstance(proofs, list) and all(isinstance(item, dict) for item in proofs), "proof_records must be objects")
    fail(isinstance(auths, list) and all(isinstance(item, dict) for item in auths), "authorization_records must be objects")
    proof_ids = [item.get("proof_id") for item in proofs]
    authorization_ids = [item.get("authorization_id") for item in auths]
    fail(len(proof_ids) == len(set(proof_ids)), "proof_records contains duplicate proof_id values")
    fail(len(authorization_ids) == len(set(authorization_ids)),
         "authorization_records contains duplicate authorization_id values")
    for proof in proofs:
        validate_record(proof, f"proof record {proof.get('proof_id', '<missing>')}")
        fail(proof.get("record_type") == "workbench-proof" and proof.get("work_id") == state["work_id"]
             and isinstance(proof.get("proof_id"), str), "proof record is invalid or out of scope")
    for authorization in auths:
        validate_record(authorization, f"authorization record {authorization.get('authorization_id', '<missing>')}")
        fail(authorization.get("record_type") == "workbench-authorization"
             and authorization.get("work_id") == state["work_id"]
             and isinstance(authorization.get("authorization_id"), str), "authorization record is invalid or out of scope")
    folder = store.work_dir(state["work_id"])
    known_records: dict[str, dict[str, Any]] = {}
    for field in ("artifact_ids", "decision_ids", "proof_ids", "authorization_ids", "handoff_ids"):
        for record_id in state.get(field, []):
            known_records[record_id] = load_json(folder / "records" / f"{record_id}.json")
    for record in [*proofs, *auths]:
        known_records[record_reference(record)["record_id"]] = record
    for index, reference in enumerate(receipt["evidence"]):
        validate_reference_resolution(reference, state, map_record, known_records, store,
                                      f"gate receipt evidence[{index}]")
    if tuple(int(part) for part in state["schema_version"].split("-")[0].split(".")[:3]) >= (0, 3, 0):
        fail(any(reference["record_type"] in {"artifact", "decision", "proof", "handoff"}
                 for reference in receipt["evidence"]),
             "v0.3 checkpoint evidence must include a registered artifact, decision, proof, or handoff")
    available_proofs = [
        record for record in known_records.values()
        if record.get("record_type") == "workbench-proof"
    ]
    available_auths = [
        record for record in known_records.values()
        if record.get("record_type") == "workbench-authorization"
    ]
    if entering_stage in {"implementation", "release"}:
        action = "implementation" if entering_stage == "implementation" else "deployment"
        fail(any(matching_authorization(item, action, state, entering_stage, operation_time) for item in available_auths),
             f"entering {entering_stage} requires an unexpired, in-scope granted {action} authorization")
    completing = stage_id == destination["completion_stage"]
    required_kind = destination["required_proof_kind"] if completing else {
        "local-verification": "local-implementation",
        "deployed-verification": "deployed-behavior",
        "outcome-verification": "business-outcome",
    }.get(stage_id)
    if required_kind:
        fail(any(proof.get("status") == "passed" and any(
            result.get("kind") == required_kind and result.get("result") == "passed"
            for result in proof.get("achieved_proof", []) if isinstance(result, dict)
        ) for proof in available_proofs), f"stage or destination completion requires passed {required_kind} proof")
    if completing:
        fail(any(matching_authorization(item, "closure", state, None, operation_time) for item in available_auths),
             "destination completion requires unexpired closure authorization scoped to this work and destination")
    return available_proofs, available_auths


def advance(args: argparse.Namespace, store: Store, routes: dict[str, Any], stages: dict[str, Any],
            destinations: dict[str, Any]) -> dict[str, Any]:
    with store.locked():
        state, map_record, events = checked_checkpoint(store, args.work_id)
        if args.accepted_handoff:
            handoff_path = store.work_dir(args.work_id) / "records" / f"{args.accepted_handoff}.json"
            fail(handoff_path.is_file(), f"accepted handoff is not registered: {args.accepted_handoff}")
            accepted = load_json(handoff_path)
            validate_record(accepted, "accepted handoff")
            fail(accepted.get("record_type") == "workbench-handoff"
                 and accepted.get("work_id") == args.work_id,
                 "accepted handoff is invalid or out of scope")
            acceptance_event = next((
                event for event in events
                if event.get("event_type") == "handoff-accepted"
                and ((event.get("payload") or {}).get("fingerprint_input") or {}).get("handoff_id")
                == args.accepted_handoff
            ), None)
            fail(acceptance_event is not None,
                 "accepted handoff has no matching acceptance event")
            receipt = {
                "work_id": args.work_id,
                "state_revision": acceptance_event["state_revision_after"],
                "stage_id": accepted["stage"],
                "exit_gate": stages[accepted["stage"]]["exit_gate"],
                "result": "passed",
                "evidence": [
                    {"record_type": "handoff", "record_id": accepted["handoff_id"]},
                    *copy.deepcopy(accepted["artifacts_produced"]),
                ],
                "checked_at": acceptance_event["occurred_at"],
                "checked_by": actor(args.actor),
            }
        else:
            receipt = load_json(Path(args.gate_receipt))
        order = [item["stage_id"] for item in state["stages"]]
        current_index = order.index(state["current_stage"])
        destination = destinations[state["planning_destination"]]
        fp_input = {
            "command": "advance-stage",
            "work_id": args.work_id,
            "gate_receipt": receipt,
            "actor": args.actor,
            "expected_revision": args.expected_revision,
        }
        if ensure_idempotency(events, args.idempotency_key, fp_input):
            return {"result": "idempotent", **summary(state, map_record, store=store)}
        if args.expected_revision is not None:
            fail(args.expected_revision == state["state_revision"], f"stale expected revision {args.expected_revision}; current is {state['state_revision']}")
        if args.accepted_handoff:
            fail(accepted.get("stage") == state["current_stage"],
                 "accepted handoff does not cover the current operational checkpoint")
        current = state["stages"][current_index]
        fail(current["status"] == "active", "current stage is not active")
        fail(all(item["status"] in {"complete", "skipped"} for item in state["stages"][:current_index]), "prior route stage is incomplete")
        blockers = [node for node in map_record["nodes"] if node.get("status") in BLOCKING]
        fail(not blockers, "active human/external blocker prevents stage advancement: " + ", ".join(node["node_id"] for node in blockers))
        destination_complete = state["current_stage"] == destination["completion_stage"]
        entering_stage = None if destination_complete else order[current_index + 1]
        proofs, authorizations = verify_gate(
            receipt, state, map_record, stages, destination, entering_stage, store
        )
        updated = copy.deepcopy(state)
        updated_map = copy.deepcopy(map_record)
        timestamp = now()
        new_revision = state["state_revision"] + 1
        eid = event_id(args.work_id, new_revision)
        updated_current = updated["stages"][current_index]
        updated_current["status"] = "complete"
        updated_current["completed_at"] = timestamp
        updated_current.pop("next_action", None)
        if destination_complete:
            updated["status"] = destination["completion_status"]
            updated.pop("next_action", None)
            proof_ids = [item["proof_id"] for item in proofs if item.get("status") == "passed"]
            authorization_id = next(item.get("authorization_id") for item in authorizations
                                    if matching_authorization(item, "closure", state, None, datetime.now(timezone.utc)))
            fail(isinstance(authorization_id, str) and authorization_id, "closure authorization record needs authorization_id")
            updated["completion"] = {"claim": f"Planning destination {state['planning_destination']} completed.",
                                     "proof_ids": proof_ids, "open_obligation_node_ids": [],
                                     "authorized_by": authorization_id, "completed_at": timestamp}
            outcome = next(node for node in updated_map["nodes"] if node["node_id"] == updated_map["desired_outcome_node_id"])
            outcome["status"] = "completed"
            outcome.pop("next_action", None)
            outcome["resolution"] = {"basis": "completion", "rationale": "The selected planning destination passed its final gate.",
                                     "resolved_at": timestamp, "resolved_by": actor(args.actor),
                                     "references": receipt["evidence"]}
        else:
            next_stage = entering_stage
            updated["current_stage"] = next_stage
            next_item = updated["stages"][current_index + 1]
            next_item["status"] = "active"
            next_item["started_at"] = timestamp
            next_action = {"description": f"Satisfy the {stages[next_stage]['exit_gate']} exit gate.",
                           "owner": next_item["owner"], "target_type": "stage", "target_id": next_stage}
            next_item["next_action"] = copy.deepcopy(next_action)
            updated["next_action"] = next_action
            outcome_index = next(index for index, node in enumerate(updated_map["nodes"])
                                 if node["node_id"] == updated_map["desired_outcome_node_id"])
            updated_map["nodes"][outcome_index]["next_action"] = copy.deepcopy(next_action)
            updated_map["updated_at"] = timestamp
        updated["state_revision"] = new_revision
        updated["latest_event_id"] = eid
        updated["updated_at"] = timestamp
        new_proof_ids = list(dict.fromkeys([*updated.get("proof_ids", []), *(item["proof_id"] for item in proofs)]))
        new_authorization_ids = list(dict.fromkeys([*updated.get("authorization_ids", []), *(item["authorization_id"] for item in authorizations)]))
        updated["proof_ids"] = new_proof_ids
        updated["authorization_ids"] = new_authorization_ids
        changes: list[dict[str, Any]] = []
        for pointer in (f"/stages/{current_index}/status", f"/stages/{current_index}/completed_at", f"/stages/{current_index}/next_action"):
            changes.append(change("work", args.work_id, pointer, get_pointer(state, pointer), get_pointer(updated, pointer)))
        if not destination_complete:
            for pointer in (f"/stages/{current_index + 1}/status", f"/stages/{current_index + 1}/started_at", f"/stages/{current_index + 1}/next_action", "/current_stage", "/next_action"):
                changes.append(change("work", args.work_id, pointer, get_pointer(state, pointer), get_pointer(updated, pointer)))
            for pointer in (f"/nodes/{outcome_index}/next_action", "/updated_at"):
                changes.append(change("map", map_record["map_id"], pointer, get_pointer(map_record, pointer), get_pointer(updated_map, pointer)))
        else:
            updated_map["updated_at"] = timestamp
            for pointer in ("/status", "/next_action", "/completion"):
                changes.append(change("work", args.work_id, pointer, get_pointer(state, pointer), get_pointer(updated, pointer)))
            outcome_index = next(index for index, node in enumerate(map_record["nodes"]) if node["node_id"] == map_record["desired_outcome_node_id"])
            for pointer in (f"/nodes/{outcome_index}/status", f"/nodes/{outcome_index}/next_action", f"/nodes/{outcome_index}/resolution", "/updated_at"):
                changes.append(change("map", map_record["map_id"], pointer, get_pointer(map_record, pointer), get_pointer(updated_map, pointer)))
        for pointer in ("/state_revision", "/latest_event_id", "/updated_at"):
            changes.append(change("work", args.work_id, pointer, get_pointer(state, pointer), get_pointer(updated, pointer)))
        for pointer in ("/proof_ids", "/authorization_ids"):
            if get_pointer(state, pointer) != get_pointer(updated, pointer):
                changes.append(change("work", args.work_id, pointer, get_pointer(state, pointer), get_pointer(updated, pointer)))
        event = make_event(args.work_id, new_revision, "stage-completed", args.actor, args.idempotency_key, fp_input, changes, f"Complete stage {state['current_stage']}.", receipt)
        validate_record(updated, "advanced state")
        validate_record(updated_map, "advanced map")
        validate_record(event, "advanced event")
        new_events = events + [event]
        folder = store.work_dir(args.work_id)
        writes = {folder / "state.json": encode_json(updated), folder / "map.json": encode_json(updated_map),
                  folder / "events.jsonl": encode_events(new_events)}
        for record, id_field in [*((item, "proof_id") for item in proofs), *((item, "authorization_id") for item in authorizations)]:
            record_path = folder / "records" / f"{record[id_field]}.json"
            if record_path.exists():
                fail(load_json(record_path) == record, f"record ID already exists with different content: {record[id_field]}")
            writes[record_path] = encode_json(record)
        store.transaction(writes)
        return {"result": "advanced", **summary(updated, updated_map, store=store)}


def read_command(args: argparse.Namespace, store: Store, command: str) -> dict[str, Any]:
    work_id = active_work(store, args.work_id)
    with store.locked():
        folder = store.work_dir(work_id)
        intake_path = folder / "intake.json"
        if intake_path.is_file() and not (folder / "events.jsonl").exists():
            fail(command != "replay", "pre-start intake has no event journal to replay; start the finalized route first")
            intake = load_json(intake_path)
            validate_intake(intake)
            routing = None
            history: list[tuple[dict[str, Any], Path]] = []
            if (folder / "routing.json").is_file():
                routing, _, history = current_routing(store, work_id, intake)
            if command == "resume" and args.work_id:
                store.transaction({store.root / "active-work.json": encode_json({"work_id": work_id})})
            view = routing_summary(routing, history) if routing is not None else intake_summary(intake)
            view["result"] = "resumed" if command == "resume" else "projected"
            if command == "next":
                result = copy.deepcopy(view)
                result["result"] = "projected"
                result["claim_boundary"] = result.pop("projection_boundary")
                return result
            return view
        state, map_record, events = checked_checkpoint(store, work_id)
        routing = None
        if (folder / "routing.json").is_file():
            routing, _, _ = current_routing(store, work_id, load_json(intake_path))
        if command == "resume" and args.work_id:
            store.transaction({store.root / "active-work.json": encode_json({"work_id": work_id})})
    if command == "replay":
        return {"result": "replayed", "runtime_version": RUNTIME_VERSION,
                "event_count": len(events), "state": state, "map": map_record,
                "claim_boundary": "replay proves internal journal consistency, not real-world truth"}
    view = summary(state, map_record, routing, store)
    view["result"] = "resumed" if command == "resume" else "projected"
    if command == "next":
        result = {"result": "projected", "work_id": work_id, "state_revision": state["state_revision"],
                "next_action": state.get("next_action"), "blockers": view["blockers"],
                "human_control": view["human_control"], "frontier": view["frontier"],
                "claim_boundary": view["projection_boundary"]}
        if routing is not None:
            result["routing_profile"] = routing_profile(routing)
            result["authorization_boundary"] = copy.deepcopy(routing["authorization_boundary"])
        return result
    return view


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=argparse.SUPPRESS, help="repository root (default: current directory)")
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="emit deterministic JSON")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Workbench event-sourced control-plane runtime")
    root.add_argument("--repo", default=".", help="repository root (default: current directory)")
    root.add_argument("--json", action="store_true", help="emit deterministic JSON")
    commands = root.add_subparsers(dest="command", required=True)
    intake_p = commands.add_parser("capture-intake"); add_common(intake_p)
    intake_p.add_argument("--work-id", required=True)
    intake_p.add_argument("--request", required=True)
    intake_p.add_argument("--reference", action="append", default=[])
    intake_p.add_argument("--idempotency-key", required=True)
    intake_p.add_argument("--owner", default="user:local")
    finalize_p = commands.add_parser("finalize-intake"); add_common(finalize_p)
    finalize_p.add_argument("--work-id", required=True)
    finalize_p.add_argument("--routing-input", required=True,
                            help="JSON file containing the synthesized routing fields")
    finalize_p.add_argument("--idempotency-key", required=True)
    finalize_p.add_argument("--owner", default="user:local")
    revise_p = commands.add_parser("revise-routing"); add_common(revise_p)
    revise_p.add_argument("--work-id", required=True)
    revise_p.add_argument("--routing-input", required=True,
                          help="JSON file containing the full updated routing fields plus revision_reason and resolved_questions")
    revise_p.add_argument("--expected-routing-revision", required=True, type=int)
    revise_p.add_argument("--idempotency-key", required=True)
    revise_p.add_argument("--owner", default="user:local")
    begin_p = commands.add_parser("route-and-start"); add_common(begin_p)
    begin_p.add_argument("--work-id", required=True)
    begin_p.add_argument("--routing-input", required=True,
                         help="JSON file containing the synthesized routing fields")
    begin_p.add_argument("--idempotency-key", required=True)
    begin_p.add_argument("--owner", default="user:local")
    start_p = commands.add_parser("start"); add_common(start_p)
    start_p.add_argument("--work-id", required=True); start_p.add_argument("--title")
    start_p.add_argument("--outcome"); start_p.add_argument("--route")
    start_p.add_argument("--destination"); start_p.add_argument("--idempotency-key", required=True)
    start_p.add_argument("--owner")
    source = start_p.add_mutually_exclusive_group()
    source.add_argument("--from-intake", action="store_true",
                        help="bind this legacy routed start to the captured intake with the same work ID")
    source.add_argument("--from-routing", action="store_true",
                        help="bind this routed start to the finalized receipt and captured intake")
    for name in ("resume", "status", "next", "replay"):
        item = commands.add_parser(name); add_common(item); item.add_argument("--work-id")
    advance_p = commands.add_parser("advance-stage"); add_common(advance_p)
    advance_p.add_argument("--work-id", required=True)
    evidence_source = advance_p.add_mutually_exclusive_group(required=True)
    evidence_source.add_argument("--gate-receipt")
    evidence_source.add_argument("--accepted-handoff",
                                 help="registered handoff ID used to construct the gate receipt")
    advance_p.add_argument("--idempotency-key", required=True); advance_p.add_argument("--expected-revision", type=int)
    advance_p.add_argument("--actor", default="user:local")
    handoff_p = commands.add_parser("accept-handoff"); add_common(handoff_p)
    handoff_p.add_argument("--work-id", required=True)
    handoff_p.add_argument("--handoff-bundle", required=True,
                           help="JSON bundle containing one handoff and its produced records")
    handoff_p.add_argument("--idempotency-key", required=True)
    handoff_p.add_argument("--expected-revision", type=int)
    handoff_p.add_argument("--actor", default="agent:workbench")
    return root


def text_output(result: dict[str, Any]) -> str:
    if "routing_revision" in result and result.get("state_revision") == 0:
        next_action = (result.get("next_action") or {}).get("description", "none")
        return (f"{result['result']}: {result['work_id']} routing revision "
                f"{result['routing_revision']} — {result['status']}; next: {next_action}")
    if "current_stage" in result:
        next_action = (result.get("next_action") or {}).get("description", "none")
        return (f"{result['result']}: {result['work_id']} revision {result['state_revision']} — "
                f"{result['status']} at {result['current_stage']}; next: {next_action}")
    if result.get("result") == "replayed":
        return f"replayed {result['event_count']} event(s) for {result['state']['work_id']}"
    next_action = (result.get("next_action") or {}).get("description", "none")
    return f"next for {result['work_id']} at revision {result['state_revision']}: {next_action}"


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    store = Store(Path(args.repo))
    try:
        routes, stages, destinations, phases = lifecycle()
        if args.command == "capture-intake":
            result = capture_intake(args, store)
        elif args.command == "finalize-intake":
            result = finalize_intake(args, store, routes, destinations, phases)
        elif args.command == "revise-routing":
            result = revise_routing(args, store, routes, destinations, phases)
        elif args.command == "route-and-start":
            result = route_and_start(args, store, routes, stages, destinations, phases)
        elif args.command == "start":
            result = start(args, store, routes, stages, destinations)
        elif args.command == "advance-stage":
            result = advance(args, store, routes, stages, destinations)
        elif args.command == "accept-handoff":
            result = accept_handoff(args, store)
        else:
            result = read_command(args, store, args.command)
    except (WorkbenchError, OSError) as exc:
        error = {"error": str(exc), "command": args.command}
        if getattr(args, "json", False):
            print(json.dumps(error, sort_keys=True))
        else:
            print(f"Workbench refused {args.command}: {exc}", file=sys.stderr)
        return 2
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(text_output(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
