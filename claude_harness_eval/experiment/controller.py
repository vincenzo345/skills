"""Deterministic campaign initialization, fake execution, resume, and reporting."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random

from ..runner import apply_reference, stage_task, verify_task
from .config import CampaignConfig, campaign_from_dict
from .isolation import DockerIsolationRunner, policy_from_qualification, validate_qualification
from .store import append_event, digest, read_json, write_atomic, write_atomic_bytes, write_immutable, write_immutable_bytes


SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _manifest(config: CampaignConfig) -> dict:
    normalized = config.to_dict()
    config_digest = digest(normalized)
    return {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": config.campaign_id,
        "experiment_id": f"{config.campaign_id}-{config_digest[:12]}",
        "config_sha256": config_digest,
        "config": normalized,
    }


def initialize_campaign(config: CampaignConfig, root: Path | str) -> dict:
    destination = Path(root).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    manifest = _manifest(config)
    write_immutable(destination / "manifest.json", manifest)
    state_path = destination / "state.json"
    if not state_path.exists():
        state = {"schema_version": 1, "status": "ready", "completed_run_ids": [], "stop_reason": None}
        write_atomic(state_path, state)
        append_event(destination / "events.jsonl", {"type": "campaign.initialized", "experiment_id": manifest["experiment_id"]})
    return {"schema_version": 1, "command": "experiment-init", "status": "ready", "experiment_id": manifest["experiment_id"], "root": str(destination)}


def _run_id(experiment_id: str, agent: str, task_id: str, attempt: int) -> str:
    return digest({"experiment_id": experiment_id, "agent": agent, "task_id": task_id, "attempt": attempt})[:24]


def _schedule(manifest: dict) -> list[dict]:
    config = campaign_from_dict(manifest["config"])
    cells = [
        {"agent": agent, "task_id": task_id, "attempt": attempt}
        for attempt in range(1, config.repetitions + 1)
        for task_id in config.task_ids
        for agent in sorted(config.agents)
    ]
    random.Random(config.seed).shuffle(cells)
    for cell in cells:
        cell["run_id"] = _run_id(manifest["experiment_id"], **cell)
    return cells


def _read_run_result(run_root: Path, *, repair_missing_digest: bool = False) -> dict:
    result_path = run_root / "result.json"
    payload = result_path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    digest_path = run_root / "result.sha256"
    if not digest_path.exists():
        if not repair_missing_digest:
            raise ValueError(f"missing result digest: {run_root.name}")
        write_immutable_bytes(digest_path, (actual + "\n").encode("ascii"))
    expected = digest_path.read_text(encoding="ascii").strip()
    if actual != expected:
        raise ValueError(f"result digest mismatch: {run_root.name}")
    return json.loads(payload)


def validate_campaign_isolation(config: CampaignConfig, *, isolation_runner: object | None = None) -> dict:
    if config.mode != "live":
        raise ValueError("campaign is not configured for live mode")
    qualification = Path(config.qualification_file or "")
    record_path = qualification if qualification.name == "qualification.json" else qualification / "qualification.json"
    if not record_path.is_file():
        raise ValueError("configured qualification artifact is missing")
    actual = hashlib.sha256(record_path.read_bytes()).hexdigest()
    if actual != config.qualification_sha256:
        raise ValueError("configured qualification digest mismatch")
    runner = isolation_runner
    if runner is None:
        runner = DockerIsolationRunner(policy_from_qualification(qualification))
    return validate_qualification(qualification, runner=runner)  # type: ignore[arg-type]


def run_campaign(root: Path | str, *, isolation_runner: object | None = None) -> dict:
    campaign_root = Path(root).resolve()
    manifest = read_json(campaign_root / "manifest.json")
    config = campaign_from_dict(manifest["config"])
    state_path = campaign_root / "state.json"
    state = read_json(state_path)
    if state["status"] == "stopped":
        raise ValueError(f"campaign is stopped: {state['stop_reason']}")
    if config.mode == "live":
        validate_campaign_isolation(config, isolation_runner=isolation_runner)
        raise ValueError("provider live execution remains disabled pending credential and egress authorization")
    schedule = _schedule(manifest)
    if len(schedule) > config.max_total_runs:
        raise ValueError("scheduled runs exceed max_total_runs")
    completed = set(state["completed_run_ids"])
    reconciled = 0
    for cell in schedule:
        result_path = campaign_root / "runs" / cell["run_id"] / "result.json"
        if not result_path.exists():
            continue
        result = _read_run_result(result_path.parent, repair_missing_digest=True)
        identity = {name: result.get(name) for name in ("run_id", "agent", "task_id", "attempt")}
        expected = {name: cell[name] for name in identity}
        if identity != expected:
            raise ValueError(f"run artifact identity conflict: {cell['run_id']}")
        if cell["run_id"] not in completed:
            completed.add(cell["run_id"])
            reconciled += 1
    if reconciled:
        state["completed_run_ids"] = sorted(completed)
        state["status"] = "completed" if len(completed) == len(schedule) else "running"
        write_atomic(state_path, state)
        append_event(campaign_root / "events.jsonl", {"type": "state.reconciled", "runs": reconciled})
    new_runs = 0
    for cell in schedule:
        if cell["run_id"] in completed:
            continue
        run_root = campaign_root / "runs" / cell["run_id"]
        workspace = run_root / "workspace"
        write_immutable(
            run_root / "manifest.json",
            {
                "schema_version": 1,
                "experiment_id": manifest["experiment_id"],
                **cell,
                "model": config.agents[cell["agent"]].model,
                "mode": config.mode,
            },
        )
        stage_task(cell["task_id"], workspace)
        agent_config = config.agents[cell["agent"]]
        if agent_config.behavior == "reference":
            apply_reference(cell["task_id"], workspace)
        verification = verify_task(cell["task_id"], workspace)
        result = {
            "schema_version": 1,
            **cell,
            "model": agent_config.model,
            "behavior": agent_config.behavior,
            "passed": verification["passed"],
            "verification": verification,
            "completed_at": _now(),
        }
        write_immutable(run_root / "result.json", result)
        result_hash = hashlib.sha256((run_root / "result.json").read_bytes()).hexdigest()
        write_immutable_bytes(run_root / "result.sha256", (result_hash + "\n").encode("ascii"))
        append_event(campaign_root / "events.jsonl", {"type": "run.completed", "run_id": cell["run_id"], "passed": result["passed"], "result_sha256": result_hash})
        completed.add(cell["run_id"])
        state["completed_run_ids"] = sorted(completed)
        state["status"] = "completed" if len(completed) == len(schedule) else "running"
        write_atomic(state_path, state)
        new_runs += 1
    return {"schema_version": 1, "command": "experiment-run", "status": state["status"], "new_runs": new_runs, "reconciled_runs": reconciled, "completed_runs": len(completed)}


def stop_campaign(root: Path | str, reason: str) -> dict:
    if not reason.strip():
        raise ValueError("stop reason must be nonempty")
    campaign_root = Path(root).resolve()
    state_path = campaign_root / "state.json"
    state = read_json(state_path)
    if state["status"] != "stopped":
        state["status"] = "stopped"
        state["stop_reason"] = reason
        write_atomic(state_path, state)
        append_event(campaign_root / "events.jsonl", {"type": "campaign.stopped", "reason": reason})
    return {"schema_version": 1, "command": "experiment-stop", "status": "stopped", "reason": state["stop_reason"]}


def report_campaign(root: Path | str) -> dict:
    campaign_root = Path(root).resolve()
    manifest = read_json(campaign_root / "manifest.json")
    agents: dict[str, dict[str, int]] = {}
    results = []
    runs_root = campaign_root / "runs"
    if runs_root.exists():
        for path in sorted(runs_root.glob("*/result.json")):
            result = _read_run_result(path.parent)
            results.append(result)
            summary = agents.setdefault(result["agent"], {"runs": 0, "passed": 0, "failed": 0})
            summary["runs"] += 1
            summary["passed" if result["passed"] else "failed"] += 1
    report = {"schema_version": 1, "command": "experiment-report", "experiment_id": manifest["experiment_id"], "total_runs": len(results), "agents": agents}
    reports = campaign_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_atomic(reports / "summary.json", report)
    lines = ["# Experiment report", "", f"Experiment: `{manifest['experiment_id']}`", "", f"Total runs: {len(results)}", ""]
    for name in sorted(agents):
        summary = agents[name]
        lines.append(f"- {name}: {summary['passed']} passed, {summary['failed']} failed, {summary['runs']} total")
    lines.extend(["", "Executable acceptance results are authoritative; agent completion claims are not.", ""])
    write_atomic_bytes(reports / "report.md", "\n".join(lines).encode("utf-8"))
    return report
