"""Public-seam contracts for the resumable harness optimization loop."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from claude_harness_eval.experiment.optimization import (
    ClaudeSessionRunner,
    FakeImprover,
    OptimizationConfig,
    _codex_structured,
    _evaluation_schema,
    _hard_gates,
    initialize_optimization,
    load_optimization_config,
    report_optimization,
    run_optimization,
)


DIMENSIONS = {
    "correctness": {"weight": 0.5, "minimum": 4.0},
    "efficiency": {"weight": 0.5, "minimum": 4.0},
}


def write_fixture(tmp_path: Path, **overrides: object) -> tuple[OptimizationConfig, Path]:
    prompt = tmp_path / "prompt.md"
    scenario = tmp_path / "scenario.md"
    rubric = tmp_path / "rubric.json"
    prompt.write_text("baseline prompt", encoding="utf-8")
    scenario.write_text("investigate the deployed slowdown", encoding="utf-8")
    rubric.write_text(json.dumps({
        "schema_version": 1,
        "rubric_id": "test-rubric",
        "dimensions": DIMENSIONS,
        "hard_gates": [{"gate_id": "no_schema_error", "kind": "forbid", "pattern": "schema error"}],
        "target": {"weighted_total": 4.0, "max_median_tokens": 5000, "max_median_elapsed_seconds": 60},
    }), encoding="utf-8")
    values: dict[str, object] = {
        "schema_version": 1,
        "optimization_id": "test-loop",
        "mode": "fake",
        "prompt_file": prompt.name,
        "scenario_prompt_file": scenario.name,
        "rubric_file": rubric.name,
        "claude_model": "fake-claude",
        "claude_effort": "high",
        "evaluator_model": "fake-codex",
        "improver_model": "fake-codex",
        "repetitions": 2,
        "max_rounds": 4,
        "max_stagnant_rounds": 2,
        "max_total_sessions": 10,
        "timeout_seconds": 60,
        "max_tokens_per_run": 5000,
        "minimum_total_gain": 0.1,
        "minimum_efficiency_gain": 0.05,
        "live_authorized": False,
    }
    values.update(overrides)
    config = tmp_path / "optimization.toml"
    lines = []
    for key, value in values.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, str):
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key} = {rendered}")
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return load_optimization_config(config), config


class ScoreRunner:
    def __init__(self, scores: dict[str, tuple[float, float]]):
        self.scores = scores
        self.calls: list[tuple[str, int]] = []

    def run(self, *, candidate_id: str, prompt_path: Path, attempt: int, round_number: int) -> dict:
        self.calls.append((candidate_id, attempt))
        correctness, efficiency = self.scores[candidate_id]
        return {
            "schema_version": 1, "candidate_id": candidate_id, "attempt": attempt,
            "round": round_number, "status": "completed", "transcript": prompt_path.read_text(encoding="utf-8"),
            "scores": {"correctness": correctness, "efficiency": efficiency},
            "metrics": {"tokens": 1000, "elapsed_seconds": 5}, "completed_at": "2026-09-17T00:00:00Z",
        }


class ScoreEvaluator:
    def evaluate(self, *, candidate_id: str, observations: list[dict], rubric: dict) -> dict:
        scores = observations[0]["scores"]
        total = sum(scores[name] * rubric["dimensions"][name]["weight"] for name in scores)
        return {
            "schema_version": 1, "candidate_id": candidate_id, "hard_gates": {"no_schema_error": True},
            "dimensions": {name: {"score": score, "evidence": ["test"]} for name, score in scores.items()},
            "weighted_total": total, "metrics": {"median_tokens": 1000.0, "median_elapsed_seconds": 5.0},
            "evaluated_at": "2026-09-17T00:00:00Z",
        }


def test_fake_loop_promotes_until_target_and_resume_is_idempotent(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)

    first = run_optimization(root)
    before = (root / "events.jsonl").read_bytes()
    resumed = run_optimization(root)
    after = (root / "events.jsonl").read_bytes()
    report = report_optimization(root)

    assert first["status"] == "completed"
    assert first["stop_reason"] == "target-met"
    assert first["champion_id"] == "CAND-002"
    assert first["sessions_used"] == 6
    assert resumed["champion_id"] == "CAND-002"
    assert before == after
    assert report["champion_id"] == "CAND-002"
    assert (root / "reports" / "report.md").is_file()


def test_resume_reconciles_existing_decision_without_duplicate_event(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path, max_rounds=1)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)
    completed = run_optimization(root)
    events_path = root / "events.jsonl"
    events_before = events_path.read_text(encoding="utf-8").splitlines()
    state_path = root / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update({
        "status": "running", "champion_id": "CAND-000", "next_round": 1,
        "completed_rounds": [], "stagnant_rounds": 0, "stop_reason": None,
    })
    state_path.write_text(json.dumps(state), encoding="utf-8")

    resumed = run_optimization(root)
    events_after = events_path.read_text(encoding="utf-8").splitlines()

    assert completed["champion_id"] == resumed["champion_id"] == "CAND-001"
    assert events_before == events_after


def test_dimension_regression_rejects_higher_total_score(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path, max_rounds=1, max_stagnant_rounds=1)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)
    runner = ScoreRunner({"CAND-000": (4.0, 2.0), "CAND-001": (3.5, 5.0)})

    result = run_optimization(root, runner=runner, evaluator=ScoreEvaluator(), improver=FakeImprover())
    decision = json.loads((root / "rounds" / "round-001" / "decision.json").read_text(encoding="utf-8"))

    assert result["champion_id"] == "CAND-000"
    assert result["stop_reason"] == "no-progress"
    assert decision["decision"] == "reject"
    assert any("regressed dimension correctness" in reason for reason in decision["reasons"])


def test_session_budget_blocks_without_promoting_partial_candidate(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path, max_total_sessions=2)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)

    with pytest.raises(ValueError, match="budget exhausted"):
        run_optimization(root)

    state = json.loads((root / "state.json").read_text(encoding="utf-8"))
    assert state["status"] == "blocked"
    assert state["stop_reason"] == "session-budget-exhausted"
    assert state["champion_id"] == "CAND-000"
    assert run_optimization(root)["status"] == "blocked"


def test_tampered_result_blocks_reporting_and_resume(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)
    run_optimization(root)
    result_path = root / "candidates" / "CAND-000" / "runs" / "attempt-01.json"
    result_path.write_text(result_path.read_text(encoding="utf-8").replace('"tokens":4000', '"tokens":1'), encoding="utf-8")

    with pytest.raises(ValueError, match="digest mismatch"):
        report_optimization(root)


def test_completed_resume_rejects_changed_frozen_rubric(tmp_path: Path) -> None:
    config, _ = write_fixture(tmp_path)
    root = tmp_path / "campaign"
    initialize_optimization(config, root)
    run_optimization(root)
    rubric_path = Path(config.rubric_file)
    rubric_path.write_text(rubric_path.read_text(encoding="utf-8").replace('"minimum": 4.0', '"minimum": 3.9', 1), encoding="utf-8")

    with pytest.raises(ValueError, match="rubric changed"):
        run_optimization(root)


def test_live_command_is_fresh_bounded_and_uses_candidate_inputs(tmp_path: Path) -> None:
    prompt = tmp_path / "candidate.md"
    prompt.write_text("candidate", encoding="utf-8")
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = OptimizationConfig(
        schema_version=1, optimization_id="live", mode="live", prompt_file=str(prompt),
        scenario_prompt_file=str(prompt), rubric_file=str(settings), workspace=str(workspace),
        claude_model="opus", claude_effort="high", evaluator_model="gpt-test",
        improver_model="gpt-test", repetitions=2, max_rounds=3, max_stagnant_rounds=2,
        max_total_sessions=10, timeout_seconds=60, max_tokens_per_run=150000,
        max_budget_usd_per_run=2.0, minimum_total_gain=0.1, minimum_efficiency_gain=0.05,
        live_authorized=True, plugin_dir=str(plugin), settings_file=str(settings),
    )

    command = ClaudeSessionRunner(config, "investigate").command(prompt)

    assert command[:4] == ["claude", "-p", "--output-format", "stream-json"]
    assert "--include-hook-events" in command
    assert "--no-session-persistence" not in command
    assert command[command.index("--permission-mode") + 1] == "bypassPermissions"
    assert "--dangerously-skip-permissions" in command
    assert command[command.index("--setting-sources") + 1] == "project"
    assert command[command.index("--append-system-prompt-file") + 1] == str(prompt)
    assert command[command.index("--plugin-dir") + 1] == str(plugin)
    assert command[-1] == "investigate"


def test_live_runner_uses_fresh_fixture_copy_and_captures_workbench_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    template = tmp_path / "template"
    template.mkdir()
    (template / ".harness-scenario.json").write_text(json.dumps({"schema_version": 1, "fixture_id": "fixture", "secret_scrubbed": True}), encoding="utf-8")
    (template / "source.txt").write_text("pristine", encoding="utf-8")
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")
    candidate = tmp_path / "campaign" / "candidates" / "CAND-001"
    candidate.mkdir(parents=True)
    prompt = candidate / "prompt.md"
    prompt.write_text("candidate", encoding="utf-8")
    config = OptimizationConfig(
        schema_version=1, optimization_id="live", mode="live", prompt_file=str(prompt),
        scenario_prompt_file=str(prompt), rubric_file=str(settings), workspace=str(template),
        claude_model="opus", claude_effort="high", evaluator_model="gpt-test",
        improver_model="gpt-test", repetitions=1, max_rounds=1, max_stagnant_rounds=1,
        max_total_sessions=2, timeout_seconds=60, max_tokens_per_run=150000,
        max_budget_usd_per_run=2.0, minimum_total_gain=0.1, minimum_efficiency_gain=0.05,
        live_authorized=True, settings_file=str(settings),
    )

    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        workspace = Path(str(kwargs["cwd"]))
        (workspace / "source.txt").write_text("changed", encoding="utf-8")
        workbench = workspace / ".workbench"
        workbench.mkdir()
        (workbench / "state.json").write_text(json.dumps({"status": "awaiting-acceptance"}), encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout=json.dumps({"usage": {"input_tokens": 10, "output_tokens": 5}, "result": "done"}) + "\n", stderr="")

    monkeypatch.setattr("claude_harness_eval.experiment.optimization.subprocess.run", fake_run)
    observation = ClaudeSessionRunner(config, "investigate").run(candidate_id="CAND-001", prompt_path=prompt, attempt=1, round_number=1)

    copied = candidate / "runs" / "attempt-01-workspace"
    assert (template / "source.txt").read_text(encoding="utf-8") == "pristine"
    assert (copied / "source.txt").read_text(encoding="utf-8") == "changed"
    assert observation["status"] == "completed"
    assert observation["metrics"]["tokens"] == 15
    assert observation["workspace_evidence"]["workbench_records"][".workbench/state.json"]["status"] == "awaiting-acceptance"


def test_live_runner_uses_peak_request_context_not_cumulative_result_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    template = tmp_path / "template"
    template.mkdir()
    (template / ".harness-scenario.json").write_text(
        json.dumps({"schema_version": 1, "fixture_id": "fixture", "secret_scrubbed": True}),
        encoding="utf-8",
    )
    settings = tmp_path / "settings.json"
    settings.write_text("{}", encoding="utf-8")
    candidate = tmp_path / "campaign" / "candidates" / "CAND-001"
    candidate.mkdir(parents=True)
    prompt = candidate / "prompt.md"
    prompt.write_text("candidate", encoding="utf-8")
    config = OptimizationConfig(
        schema_version=1, optimization_id="live", mode="live", prompt_file=str(prompt),
        scenario_prompt_file=str(prompt), rubric_file=str(settings), workspace=str(template),
        claude_model="opus", claude_effort="high", evaluator_model="gpt-test",
        improver_model="gpt-test", repetitions=1, max_rounds=1, max_stagnant_rounds=1,
        max_total_sessions=2, timeout_seconds=60, max_tokens_per_run=150000,
        max_budget_usd_per_run=2.0, minimum_total_gain=0.1, minimum_efficiency_gain=0.05,
        live_authorized=True, settings_file=str(settings),
    )
    stream = "\n".join([
        json.dumps({"type": "assistant", "message": {"usage": {
            "input_tokens": 10, "cache_creation_input_tokens": 20,
            "cache_read_input_tokens": 100000, "output_tokens": 5,
        }}}),
        json.dumps({"type": "result", "usage": {
            "input_tokens": 100, "cache_read_input_tokens": 9000000, "output_tokens": 50,
        }, "result": "done"}),
    ]) + "\n"

    monkeypatch.setattr(
        "claude_harness_eval.experiment.optimization.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=stream, stderr=""),
    )
    observation = ClaudeSessionRunner(config, "investigate").run(
        candidate_id="CAND-001", prompt_path=prompt, attempt=1, round_number=1,
    )

    assert observation["status"] == "completed"
    assert observation["metrics"]["tokens"] == 100035


def test_codex_structured_resolves_windows_command_shim(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shim = str(tmp_path / "codex.cmd")
    captured: list[str] = []

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        captured.extend(command)
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text('{"dimensions": {}}', encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("claude_harness_eval.experiment.optimization.shutil.which", lambda name: shim)
    monkeypatch.setattr("claude_harness_eval.experiment.optimization.subprocess.run", fake_run)

    assert _codex_structured("gpt-test", "grade", {"type": "object"}, 60) == {"dimensions": {}}
    assert captured[0] == shim


def test_evaluation_schema_has_explicit_strict_dimension_properties() -> None:
    schema = _evaluation_schema(["correctness", "efficiency"])
    dimensions = schema["properties"]["dimensions"]

    assert dimensions["additionalProperties"] is False
    assert dimensions["required"] == ["correctness", "efficiency"]
    assert set(dimensions["properties"]) == {"correctness", "efficiency"}


def test_hard_gates_ignore_source_echo_but_detect_operational_tool_failure() -> None:
    rubric = {
        "hard_gates": [
            {"gate_id": "clean", "kind": "forbid", "pattern": "Workbench refused"},
        ],
    }
    source_echo = json.dumps({
        "type": "event_msg",
        "payload": {"item": {"type": "CommandExecution", "stdout": 'runtime.py: print("Workbench refused")'}},
    })
    refusal = json.dumps({
        "type": "user",
        "message": {"content": [{"type": "tool_result", "content": "Workbench refused accept-handoff: digest mismatch"}]},
    })

    assert _hard_gates(source_echo, rubric)["clean"] is True
    assert _hard_gates(refusal, rubric)["clean"] is False


def test_order_gate_passes_when_later_pattern_is_absent() -> None:
    rubric = {
        "hard_gates": [{
            "gate_id": "environment_first",
            "kind": "order",
            "first_pattern": "environment",
            "then_pattern": "ranking|recommendation",
        }]
    }
    transcript = "Environment: deployed test.\nConditional options follow."

    assert _hard_gates(transcript, rubric)["environment_first"] is True


def test_order_gate_still_requires_first_pattern() -> None:
    rubric = {
        "hard_gates": [{
            "gate_id": "environment_first",
            "kind": "order",
            "first_pattern": "environment",
            "then_pattern": "ranking|recommendation",
        }]
    }

    assert _hard_gates("Conditional options follow.", rubric)["environment_first"] is False


def test_live_configuration_requires_authorization_budget_and_disposable_marker(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".harness-scenario.json"):
        write_fixture(tmp_path, mode="live", live_authorized=True, workspace=str(tmp_path), max_budget_usd_per_run=1.0)


def test_cli_zero_cost_optimization_round_trip(tmp_path: Path) -> None:
    _, config = write_fixture(tmp_path)
    root = tmp_path / "campaign"
    commands = [
        ["optimize", "init", "--config", str(config), "--root", str(root), "--json"],
        ["optimize", "run", "--root", str(root), "--json"],
        ["optimize", "resume", "--root", str(root), "--json"],
        ["optimize", "report", "--root", str(root), "--json"],
    ]
    results = []
    for arguments in commands:
        completed = subprocess.run([sys.executable, "-m", "claude_harness_eval", *arguments], capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        results.append(json.loads(completed.stdout))

    assert [item["command"] for item in results] == ["optimize-init", "optimize-run", "optimize-run", "optimize-report"]
    assert results[1]["champion_id"] == results[2]["champion_id"] == results[3]["champion_id"]
