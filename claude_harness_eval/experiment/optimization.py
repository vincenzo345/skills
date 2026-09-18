"""Resumable champion-challenger optimization for Claude harness candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import tempfile
import time
import tomllib
from typing import Any, Protocol

from .store import (
    append_event,
    digest,
    read_json,
    write_atomic,
    write_atomic_bytes,
    write_immutable,
    write_immutable_bytes,
)


SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _path_digest(path_value: str | None) -> str | None:
    if path_value is None:
        return None
    path = Path(path_value)
    if path.is_file():
        return _sha256_bytes(path.read_bytes())
    if path.is_dir():
        entries = []
        for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
            entries.append({"path": item.relative_to(path).as_posix(), "sha256": _sha256_bytes(item.read_bytes())})
        return digest(entries)
    raise ValueError(f"runtime input does not exist: {path}")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _append_event_once(path: Path, event_id: str, event: dict[str, Any]) -> None:
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                existing = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid optimization event stream: {path}") from exc
            if existing.get("event_id") == event_id:
                if existing != {"event_id": event_id, **event}:
                    raise ValueError(f"optimization event conflict: {event_id}")
                return
    append_event(path, {"event_id": event_id, **event})


@dataclass(frozen=True)
class OptimizationConfig:
    schema_version: int
    optimization_id: str
    mode: str
    prompt_file: str
    scenario_prompt_file: str
    rubric_file: str
    workspace: str | None
    claude_model: str
    claude_effort: str
    evaluator_model: str
    improver_model: str
    repetitions: int
    max_rounds: int
    max_stagnant_rounds: int
    max_total_sessions: int
    timeout_seconds: int
    max_tokens_per_run: int
    max_budget_usd_per_run: float | None
    minimum_total_gain: float
    minimum_efficiency_gain: float
    live_authorized: bool
    plugin_dir: str | None = None
    settings_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _positive_int(data: dict[str, Any], name: str) -> int:
    value = data.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def load_optimization_config(path: Path | str) -> OptimizationConfig:
    source = Path(path).resolve()
    with source.open("rb") as stream:
        data = tomllib.load(stream)
    allowed = {
        "schema_version", "optimization_id", "mode", "prompt_file",
        "scenario_prompt_file", "rubric_file", "workspace", "claude_model",
        "claude_effort", "evaluator_model", "improver_model", "repetitions",
        "max_rounds", "max_stagnant_rounds", "max_total_sessions",
        "timeout_seconds", "max_tokens_per_run", "max_budget_usd_per_run",
        "minimum_total_gain", "minimum_efficiency_gain", "live_authorized",
        "plugin_dir", "settings_file",
    }
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"unknown optimization fields: {', '.join(unknown)}")
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if data.get("mode") not in {"fake", "live"}:
        raise ValueError("mode must be fake or live")
    for name in ("optimization_id", "prompt_file", "scenario_prompt_file", "rubric_file"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"{name} must be a nonempty string")
    for name in ("claude_model", "claude_effort", "evaluator_model", "improver_model"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"{name} must be a nonempty string")
    for name in ("minimum_total_gain", "minimum_efficiency_gain"):
        if not isinstance(data.get(name), (int, float)) or isinstance(data.get(name), bool) or data[name] < 0:
            raise ValueError(f"{name} must be a nonnegative number")

    def resolved(name: str, *, required: bool = False) -> str | None:
        value = data.get(name)
        if value is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a nonempty path")
        return str((source.parent / value).resolve())

    prompt_file = resolved("prompt_file", required=True)
    scenario_prompt_file = resolved("scenario_prompt_file", required=True)
    rubric_file = resolved("rubric_file", required=True)
    for label, value in (("prompt_file", prompt_file), ("scenario_prompt_file", scenario_prompt_file), ("rubric_file", rubric_file)):
        if not Path(value or "").is_file():
            raise ValueError(f"{label} does not exist")
    workspace = resolved("workspace")
    max_budget = data.get("max_budget_usd_per_run")
    if max_budget is not None and (
        not isinstance(max_budget, (int, float)) or isinstance(max_budget, bool) or max_budget <= 0
    ):
        raise ValueError("max_budget_usd_per_run must be a positive number")
    live_authorized = data.get("live_authorized", False)
    if data["mode"] == "live":
        if live_authorized is not True:
            raise ValueError("live mode requires live_authorized = true")
        if workspace is None or not Path(workspace).is_dir():
            raise ValueError("live mode requires an existing disposable workspace")
        marker_path = Path(workspace) / ".harness-scenario.json"
        if not marker_path.is_file():
            raise ValueError("live workspace must contain .harness-scenario.json")
        try:
            marker = json.loads(marker_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("live workspace marker must be valid JSON") from exc
        if marker.get("schema_version") != 1 or marker.get("secret_scrubbed") is not True or not isinstance(marker.get("fixture_id"), str):
            raise ValueError("live workspace marker must identify a schema-v1 secret-scrubbed fixture")
        settings_path = resolved("settings_file")
        if settings_path is None:
            raise ValueError("live mode requires an explicit settings_file")
        if not Path(settings_path).is_file():
            raise ValueError("live settings_file does not exist")
        plugin_path = resolved("plugin_dir")
        if plugin_path is not None and not Path(plugin_path).is_dir():
            raise ValueError("plugin_dir must be an existing directory")
        if max_budget is None:
            raise ValueError("live mode requires max_budget_usd_per_run")
    return OptimizationConfig(
        schema_version=1,
        optimization_id=data["optimization_id"],
        mode=data["mode"],
        prompt_file=prompt_file or "",
        scenario_prompt_file=scenario_prompt_file or "",
        rubric_file=rubric_file or "",
        workspace=workspace,
        claude_model=data["claude_model"],
        claude_effort=data["claude_effort"],
        evaluator_model=data["evaluator_model"],
        improver_model=data["improver_model"],
        repetitions=_positive_int(data, "repetitions"),
        max_rounds=_positive_int(data, "max_rounds"),
        max_stagnant_rounds=_positive_int(data, "max_stagnant_rounds"),
        max_total_sessions=_positive_int(data, "max_total_sessions"),
        timeout_seconds=_positive_int(data, "timeout_seconds"),
        max_tokens_per_run=_positive_int(data, "max_tokens_per_run"),
        max_budget_usd_per_run=float(max_budget) if max_budget is not None else None,
        minimum_total_gain=float(data["minimum_total_gain"]),
        minimum_efficiency_gain=float(data["minimum_efficiency_gain"]),
        live_authorized=live_authorized is True,
        plugin_dir=resolved("plugin_dir"),
        settings_file=resolved("settings_file"),
    )


def load_rubric(path: Path | str) -> dict[str, Any]:
    value = read_json(Path(path))
    if value.get("schema_version") != 1 or not isinstance(value.get("rubric_id"), str):
        raise ValueError("rubric must have schema_version 1 and rubric_id")
    dimensions = value.get("dimensions")
    if not isinstance(dimensions, dict) or not dimensions:
        raise ValueError("rubric dimensions must be a nonempty object")
    weight = 0.0
    for name, item in dimensions.items():
        if not isinstance(name, str) or not isinstance(item, dict):
            raise ValueError("rubric dimension entries are invalid")
        if not isinstance(item.get("weight"), (int, float)) or item["weight"] <= 0:
            raise ValueError(f"rubric dimension {name} has invalid weight")
        if not isinstance(item.get("minimum"), (int, float)):
            raise ValueError(f"rubric dimension {name} has invalid minimum")
        if not 0 <= float(item["minimum"]) <= 5:
            raise ValueError(f"rubric dimension {name} minimum must be within the 0-5 scale")
        weight += float(item["weight"])
    if abs(weight - 1.0) > 1e-6:
        raise ValueError("rubric dimension weights must sum to 1")
    gates = value.get("hard_gates", [])
    if not isinstance(gates, list):
        raise ValueError("rubric hard_gates must be an array")
    for gate in gates:
        if not isinstance(gate, dict) or gate.get("kind") not in {"contains", "forbid", "order"}:
            raise ValueError("rubric hard gate is invalid")
        if not isinstance(gate.get("gate_id"), str):
            raise ValueError("rubric hard gate needs gate_id")
    return value


@dataclass(frozen=True)
class CandidateProposal:
    prompt: str
    hypothesis: str
    predicted_effects: tuple[str, ...]
    risks: tuple[str, ...]


class SessionRunner(Protocol):
    def run(self, *, candidate_id: str, prompt_path: Path, attempt: int, round_number: int) -> dict[str, Any]: ...


class Evaluator(Protocol):
    def evaluate(self, *, candidate_id: str, observations: list[dict[str, Any]], rubric: dict[str, Any]) -> dict[str, Any]: ...


class Improver(Protocol):
    def improve(self, *, candidate_id: str, prompt: str, evaluation: dict[str, Any], history: list[dict[str, Any]], rubric: dict[str, Any]) -> CandidateProposal: ...


class FakeSessionRunner:
    """Zero-cost deterministic runner used to prove orchestration."""

    def run(self, *, candidate_id: str, prompt_path: Path, attempt: int, round_number: int) -> dict[str, Any]:
        index = int(candidate_id.rsplit("-", 1)[-1])
        score = min(5.0, 2.0 + index)
        transcript = _read_text(prompt_path) + f"\nFAKE candidate={candidate_id} attempt={attempt}"
        return {
            "schema_version": 1,
            "candidate_id": candidate_id,
            "attempt": attempt,
            "round": round_number,
            "status": "completed",
            "transcript": transcript,
            "suggested_scores": {"*": score},
            "metrics": {"tokens": max(1000, 4000 - index * 500), "elapsed_seconds": max(1.0, 12.0 - index)},
            "completed_at": _now(),
        }


_OPERATIONAL_FAILURE_LINE = re.compile(
    r"^\s*(?:error:\s*)?(?:Workbench refused|missing fields:|schema validation failed|"
    r"not a registered Workbench record|unregistered addendum|ralph-loop|completion_guard\.py)",
    re.IGNORECASE,
)


def _gate_transcript(transcript: str) -> str:
    """Keep agent prose and actual failure lines, excluding source-code/search echoes."""
    evidence: list[str] = []
    parsed = False

    def add_failure_lines(value: str) -> None:
        evidence.extend(line for line in value.splitlines() if _OPERATIONAL_FAILURE_LINE.search(line))

    for line in transcript.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict):
            continue
        parsed = True
        if item.get("type") == "assistant":
            for block in (item.get("message") or {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                    evidence.append(block["text"])
        elif item.get("type") == "result" and isinstance(item.get("result"), str):
            evidence.append(item["result"])
        elif item.get("type") == "user":
            for block in (item.get("message") or {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_result" and isinstance(block.get("content"), str):
                    add_failure_lines(block["content"])

        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue
        nested = payload.get("item")
        if isinstance(nested, dict) and nested.get("type") == "AgentMessage":
            for block in nested.get("content", []):
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    evidence.append(block["text"])
        elif isinstance(nested, dict) and nested.get("type") == "CommandExecution":
            for key in ("stdout", "stderr"):
                if isinstance(nested.get(key), str):
                    add_failure_lines(nested[key])
        if payload.get("type") == "message" and payload.get("role") == "assistant":
            for block in payload.get("content", []):
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    evidence.append(block["text"])
        if payload.get("type") == "task_complete" and isinstance(payload.get("last_agent_message"), str):
            evidence.append(payload["last_agent_message"])
    return "\n".join(evidence) if parsed else transcript


def _hard_gates(transcript: str, rubric: dict[str, Any]) -> dict[str, bool]:
    transcript = _gate_transcript(transcript)
    results: dict[str, bool] = {}
    for gate in rubric.get("hard_gates", []):
        kind = gate["kind"]
        if kind == "contains":
            results[gate["gate_id"]] = re.search(gate["pattern"], transcript, re.IGNORECASE | re.DOTALL) is not None
        elif kind == "forbid":
            results[gate["gate_id"]] = re.search(gate["pattern"], transcript, re.IGNORECASE | re.DOTALL) is None
        else:
            first = re.search(gate["first_pattern"], transcript, re.IGNORECASE | re.DOTALL)
            second = re.search(gate["then_pattern"], transcript, re.IGNORECASE | re.DOTALL)
            results[gate["gate_id"]] = first is not None and (
                second is None or first.start() < second.start()
            )
    return results


def _aggregate_metrics(observations: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "median_tokens": float(statistics.median(float(item["metrics"]["tokens"]) for item in observations)),
        "median_elapsed_seconds": float(statistics.median(float(item["metrics"]["elapsed_seconds"]) for item in observations)),
    }


def _weighted_total(scores: dict[str, float], rubric: dict[str, Any]) -> float:
    return sum(float(scores[name]) * float(item["weight"]) for name, item in rubric["dimensions"].items())


class FakeEvaluator:
    def evaluate(self, *, candidate_id: str, observations: list[dict[str, Any]], rubric: dict[str, Any]) -> dict[str, Any]:
        default = float(observations[0].get("suggested_scores", {}).get("*", 0.0))
        scores = {name: default for name in rubric["dimensions"]}
        transcript = "\n".join(item.get("transcript", "") for item in observations)
        gates = _hard_gates(transcript, rubric)
        return {
            "schema_version": 1,
            "candidate_id": candidate_id,
            "hard_gates": gates,
            "dimensions": {name: {"score": score, "evidence": ["deterministic fake observation"]} for name, score in scores.items()},
            "weighted_total": _weighted_total(scores, rubric),
            "metrics": _aggregate_metrics(observations),
            "evaluated_at": _now(),
        }


class FakeImprover:
    def improve(self, *, candidate_id: str, prompt: str, evaluation: dict[str, Any], history: list[dict[str, Any]], rubric: dict[str, Any]) -> CandidateProposal:
        number = len(history) + 1
        return CandidateProposal(
            prompt=prompt.rstrip() + f"\n\n# Candidate refinement {number}\nResolve the failed rubric evidence without regressing established behavior.\n",
            hypothesis=f"A targeted refinement in round {number} improves the weakest rubric evidence.",
            predicted_effects=("increase the lowest score", "reduce unnecessary work"),
            risks=("additional instruction text may increase prompt cost",),
        )


def _json_lines_metrics(output: str) -> tuple[int, str]:
    # Claude's terminal `result.usage` is cumulative across every cached API
    # turn. That is useful for billing, but it is not the per-session context
    # footprint used by this rubric's token ceiling and grows quadratically with
    # tool calls. Measure the largest individual assistant request instead.
    assistant_tokens = 0
    fallback_tokens = 0
    texts: list[str] = []

    def usage_total(value: Any) -> int:
        if isinstance(value, list):
            return max((usage_total(item) for item in value), default=0)
        if not isinstance(value, dict):
            return 0
        direct = sum(
            int(value.get(key, 0) or 0)
            for key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
            if isinstance(value.get(key, 0), (int, float))
        )
        return max(direct, max((usage_total(item) for item in value.values()), default=0))

    for line in output.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            if item.get("type") == "assistant" and isinstance(item.get("message"), dict):
                assistant_tokens = max(assistant_tokens, usage_total(item["message"].get("usage", {})))
            else:
                fallback_tokens = max(fallback_tokens, usage_total(item))
            text = item.get("result") or item.get("text")
            if isinstance(text, str):
                texts.append(text)
    return assistant_tokens or fallback_tokens, "\n".join(texts)


class ClaudeSessionRunner:
    def __init__(self, config: OptimizationConfig, scenario_prompt: str):
        self.config = config
        self.scenario_prompt = scenario_prompt

    def command(self, prompt_path: Path) -> list[str]:
        command = [
            "claude", "-p", "--output-format", "stream-json", "--verbose",
            "--include-hook-events", "--setting-sources", "project",
            "--model", self.config.claude_model, "--effort", self.config.claude_effort,
            "--append-system-prompt-file", str(prompt_path), "--permission-mode", "bypassPermissions",
            "--dangerously-skip-permissions", "--permission-prompts", "none",
        ]
        if self.config.max_budget_usd_per_run is not None:
            command.extend(["--max-budget-usd", str(self.config.max_budget_usd_per_run)])
        if self.config.settings_file:
            command.extend(["--settings", self.config.settings_file])
        if self.config.plugin_dir:
            command.extend(["--plugin-dir", self.config.plugin_dir])
        command.append(self.scenario_prompt)
        return command

    def run(self, *, candidate_id: str, prompt_path: Path, attempt: int, round_number: int) -> dict[str, Any]:
        run_root = prompt_path.parent / "runs"
        workspace = run_root / f"attempt-{attempt:02d}-workspace"
        if workspace.exists():
            raise ValueError(f"incomplete candidate workspace already exists: {workspace}")
        shutil.copytree(Path(self.config.workspace or ""), workspace)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                self.command(prompt_path), cwd=workspace, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=self.config.timeout_seconds,
                check=False,
            )
            timed_out = False
            stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            exit_code = -9
        elapsed = time.monotonic() - started
        tokens, result_text = _json_lines_metrics(stdout)
        status = "completed" if exit_code == 0 and not timed_out and 0 < tokens <= self.config.max_tokens_per_run else "failed"
        workbench_records: dict[str, Any] = {}
        workbench_root = workspace / ".workbench"
        if workbench_root.exists():
            for path in sorted(workbench_root.rglob("*.json")):
                if path.name not in {"state.json", "routing.json", "active-work.json"}:
                    continue
                try:
                    workbench_records[path.relative_to(workspace).as_posix()] = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    workbench_records[path.relative_to(workspace).as_posix()] = {"invalid_json": True}
        return {
            "schema_version": 1, "candidate_id": candidate_id, "attempt": attempt,
            "round": round_number, "status": status, "exit_code": exit_code,
            "timed_out": timed_out, "transcript": stdout, "stderr": stderr,
            "result_text": result_text,
            "workspace_evidence": {
                "fixture_sha256": _path_digest(self.config.workspace),
                "result_sha256": _path_digest(str(workspace)),
                "workbench_records": workbench_records,
                "workspace": str(workspace),
            },
            "metrics": {"tokens": tokens, "elapsed_seconds": elapsed}, "completed_at": _now(),
        }


def _evaluation_schema(dimension_names: list[str]) -> dict[str, Any]:
    score_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["score", "evidence"],
        "properties": {
            "score": {"type": "number"},
            "evidence": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["dimensions"],
        "properties": {
            "dimensions": {
                "type": "object",
                "additionalProperties": False,
                "required": dimension_names,
                "properties": {name: score_schema for name in dimension_names},
            },
        },
    }


_IMPROVEMENT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["prompt", "hypothesis", "predicted_effects", "risks"],
    "properties": {
        "prompt": {"type": "string"}, "hypothesis": {"type": "string"},
        "predicted_effects": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
    },
}


def _codex_structured(model: str, prompt: str, schema: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    codex_executable = shutil.which("codex")
    if codex_executable is None:
        raise ValueError("Codex executable was not found on PATH")
    with tempfile.TemporaryDirectory(prefix="harness-codex-") as temporary:
        temp = Path(temporary)
        schema_path = temp / "schema.json"
        output_path = temp / "output.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        completed = subprocess.run(
            [codex_executable, "exec", "--json", "--ephemeral", "--ignore-user-config", "--ignore-rules",
             "--sandbox", "read-only", "--skip-git-repo-check", "--model", model,
             "--cd", str(temp), "--output-schema", str(schema_path), "--output-last-message", str(output_path), "-"],
            input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_seconds, check=False,
        )
        if completed.returncode != 0 or not output_path.is_file():
            detail = (completed.stderr or completed.stdout)[-1000:]
            raise ValueError(f"Codex structured call failed with exit {completed.returncode}: {detail}")
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Codex structured call returned invalid JSON") from exc


class CodexEvaluator:
    def __init__(self, config: OptimizationConfig, root: Path):
        self.config, self.root = config, root

    def evaluate(self, *, candidate_id: str, observations: list[dict[str, Any]], rubric: dict[str, Any]) -> dict[str, Any]:
        transcript = "\n\n".join(item.get("transcript", "") for item in observations)
        workspace_evidence = [item.get("workspace_evidence", {}) for item in observations]
        gate_input = transcript + "\n" + json.dumps(workspace_evidence, ensure_ascii=False)
        gates = _hard_gates(gate_input, rubric)
        if len(transcript) > 250_000:
            transcript = transcript[:75_000] + "\n\n[... bounded middle omitted ...]\n\n" + transcript[-175_000:]
        request = {
            "instruction": "Blindly grade the candidate transcript against every supplied dimension. Use only transcript evidence. Return the required JSON and no prose.",
            "rubric_dimensions": rubric["dimensions"],
            "transcript": transcript,
            "workspace_evidence": workspace_evidence,
        }
        judged = _codex_structured(
            self.config.evaluator_model,
            json.dumps(request),
            _evaluation_schema(sorted(rubric["dimensions"])),
            self.config.timeout_seconds,
        )
        names = set(rubric["dimensions"])
        if set(judged.get("dimensions", {})) != names:
            raise ValueError("evaluator did not return every frozen rubric dimension")
        scores = {name: float(judged["dimensions"][name]["score"]) for name in names}
        if any(score < 0 or score > 5 for score in scores.values()):
            raise ValueError("evaluator returned a score outside the frozen 0-5 scale")
        return {
            "schema_version": 1, "candidate_id": candidate_id, "hard_gates": gates,
            "dimensions": judged["dimensions"], "weighted_total": _weighted_total(scores, rubric),
            "metrics": _aggregate_metrics(observations), "evaluated_at": _now(),
        }


class CodexImprover:
    def __init__(self, config: OptimizationConfig, root: Path):
        self.config, self.root = config, root

    def improve(self, *, candidate_id: str, prompt: str, evaluation: dict[str, Any], history: list[dict[str, Any]], rubric: dict[str, Any]) -> CandidateProposal:
        request = {
            "instruction": "Produce one targeted revision of the Claude harness prompt. Change only prompt text. Address failed or weakest grading evidence without weakening stronger dimensions. Do not generate executable hook code. Return the required JSON and no prose.",
            "incumbent_id": candidate_id, "incumbent_prompt": prompt,
            "evaluation": evaluation, "prior_decisions": history, "rubric_dimensions": rubric["dimensions"],
        }
        value = _codex_structured(self.config.improver_model, json.dumps(request), _IMPROVEMENT_SCHEMA, self.config.timeout_seconds)
        if not value["prompt"].strip() or value["prompt"] == prompt:
            raise ValueError("improver returned an empty or unchanged prompt")
        return CandidateProposal(value["prompt"], value["hypothesis"], tuple(value["predicted_effects"]), tuple(value["risks"]))


def _write_record(path: Path, value: dict[str, Any]) -> None:
    write_immutable(path, value)
    payload = path.read_bytes()
    write_immutable_bytes(path.with_suffix(path.suffix + ".sha256"), (_sha256_bytes(payload) + "\n").encode("ascii"))


def _read_record(path: Path) -> dict[str, Any]:
    digest_path = path.with_suffix(path.suffix + ".sha256")
    if not path.is_file() or not digest_path.is_file():
        raise ValueError(f"missing evidenced record: {path}")
    if _sha256_bytes(path.read_bytes()) != digest_path.read_text(encoding="ascii").strip():
        raise ValueError(f"record digest mismatch: {path}")
    return read_json(path)


def _candidate_id(number: int) -> str:
    return f"CAND-{number:03d}"


def _candidate_root(root: Path, candidate_id: str) -> Path:
    return root / "candidates" / candidate_id


def _write_candidate(root: Path, candidate_id: str, proposal: CandidateProposal, parent: str | None) -> None:
    destination = _candidate_root(root, candidate_id)
    prompt = proposal.prompt.encode("utf-8")
    write_immutable_bytes(destination / "prompt.md", prompt)
    write_immutable_bytes(destination / "prompt.sha256", (_sha256_bytes(prompt) + "\n").encode("ascii"))
    _write_record(destination / "candidate.json", {
        "schema_version": 1, "candidate_id": candidate_id, "parent_candidate_id": parent,
        "prompt_sha256": _sha256_bytes(prompt), "hypothesis": proposal.hypothesis,
        "predicted_effects": list(proposal.predicted_effects), "risks": list(proposal.risks),
        "created_at": _now(),
    })


def _read_candidate_prompt(root: Path, candidate_id: str) -> str:
    destination = _candidate_root(root, candidate_id)
    _read_record(destination / "candidate.json")
    payload = (destination / "prompt.md").read_bytes()
    expected = (destination / "prompt.sha256").read_text(encoding="ascii").strip()
    if _sha256_bytes(payload) != expected:
        raise ValueError(f"candidate prompt digest mismatch: {candidate_id}")
    return payload.decode("utf-8")


def _validate_optimization_artifacts(root: Path) -> None:
    candidates_root = root / "candidates"
    if candidates_root.exists():
        for candidate in sorted(candidates_root.glob("CAND-*")):
            _read_candidate_prompt(root, candidate.name)
            evaluation = candidate / "evaluation.json"
            if evaluation.exists():
                _read_record(evaluation)
            runs = candidate / "runs"
            if runs.exists():
                for result in sorted(runs.glob("attempt-*.json")):
                    record = _read_record(result)
                    evidence = record.get("workspace_evidence")
                    if isinstance(evidence, dict) and evidence.get("workspace"):
                        workspace = Path(evidence["workspace"])
                        if not workspace.is_dir() or _path_digest(str(workspace)) != evidence.get("result_sha256"):
                            raise ValueError(f"candidate workspace digest mismatch: {workspace}")
    rounds_root = root / "rounds"
    if rounds_root.exists():
        for decision in sorted(rounds_root.glob("round-*/decision.json")):
            _read_record(decision)


def initialize_optimization(config: OptimizationConfig, root: Path | str) -> dict[str, Any]:
    destination = Path(root).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    prompt = Path(config.prompt_file).read_bytes()
    scenario = Path(config.scenario_prompt_file).read_bytes()
    rubric = Path(config.rubric_file).read_bytes()
    manifest = {
        "schema_version": 1, "optimization_id": config.optimization_id,
        "experiment_id": f"{config.optimization_id}-{digest(config.to_dict())[:12]}",
        "config": config.to_dict(), "prompt_sha256": _sha256_bytes(prompt),
        "scenario_prompt_sha256": _sha256_bytes(scenario), "rubric_sha256": _sha256_bytes(rubric),
        "runtime_input_digests": {
            "settings": _path_digest(config.settings_file),
            "plugin": _path_digest(config.plugin_dir),
            "workspace_marker": _path_digest(str(Path(config.workspace) / ".harness-scenario.json")) if config.workspace else None,
            "workspace_template": _path_digest(config.workspace),
        },
    }
    write_immutable(destination / "manifest.json", manifest)
    _write_candidate(destination, _candidate_id(0), CandidateProposal(prompt.decode("utf-8"), "baseline", (), ()), None)
    state_path = destination / "state.json"
    if not state_path.exists():
        write_atomic(state_path, {
            "schema_version": 1, "status": "ready", "champion_id": _candidate_id(0),
            "next_round": 1, "sessions_used": 0, "stagnant_rounds": 0,
            "completed_rounds": [], "stop_reason": None,
        })
        _append_event_once(destination / "events.jsonl", "optimization.initialized", {"type": "optimization.initialized", "experiment_id": manifest["experiment_id"]})
    return {"schema_version": 1, "command": "optimize-init", "status": "ready", "experiment_id": manifest["experiment_id"], "root": str(destination)}


def _evaluation_path(root: Path, candidate_id: str) -> Path:
    return _candidate_root(root, candidate_id) / "evaluation.json"


def _run_and_evaluate(root: Path, candidate_id: str, round_number: int, config: OptimizationConfig, rubric: dict[str, Any], runner: SessionRunner, evaluator: Evaluator, state: dict[str, Any]) -> dict[str, Any]:
    candidate = _candidate_root(root, candidate_id)
    observations: list[dict[str, Any]] = []
    for attempt in range(1, config.repetitions + 1):
        result_path = candidate / "runs" / f"attempt-{attempt:02d}.json"
        if result_path.exists():
            observation = _read_record(result_path)
        else:
            if state["sessions_used"] >= config.max_total_sessions:
                state["status"], state["stop_reason"] = "blocked", "session-budget-exhausted"
                write_atomic(root / "state.json", state)
                _append_event_once(root / "events.jsonl", f"blocked.{state['stop_reason']}", {"type": "optimization.blocked", "reason": state["stop_reason"]})
                raise ValueError("optimization session budget exhausted")
            try:
                observation = runner.run(candidate_id=candidate_id, prompt_path=candidate / "prompt.md", attempt=attempt, round_number=round_number)
            except Exception as exc:
                state["status"], state["stop_reason"] = "blocked", f"session-provider-error:{type(exc).__name__}"
                write_atomic(root / "state.json", state)
                _append_event_once(root / "events.jsonl", f"blocked.{state['stop_reason']}", {"type": "optimization.blocked", "reason": state["stop_reason"]})
                raise
            _write_record(result_path, observation)
            state["sessions_used"] += 1
            write_atomic(root / "state.json", state)
            _append_event_once(root / "events.jsonl", f"session.{candidate_id}.{attempt}", {"type": "session.completed", "candidate_id": candidate_id, "attempt": attempt, "status": observation.get("status")})
        if observation.get("status") != "completed":
            state["status"], state["stop_reason"] = "blocked", f"candidate-session-failed:{candidate_id}:attempt-{attempt}"
            write_atomic(root / "state.json", state)
            _append_event_once(root / "events.jsonl", f"blocked.{state['stop_reason']}", {"type": "optimization.blocked", "reason": state["stop_reason"]})
            raise ValueError(f"candidate session failed: {candidate_id} attempt {attempt}")
        observations.append(observation)
    evaluation_path = _evaluation_path(root, candidate_id)
    if evaluation_path.exists():
        return _read_record(evaluation_path)
    try:
        evaluation = evaluator.evaluate(candidate_id=candidate_id, observations=observations, rubric=rubric)
    except Exception as exc:
        state["status"], state["stop_reason"] = "blocked", f"evaluator-error:{type(exc).__name__}"
        write_atomic(root / "state.json", state)
        _append_event_once(root / "events.jsonl", f"blocked.{state['stop_reason']}", {"type": "optimization.blocked", "reason": state["stop_reason"]})
        raise
    _write_record(evaluation_path, evaluation)
    _append_event_once(root / "events.jsonl", f"evaluation.{candidate_id}", {"type": "candidate.evaluated", "candidate_id": candidate_id, "weighted_total": evaluation["weighted_total"]})
    return evaluation


def _passes_target(evaluation: dict[str, Any], rubric: dict[str, Any]) -> bool:
    if not all(evaluation.get("hard_gates", {}).values()):
        return False
    for name, definition in rubric["dimensions"].items():
        if float(evaluation["dimensions"][name]["score"]) < float(definition["minimum"]):
            return False
    target = rubric.get("target", {})
    return (
        float(evaluation["weighted_total"]) >= float(target.get("weighted_total", 0))
        and float(evaluation["metrics"]["median_tokens"]) <= float(target.get("max_median_tokens", float("inf")))
        and float(evaluation["metrics"]["median_elapsed_seconds"]) <= float(target.get("max_median_elapsed_seconds", float("inf")))
    )


def _promotion_decision(champion: dict[str, Any], challenger: dict[str, Any], config: OptimizationConfig, rubric: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not all(challenger.get("hard_gates", {}).values()):
        reasons.append("challenger failed one or more hard gates")
    for name in rubric["dimensions"]:
        old = float(champion["dimensions"][name]["score"])
        new = float(challenger["dimensions"][name]["score"])
        if new < old:
            reasons.append(f"challenger regressed dimension {name}: {new} < {old}")
    total_gain = float(challenger["weighted_total"]) - float(champion["weighted_total"])
    token_gain = 1.0 - float(challenger["metrics"]["median_tokens"]) / max(1.0, float(champion["metrics"]["median_tokens"]))
    time_gain = 1.0 - float(challenger["metrics"]["median_elapsed_seconds"]) / max(0.001, float(champion["metrics"]["median_elapsed_seconds"]))
    if total_gain < config.minimum_total_gain and max(token_gain, time_gain) < config.minimum_efficiency_gain:
        reasons.append("challenger improved neither weighted quality nor efficiency enough")
    return not reasons, reasons


def run_optimization(root: Path | str, *, runner: SessionRunner | None = None, evaluator: Evaluator | None = None, improver: Improver | None = None) -> dict[str, Any]:
    campaign_root = Path(root).resolve()
    manifest = read_json(campaign_root / "manifest.json")
    config = OptimizationConfig(**manifest["config"])
    state_path = campaign_root / "state.json"
    state = read_json(state_path)
    _validate_optimization_artifacts(campaign_root)
    rubric_path = Path(config.rubric_file)
    if _sha256_bytes(rubric_path.read_bytes()) != manifest["rubric_sha256"]:
        raise ValueError("rubric changed after optimization initialization")
    if _sha256_bytes(Path(config.scenario_prompt_file).read_bytes()) != manifest["scenario_prompt_sha256"]:
        raise ValueError("scenario prompt changed after optimization initialization")
    actual_runtime_inputs = {
        "settings": _path_digest(config.settings_file),
        "plugin": _path_digest(config.plugin_dir),
        "workspace_marker": _path_digest(str(Path(config.workspace) / ".harness-scenario.json")) if config.workspace else None,
        "workspace_template": _path_digest(config.workspace),
    }
    if actual_runtime_inputs != manifest.get("runtime_input_digests"):
        raise ValueError("runtime inputs changed after optimization initialization")
    if state["status"] in {"completed", "stopped", "blocked"}:
        return {"schema_version": 1, "command": "optimize-run", **state}
    rubric = load_rubric(rubric_path)
    if runner is None:
        runner = FakeSessionRunner() if config.mode == "fake" else ClaudeSessionRunner(config, _read_text(Path(config.scenario_prompt_file)))
    if evaluator is None:
        evaluator = FakeEvaluator() if config.mode == "fake" else CodexEvaluator(config, campaign_root)
    if improver is None:
        improver = FakeImprover() if config.mode == "fake" else CodexImprover(config, campaign_root)
    state["status"] = "running"
    write_atomic(state_path, state)
    while state["next_round"] <= config.max_rounds:
        round_number = int(state["next_round"])
        champion_id = state["champion_id"]
        champion_eval = _run_and_evaluate(campaign_root, champion_id, round_number, config, rubric, runner, evaluator, state)
        if _passes_target(champion_eval, rubric):
            state["status"], state["stop_reason"] = "completed", "target-met"
            break
        history = [
            _read_record(campaign_root / "rounds" / f"round-{number:03d}" / "decision.json")
            for number in state["completed_rounds"]
        ]
        challenger_id = _candidate_id(round_number)
        challenger_root = _candidate_root(campaign_root, challenger_id)
        if not challenger_root.exists():
            try:
                proposal = improver.improve(
                    candidate_id=champion_id, prompt=_read_candidate_prompt(campaign_root, champion_id),
                    evaluation=champion_eval, history=history, rubric=rubric,
                )
            except Exception as exc:
                state["status"], state["stop_reason"] = "blocked", f"improver-error:{type(exc).__name__}"
                write_atomic(state_path, state)
                _append_event_once(campaign_root / "events.jsonl", f"blocked.{state['stop_reason']}", {"type": "optimization.blocked", "reason": state["stop_reason"]})
                raise
            _write_candidate(campaign_root, challenger_id, proposal, champion_id)
            _append_event_once(campaign_root / "events.jsonl", f"candidate.{challenger_id}", {"type": "candidate.created", "candidate_id": challenger_id, "parent_candidate_id": champion_id})
        challenger_eval = _run_and_evaluate(campaign_root, challenger_id, round_number, config, rubric, runner, evaluator, state)
        promoted, reasons = _promotion_decision(champion_eval, challenger_eval, config, rubric)
        decision = {
            "schema_version": 1, "round": round_number, "champion_id": champion_id,
            "challenger_id": challenger_id, "decision": "promote" if promoted else "reject",
            "reasons": reasons, "decided_at": _now(),
        }
        round_root = campaign_root / "rounds" / f"round-{round_number:03d}"
        decision_path = round_root / "decision.json"
        if decision_path.exists():
            existing = _read_record(decision_path)
            if existing["decision"] != decision["decision"] or existing["challenger_id"] != challenger_id:
                raise ValueError(f"round decision conflict: {round_number}")
            decision = existing
            promoted = decision["decision"] == "promote"
        else:
            _write_record(decision_path, decision)
        if promoted:
            state["champion_id"] = challenger_id
            state["stagnant_rounds"] = 0
        else:
            state["stagnant_rounds"] += 1
        state["completed_rounds"] = sorted(set(state["completed_rounds"] + [round_number]))
        state["next_round"] = round_number + 1
        _append_event_once(campaign_root / "events.jsonl", f"round.{round_number}", {"type": "round.completed", "round": round_number, "decision": decision["decision"], "challenger_id": challenger_id})
        if promoted and _passes_target(challenger_eval, rubric):
            state["status"], state["stop_reason"] = "completed", "target-met"
            write_atomic(state_path, state)
            break
        if state["stagnant_rounds"] >= config.max_stagnant_rounds:
            state["status"], state["stop_reason"] = "completed", "no-progress"
            write_atomic(state_path, state)
            break
        write_atomic(state_path, state)
    if state["status"] == "running":
        state["status"], state["stop_reason"] = "completed", "max-rounds"
    write_atomic(state_path, state)
    return {"schema_version": 1, "command": "optimize-run", **state}


def stop_optimization(root: Path | str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("stop reason must be nonempty")
    campaign_root = Path(root).resolve()
    state = read_json(campaign_root / "state.json")
    if state["status"] != "stopped":
        state["status"], state["stop_reason"] = "stopped", reason
        write_atomic(campaign_root / "state.json", state)
        _append_event_once(campaign_root / "events.jsonl", "optimization.stopped", {"type": "optimization.stopped", "reason": reason})
    return {"schema_version": 1, "command": "optimize-stop", **state}


def report_optimization(root: Path | str) -> dict[str, Any]:
    campaign_root = Path(root).resolve()
    _validate_optimization_artifacts(campaign_root)
    manifest = read_json(campaign_root / "manifest.json")
    state = read_json(campaign_root / "state.json")
    candidates = []
    for path in sorted((campaign_root / "candidates").glob("CAND-*/evaluation.json")):
        evaluation = _read_record(path)
        candidates.append({
            "candidate_id": evaluation["candidate_id"], "weighted_total": evaluation["weighted_total"],
            "hard_gates_passed": all(evaluation.get("hard_gates", {}).values()), "metrics": evaluation["metrics"],
        })
    result = {
        "schema_version": 1, "command": "optimize-report", "experiment_id": manifest["experiment_id"],
        "status": state["status"], "stop_reason": state["stop_reason"], "champion_id": state["champion_id"],
        "sessions_used": state["sessions_used"], "completed_rounds": state["completed_rounds"], "candidates": candidates,
    }
    reports = campaign_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_atomic(reports / "summary.json", result)
    lines = ["# Harness optimization report", "", f"Champion: `{state['champion_id']}`", f"Stop reason: `{state['stop_reason']}`", ""]
    lines.extend(f"- {item['candidate_id']}: score {item['weighted_total']:.3f}, tokens {item['metrics']['median_tokens']:.0f}, seconds {item['metrics']['median_elapsed_seconds']:.1f}" for item in candidates)
    write_atomic_bytes(reports / "report.md", ("\n".join(lines) + "\n").encode("utf-8"))
    return result
