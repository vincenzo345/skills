"""Public-seam tests for the zero-cost agent experiment controller."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys

import pytest

from claude_harness_eval.experiment.adapters import ClaudeAdapter, CodexAdapter
from claude_harness_eval.experiment.config import load_campaign
from claude_harness_eval.experiment.controller import (
    initialize_campaign,
    report_campaign,
    run_campaign,
    stop_campaign,
)
from claude_harness_eval.experiment.isolation import IsolationPolicy, RunResult, qualify_isolation


def write_config(path: Path, *, mode: str = "fake") -> Path:
    path.write_text(
        f'''schema_version = 1
campaign_id = "smoke"
mode = "{mode}"
task_ids = ["inclusive-range-partition", "config-precedence"]
repetitions = 1
seed = 17
max_rounds = 3
max_total_runs = 4
max_concurrency = 1

[agents.claude]
model = "fake-claude"
behavior = "reference"

[agents.codex]
model = "fake-codex"
behavior = "noop"
''',
        encoding="utf-8",
    )
    return path


class _QualificationRunner:
    policy = IsolationPolicy()

    def inspect_environment(self) -> tuple[dict, dict]:
        return (
            {"id": "server-1", "server_version": "28.3.2", "os_type": "linux", "architecture": "x86_64"},
            {"requested": self.policy.image, "id": "sha256:image-1", "repo_digests": ["python@sha256:one"]},
        )

    def run(self, workspace: Path, command: list[str], *, container_name: str | None = None, timeout_seconds: float | None = None) -> RunResult:
        if timeout_seconds is not None:
            return RunResult(container_name or "timeout", -9, "", "", True, False, 0.1)
        canaries = {
            "workspace_writable": True, "root_read_only": True, "non_root": True,
            "capabilities_dropped": True, "no_new_privileges": True, "network_disabled": True,
            "host_secret_absent": True, "evaluator_absent": True, "memory_limited": True,
            "cpu_limited": True, "pids_limited": True,
        }
        return RunResult(container_name or "canary", 0, json.dumps(canaries), "", False, False, 0.1)

    def container_exists(self, name: str) -> bool:
        return False


def test_fake_campaign_runs_through_public_verifier_and_resume_is_idempotent(tmp_path: Path) -> None:
    config = load_campaign(write_config(tmp_path / "campaign.toml"))
    root = tmp_path / "run"

    initialized = initialize_campaign(config, root)
    first = run_campaign(root)
    before = (root / "events.jsonl").read_bytes()
    resumed = run_campaign(root)
    after = (root / "events.jsonl").read_bytes()
    report = report_campaign(root)

    assert initialized["command"] == "experiment-init"
    assert first["new_runs"] == 4
    assert resumed["new_runs"] == 0
    assert before == after
    assert report["agents"]["claude"]["passed"] == 2
    assert report["agents"]["codex"]["passed"] == 0
    assert report["total_runs"] == 4
    assert len(list((root / "runs").glob("*/result.json"))) == 4
    for result_path in (root / "runs").glob("*/result.json"):
        run_root = result_path.parent
        assert (run_root / "manifest.json").is_file()
        assert (run_root / "result.sha256").read_text(encoding="ascii").strip() == hashlib.sha256(result_path.read_bytes()).hexdigest()
    assert (root / "reports" / "report.md").read_text(encoding="utf-8").startswith("# Experiment report")


def test_stop_is_durable_and_prevents_new_runs(tmp_path: Path) -> None:
    config = load_campaign(write_config(tmp_path / "campaign.toml"))
    root = tmp_path / "run"
    initialize_campaign(config, root)

    stopped = stop_campaign(root, "operator requested stop")

    assert stopped["status"] == "stopped"
    with pytest.raises(ValueError, match="stopped"):
        run_campaign(root)
    assert not (root / "runs").exists()


def test_resume_reconciles_a_completed_artifact_after_state_write_loss(tmp_path: Path) -> None:
    config = load_campaign(write_config(tmp_path / "campaign.toml"))
    root = tmp_path / "run"
    initialize_campaign(config, root)
    run_campaign(root)
    state_path = root / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    lost_id = state["completed_run_ids"].pop()
    state["status"] = "running"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result_path = root / "runs" / lost_id / "result.json"
    result_before = result_path.read_bytes()

    resumed = run_campaign(root)

    assert resumed["new_runs"] == 0
    assert resumed["reconciled_runs"] == 1
    assert result_path.read_bytes() == result_before
    repaired = json.loads(state_path.read_text(encoding="utf-8"))
    assert lost_id in repaired["completed_run_ids"]


def test_initialization_rejects_reusing_a_root_for_different_config(tmp_path: Path) -> None:
    first_path = write_config(tmp_path / "first.toml")
    second_path = write_config(tmp_path / "second.toml")
    second_path.write_text(second_path.read_text(encoding="utf-8").replace('seed = 17', 'seed = 18'), encoding="utf-8")
    root = tmp_path / "run"
    initialize_campaign(load_campaign(first_path), root)

    with pytest.raises(ValueError, match="immutable artifact conflict"):
        initialize_campaign(load_campaign(second_path), root)


def test_tampered_run_result_blocks_resume_and_reporting(tmp_path: Path) -> None:
    config = load_campaign(write_config(tmp_path / "campaign.toml"))
    root = tmp_path / "run"
    initialize_campaign(config, root)
    run_campaign(root)
    result_path = next((root / "runs").glob("*/result.json"))
    result_path.write_text(result_path.read_text(encoding="utf-8").replace('"passed":true', '"passed":false'), encoding="utf-8")

    with pytest.raises(ValueError, match="digest mismatch"):
        run_campaign(root)
    with pytest.raises(ValueError, match="digest mismatch"):
        report_campaign(root)


def test_live_configuration_fails_closed_without_authorization_and_limits(tmp_path: Path) -> None:
    path = write_config(tmp_path / "campaign.toml", mode="live")

    with pytest.raises(ValueError, match="live mode requires"):
        load_campaign(path)


def test_live_campaign_binds_and_revalidates_exact_qualification(tmp_path: Path) -> None:
    qualification = tmp_path / "qualification"
    qualify_isolation(qualification, runner=_QualificationRunner())
    qualification_digest = hashlib.sha256((qualification / "qualification.json").read_bytes()).hexdigest()
    config_path = tmp_path / "live.toml"
    config_path.write_text(
        f'''schema_version = 1
campaign_id = "live-smoke"
mode = "live"
task_ids = ["inclusive-range-partition"]
repetitions = 1
seed = 17
max_rounds = 1
max_total_runs = 2
max_concurrency = 1
live_authorized = true
organization_permission_confirmed = true
qualification_file = "{qualification.as_posix()}"
qualification_sha256 = "{qualification_digest}"
max_total_cost_usd = 1.0

[agents.claude]
model = "claude-example"

[agents.codex]
model = "codex-example"
''',
        encoding="utf-8",
    )
    root = tmp_path / "campaign"
    initialize_campaign(load_campaign(config_path), root)

    with pytest.raises(ValueError, match="provider live execution remains disabled"):
        run_campaign(root, isolation_runner=_QualificationRunner())

    record = qualification / "qualification.json"
    record.write_text(record.read_text(encoding="utf-8").replace("server-1", "server-x"), encoding="utf-8")
    with pytest.raises(ValueError, match="configured qualification digest mismatch"):
        run_campaign(root, isolation_runner=_QualificationRunner())


def test_vendor_adapters_build_explicit_noninteractive_argv(tmp_path: Path) -> None:
    prompt = tmp_path / "candidate.md"
    prompt.write_text("verify before claiming completion", encoding="utf-8")

    claude = ClaudeAdapter(model="claude-example", effort="high", prompt_file=prompt)
    codex = CodexAdapter(model="codex-example", prompt_file=prompt)

    claude_argv = claude.command(tmp_path)
    codex_argv = codex.command(tmp_path)
    assert claude_argv[:3] == ["claude", "-p", "--output-format"]
    assert "stream-json" in claude_argv
    assert "--no-session-persistence" in claude_argv
    assert "--append-system-prompt-file" in claude_argv
    assert claude_argv[-1].startswith("Read TASK.md")
    assert codex_argv[:3] == ["codex", "exec", "--json"]
    assert "--ephemeral" in codex_argv
    assert "workspace-write" in codex_argv
    assert str(tmp_path) in codex_argv


def test_cli_experiment_round_trip_is_machine_readable(tmp_path: Path) -> None:
    config = write_config(tmp_path / "campaign.toml")
    root = tmp_path / "run"
    commands = [
        ["doctor", "--config", str(config), "--json"],
        ["experiment", "init", "--config", str(config), "--root", str(root), "--json"],
        ["experiment", "run", "--root", str(root), "--json"],
        ["experiment", "report", "--root", str(root), "--json"],
    ]
    results = []
    for arguments in commands:
        completed = subprocess.run(
            [sys.executable, "-m", "claude_harness_eval", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        results.append(json.loads(completed.stdout))

    assert [item["command"] for item in results] == [
        "doctor",
        "experiment-init",
        "experiment-run",
        "experiment-report",
    ]
    assert results[-1]["total_runs"] == 4
