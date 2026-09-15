"""Black-box harness for the Workbench command-line contract.

The harness intentionally imports no Workbench implementation modules.  Its
only seams are subprocess exit/output and the documented file-backed records.
CLI spelling is discovered from help so behavior tests do not depend on one
reasonable choice of long-option name.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import pytest

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover - exercised only in a minimal test environment
    Draft202012Validator = None
    FormatChecker = None
    Registry = None
    Resource = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = Path(os.environ.get(
    "WORKBENCH_CLI_PATH",
    PROJECT_ROOT
    / "skills"
    / "workbench"
    / "scripts"
    / "workbench.py",
))
BUNDLED_SCHEMAS = CLI_PATH.parent.parent / "references" / "schemas"


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str
    stderr: str
    command: tuple[str, ...]

    @property
    def output(self) -> str:
        return f"{self.stdout}\n{self.stderr}".strip()


class WorkbenchCLI:
    """Adapt harmless CLI naming differences while preserving strict behavior."""

    commands = (
        "capture-intake",
        "finalize-intake",
        "revise-routing",
        "route-and-start",
        "start",
        "resume",
        "status",
        "next",
        "advance-stage",
        "accept-handoff",
        "replay",
    )

    def __init__(self, cli_path: Path) -> None:
        if not cli_path.is_file():
            pytest.fail(f"interface mismatch: Workbench CLI is missing at {cli_path}")
        self.cli_path = cli_path
        self.root_help = self._help(("--help",))
        self.command_help = {
            command: self._help((command, "--help")) for command in self.commands
        }
        missing = [name for name in self.commands if name not in self.root_help]
        if missing:
            pytest.fail(
                "interface mismatch: root help does not expose required commands: "
                + ", ".join(missing)
            )
        if "--repo" not in self.root_help and not all(
            "--repo" in help_text for help_text in self.command_help.values()
        ):
            pytest.fail("interface mismatch: help does not expose the required --repo option")
        self.repo_is_global = "--repo" in self.root_help

    def _raw(
        self,
        args: Iterable[str],
        *,
        cwd: Path | None = None,
    ) -> Result:
        command = (sys.executable, str(self.cli_path), *tuple(args))
        completed = subprocess.run(
            command,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
        return Result(
            completed.returncode,
            completed.stdout,
            completed.stderr,
            command,
        )

    def _help(self, args: tuple[str, ...]) -> str:
        result = self._raw(args)
        if result.returncode != 0:
            pytest.fail(
                "interface mismatch: help probe failed\n"
                f"command: {' '.join(result.command)}\n{result.output}"
            )
        return result.output

    def option(
        self,
        command: str,
        aliases: tuple[str, ...],
        *,
        required: bool,
    ) -> str | None:
        help_text = self.command_help[command]
        for alias in aliases:
            if re.search(rf"(?<![\w-]){re.escape(alias)}(?![\w-])", help_text):
                return alias
        if required:
            pytest.fail(
                f"interface mismatch: {command} help exposes none of "
                + ", ".join(aliases)
            )
        return None

    def invoke(
        self,
        command: str,
        repo: Path,
        args: Iterable[str] = (),
        *,
        cwd: Path | None = None,
    ) -> Result:
        tail = tuple(args)
        if self.repo_is_global:
            command_args = ("--repo", str(repo), command, *tail)
        else:
            command_args = (command, "--repo", str(repo), *tail)
        return self._raw(command_args, cwd=cwd)

    def start(
        self,
        repo: Path,
        *,
        route: str = "brownfield-feature",
        destination: str = "locally-verified-implementation",
    ) -> Result:
        values = (
            (("--work-id",), "WB-RUNTIME-001", True),
            (
                ("--route", "--route-kind", "--entrance"),
                route,
                True,
            ),
            (
                ("--destination", "--planning-destination"),
                destination,
                True,
            ),
            (("--title", "--name"), "Bounded brownfield improvement", False),
            (
                ("--desired-outcome", "--outcome"),
                "Produce a locally verified implementation without claiming release.",
                False,
            ),
            (("--owner", "--owner-id"), "human:runtime-test", False),
            (
                ("--idempotency-key", "--operation-key"),
                "runtime-test:start:WB-RUNTIME-001",
                True,
            ),
        )
        args: list[str] = []
        for aliases, value, required in values:
            option = self.option("start", aliases, required=required)
            if option:
                args.extend((option, value))
        return self.invoke("start", repo, args)

    def advance(
        self,
        repo: Path,
        *,
        receipt: Path | None,
        idempotency_key: str,
        target_stage: str = "outcome-framing",
    ) -> Result:
        args: list[str] = []
        _, state = load_state(repo)
        work_option = self.option("advance-stage", ("--work-id",), required=True)
        args.extend((work_option, state["work_id"]))
        target_option = self.option(
            "advance-stage",
            ("--to-stage", "--target-stage", "--to", "--stage"),
            required=False,
        )
        if target_option:
            args.extend((target_option, target_stage))
        if receipt is not None:
            receipt_option = self.option(
                "advance-stage",
                ("--gate-receipt", "--receipt", "--gate-proof"),
                required=True,
            )
            args.extend((receipt_option, str(receipt)))
        key_option = self.option(
            "advance-stage",
            ("--idempotency-key", "--operation-key"),
            required=True,
        )
        args.extend((key_option, idempotency_key))
        actor_option = self.option(
            "advance-stage",
            ("--actor", "--actor-id"),
            required=False,
        )
        if actor_option:
            args.extend((actor_option, "agent:runtime-test"))
        return self.invoke("advance-stage", repo, args)


@pytest.fixture(scope="session")
def workbench_cli() -> WorkbenchCLI:
    return WorkbenchCLI(CLI_PATH)


def assert_succeeded(result: Result) -> None:
    assert result.returncode == 0, (
        "expected command to succeed\n"
        f"command: {' '.join(result.command)}\n{result.output}"
    )


def assert_rejected(result: Result) -> None:
    assert result.returncode != 0, (
        "expected command to reject invalid input\n"
        f"command: {' '.join(result.command)}\n{result.output}"
    )


def json_documents(repo: Path) -> list[tuple[Path, Any]]:
    documents: list[tuple[Path, Any]] = []
    for path in sorted(repo.rglob("*.json")):
        try:
            documents.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            continue
    return documents


def load_state(repo: Path) -> tuple[Path, dict[str, Any]]:
    matches = [
        (path, value)
        for path, value in json_documents(repo)
        if isinstance(value, dict) and value.get("record_type") == "workbench-state"
    ]
    assert len(matches) == 1, (
        "expected exactly one persisted workbench-state record; "
        f"found {[str(path.relative_to(repo)) for path, _ in matches]}"
    )
    return matches[0]


def persisted_bytes(repo: Path) -> dict[str, bytes]:
    return {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in sorted(repo.rglob("*"))
        if path.is_file()
    }


@lru_cache(maxsize=1)
def schema_validators() -> dict[str, Any]:
    if Draft202012Validator is None:
        pytest.skip("jsonschema and referencing are required for runtime contract checks")
    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in BUNDLED_SCHEMAS.glob("*.json")
    }
    assert schemas, f"bundled schemas are missing from {BUNDLED_SCHEMAS}"
    id_key = "$id"
    registry = Registry().with_resources(
        (schema[id_key], Resource.from_contents(schema))
        for schema in schemas.values()
    )
    validators: dict[str, Any] = {}
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(
            schema,
            registry=registry,
            format_checker=FormatChecker(),
        )
    return validators


def assert_schema_valid(value: dict[str, Any], schema_name: str) -> None:
    validators = schema_validators()
    assert schema_name in validators, f"bundled schema is missing: {schema_name}"
    errors = sorted(validators[schema_name].iter_errors(value), key=lambda error: list(error.path))
    assert not errors, "\n".join(
        f"{schema_name} at /{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in errors
    )


def assert_repo_records_schema_valid(repo: Path) -> None:
    record_schemas = {
        "workbench-routing-receipt": "workbench-routing-receipt.schema.json",
        "workbench-state": "workbench-state.schema.json",
        "workbench-map": "workbench-map.schema.json",
        "workbench-event": "workbench-event.schema.json",
        "workbench-proof": "workbench-proof.schema.json",
        "workbench-authorization": "workbench-authorization.schema.json",
    }
    seen: set[tuple[str, str]] = set()
    for path, value in json_documents(repo):
        if not isinstance(value, dict) or value.get("record_type") not in record_schemas:
            continue
        assert_schema_valid(value, record_schemas[value["record_type"]])
        seen.add((value["record_type"], str(path.relative_to(repo))))
    event_store = find_event_store(repo)
    for index, event in enumerate(event_store.read(), start=1):
        assert_schema_valid(event, "workbench-event.schema.json")
        seen.add(("workbench-event", f"event:{index}"))
    assert any(kind == "workbench-state" for kind, _ in seen)
    assert any(kind == "workbench-map" for kind, _ in seen)
    assert any(kind == "workbench-event" for kind, _ in seen)


@dataclass
class EventStore:
    paths: list[Path]
    style: str

    def read(self) -> list[dict[str, Any]]:
        if self.style == "jsonl":
            return [
                json.loads(line)
                for line in self.paths[0].read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        if self.style == "array":
            return json.loads(self.paths[0].read_text(encoding="utf-8"))
        return [json.loads(path.read_text(encoding="utf-8")) for path in self.paths]

    def write(self, events: list[dict[str, Any]]) -> None:
        if self.style == "jsonl":
            payload = "\n".join(
                json.dumps(event, sort_keys=True, separators=(",", ":")) for event in events
            )
            self.paths[0].write_text(payload + "\n", encoding="utf-8")
            return
        if self.style == "array":
            self.paths[0].write_text(
                json.dumps(events, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            return
        assert len(events) == len(self.paths)
        for path, event in zip(self.paths, events, strict=True):
            path.write_text(
                json.dumps(event, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )


def find_event_store(repo: Path) -> EventStore:
    jsonl_matches: list[Path] = []
    array_matches: list[Path] = []
    object_matches: list[Path] = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        if path.suffix == ".jsonl":
            try:
                values = [json.loads(line) for line in text.splitlines() if line.strip()]
            except json.JSONDecodeError:
                continue
            if values and all(
                isinstance(value, dict)
                and value.get("record_type") == "workbench-event"
                for value in values
            ):
                jsonl_matches.append(path)
            continue
        if path.suffix != ".json":
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and value and all(
            isinstance(item, dict) and item.get("record_type") == "workbench-event"
            for item in value
        ):
            array_matches.append(path)
        elif isinstance(value, dict) and value.get("record_type") == "workbench-event":
            object_matches.append(path)

    modes = sum(bool(group) for group in (jsonl_matches, array_matches, object_matches))
    assert modes == 1, "expected one discoverable append-only event storage convention"
    if jsonl_matches:
        assert len(jsonl_matches) == 1
        return EventStore(jsonl_matches, "jsonl")
    if array_matches:
        assert len(array_matches) == 1
        return EventStore(array_matches, "array")
    return EventStore(object_matches, "objects")


def write_gate_receipt(
    path: Path,
    state: dict[str, Any],
    *,
    stage_id: str = "intake",
    gate_id: str = "intake-recorded",
    status: str = "passed",
    proof_records: list[dict[str, Any]] | None = None,
    authorization_records: list[dict[str, Any]] | None = None,
) -> Path:
    """Write the public gate-receipt shape exercised by advance-stage."""

    value = {
        "work_id": state["work_id"],
        "state_revision": state["state_revision"],
        "stage_id": stage_id,
        "exit_gate": gate_id,
        "result": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checked_by": "agent:runtime-test",
        "evidence": [
            {
                "record_type": "work",
                "record_id": state["work_id"],
            }
        ],
    }
    if proof_records is not None:
        value["proof_records"] = proof_records
    if authorization_records is not None:
        value["authorization_records"] = authorization_records
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def started_repo(tmp_path: Path, workbench_cli: WorkbenchCLI) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert_succeeded(workbench_cli.start(repo))
    load_state(repo)
    assert_repo_records_schema_valid(repo)
    return repo


@pytest.fixture
def advanced_repo(
    started_repo: Path,
    tmp_path: Path,
    workbench_cli: WorkbenchCLI,
) -> tuple[Path, Path, tuple[str, ...]]:
    _, state = load_state(started_repo)
    receipt = write_gate_receipt(tmp_path / "passed-intake-gate.json", state)
    operation_key = "runtime-test:intake-to-outcome-framing"
    result = workbench_cli.advance(
        started_repo,
        receipt=receipt,
        idempotency_key=operation_key,
    )
    assert_succeeded(result)
    assert_repo_records_schema_valid(started_repo)
    return started_repo, receipt, tuple(result.command)
