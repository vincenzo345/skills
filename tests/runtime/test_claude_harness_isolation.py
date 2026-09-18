"""Public-seam tests for the Docker isolation boundary."""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

import pytest

from claude_harness_eval.experiment.isolation import (
    DockerIsolationRunner,
    IsolationPolicy,
    RunResult,
    qualify_isolation,
    run_qualified,
    validate_qualification,
)


def test_runner_command_enforces_the_complete_isolation_policy(tmp_path: Path) -> None:
    policy = IsolationPolicy(image="python:3.12-slim")
    runner = DockerIsolationRunner(policy)

    argv = runner.command(tmp_path, ["python", "-c", "print('ok')"], container_name="eval-fixed")

    assert argv[:3] == ["docker", "run", "--rm"]
    assert ["--name", "eval-fixed"] == argv[argv.index("--name") : argv.index("--name") + 2]
    assert ["--network", "none"] == argv[argv.index("--network") : argv.index("--network") + 2]
    assert "--read-only" in argv
    assert ["--cap-drop", "ALL"] == argv[argv.index("--cap-drop") : argv.index("--cap-drop") + 2]
    assert ["--security-opt", "no-new-privileges"] == argv[argv.index("--security-opt") : argv.index("--security-opt") + 2]
    assert ["--user", "65534:65534"] == argv[argv.index("--user") : argv.index("--user") + 2]
    assert ["--memory", "256m"] == argv[argv.index("--memory") : argv.index("--memory") + 2]
    assert ["--cpus", "1.0"] == argv[argv.index("--cpus") : argv.index("--cpus") + 2]
    assert ["--pids-limit", "64"] == argv[argv.index("--pids-limit") : argv.index("--pids-limit") + 2]
    mount = argv[argv.index("--mount") + 1]
    assert mount == f"type=bind,source={tmp_path.resolve()},target=/workspace"
    assert argv[argv.index("--workdir") + 1] == "/workspace"
    assert argv[argv.index("--tmpfs") + 1] == "/tmp:rw,noexec,nosuid,size=64m"
    assert argv[-4:] == ["python:3.12-slim", "python", "-c", "print('ok')"]
    assert sum("type=bind" in item for item in argv) == 1


@pytest.mark.parametrize("marker", [".git", ".workbench", ".claude", ".codex"])
def test_runner_rejects_a_broad_or_control_plane_workspace(tmp_path: Path, marker: str) -> None:
    (tmp_path / marker).mkdir()

    with pytest.raises(ValueError, match="staged workspace"):
        DockerIsolationRunner(IsolationPolicy()).command(
            tmp_path,
            ["python", "agent.py"],
            container_name="eval-rejected",
        )


def _fake_docker(path: Path) -> tuple[str, ...]:
    script = path / "fake_docker.py"
    script.write_text(
        """import sys, time
if sys.argv[1] == 'rm':
    raise SystemExit(0)
mode = sys.argv[-1]
if mode == 'overflow':
    sys.stdout.write('x' * 4096)
elif mode == 'hang':
    time.sleep(10)
else:
    print('ok')
""",
        encoding="utf-8",
    )
    return (sys.executable, str(script))


def test_runner_bounds_output_and_fails_closed_on_overflow(tmp_path: Path) -> None:
    policy = IsolationPolicy(max_output_bytes=128)
    runner = DockerIsolationRunner(policy, docker_command=_fake_docker(tmp_path))

    result = runner.run(tmp_path, ["overflow"], container_name="eval-overflow")

    assert result.output_exceeded is True
    assert result.succeeded is False
    assert len(result.stdout.encode("utf-8")) == 128
    assert result.container_name == "eval-overflow"


def test_runner_times_out_and_attempts_forced_cleanup(tmp_path: Path) -> None:
    policy = IsolationPolicy(timeout_seconds=0.1)
    runner = DockerIsolationRunner(policy, docker_command=_fake_docker(tmp_path))

    result = runner.run(tmp_path, ["hang"], container_name="eval-timeout")

    assert result.timed_out is True
    assert result.succeeded is False
    assert result.duration_seconds < 5


def test_unavailable_docker_fails_with_a_bounded_diagnostic(tmp_path: Path) -> None:
    runner = DockerIsolationRunner(
        IsolationPolicy(),
        docker_command=("definitely-missing-docker-executable",),
    )

    with pytest.raises(ValueError, match="Docker executable is unavailable"):
        runner.inspect_environment()
    with pytest.raises(ValueError, match="Docker executable is unavailable"):
        runner.run(tmp_path, ["python", "-c", "print('no')"])


class QualifyingRunner:
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
            "workspace_writable": True,
            "root_read_only": True,
            "non_root": True,
            "capabilities_dropped": True,
            "no_new_privileges": True,
            "network_disabled": True,
            "host_secret_absent": True,
            "evaluator_absent": True,
            "memory_limited": True,
            "cpu_limited": True,
            "pids_limited": True,
        }
        return RunResult(container_name or "canary", 0, json.dumps(canaries), "", False, False, 0.1)

    def container_exists(self, name: str) -> bool:
        return False


def test_qualification_is_written_only_after_all_canaries_pass(tmp_path: Path) -> None:
    destination = tmp_path / "qualification"

    result = qualify_isolation(destination, runner=QualifyingRunner())

    assert result["status"] == "qualified"
    assert result["runtime"]["id"] == "server-1"
    assert result["image"]["id"] == "sha256:image-1"
    assert all(result["canaries"].values())
    record = destination / "qualification.json"
    assert json.loads(record.read_text(encoding="utf-8")) == result
    assert len((destination / "qualification.sha256").read_text(encoding="ascii").strip()) == 64


def test_failed_canary_leaves_no_qualification_artifact(tmp_path: Path) -> None:
    class FailingRunner(QualifyingRunner):
        def run(self, workspace: Path, command: list[str], *, container_name: str | None = None, timeout_seconds: float | None = None) -> RunResult:
            result = super().run(workspace, command, container_name=container_name, timeout_seconds=timeout_seconds)
            if timeout_seconds is None:
                values = json.loads(result.stdout)
                values["network_disabled"] = False
                return RunResult(result.container_name, 0, json.dumps(values), "", False, False, 0.1)
            return result

    destination = tmp_path / "qualification"

    with pytest.raises(ValueError, match="network_disabled"):
        qualify_isolation(destination, runner=FailingRunner())

    assert not (destination / "qualification.json").exists()


def test_qualification_rejects_tampering_policy_drift_and_runtime_drift(tmp_path: Path) -> None:
    destination = tmp_path / "qualification"
    qualify_isolation(destination, runner=QualifyingRunner())

    class PolicyDrift(QualifyingRunner):
        policy = IsolationPolicy(memory_mb=512)

    with pytest.raises(ValueError, match="policy mismatch"):
        validate_qualification(destination, runner=PolicyDrift())

    class RuntimeDrift(QualifyingRunner):
        def inspect_environment(self) -> tuple[dict, dict]:
            runtime, image = super().inspect_environment()
            runtime["id"] = "server-2"
            return runtime, image

    with pytest.raises(ValueError, match="runtime mismatch"):
        validate_qualification(destination, runner=RuntimeDrift())

    record = destination / "qualification.json"
    record.write_text(record.read_text(encoding="utf-8").replace("server-1", "server-x"), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_qualification(destination, runner=QualifyingRunner())


def test_qualified_runner_executes_only_after_evidence_validation(tmp_path: Path) -> None:
    destination = tmp_path / "qualification"
    qualify_isolation(destination, runner=QualifyingRunner())

    class ExecutingRunner(QualifyingRunner):
        def run(self, workspace: Path, command: list[str], *, container_name: str | None = None, timeout_seconds: float | None = None) -> RunResult:
            return RunResult(container_name or "agent", 0, "agent ok\n", "", False, False, 0.2)

    result = run_qualified(destination, tmp_path / "workspace", ["python", "agent.py"], runner=ExecutingRunner())

    assert result.succeeded is True
    assert result.stdout == "agent ok\n"


def _docker_ready() -> bool:
    completed = subprocess.run(
        ["docker", "image", "inspect", "python:3.12-slim"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


@pytest.mark.skipif(not _docker_ready(), reason="local Docker engine/image unavailable")
def test_cli_qualifies_and_runs_a_real_isolated_fake_agent(tmp_path: Path) -> None:
    qualification = tmp_path / "qualification"
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    qualify = subprocess.run(
        [
            sys.executable,
            "-m",
            "claude_harness_eval",
            "isolation",
            "qualify",
            "--root",
            str(qualification),
            "--image",
            "python:3.12-slim",
            "--timeout-seconds",
            "5",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert qualify.returncode == 0, qualify.stderr
    qualified = json.loads(qualify.stdout)
    assert qualified["status"] == "qualified"

    live_config = tmp_path / "live.toml"
    live_config.write_text(
        f'''schema_version = 1
campaign_id = "docker-doctor"
mode = "live"
task_ids = ["inclusive-range-partition"]
repetitions = 1
seed = 1
max_rounds = 1
max_total_runs = 2
max_concurrency = 1
live_authorized = true
organization_permission_confirmed = true
qualification_file = "{qualification.as_posix()}"
qualification_sha256 = "{(qualification / 'qualification.sha256').read_text(encoding='ascii').strip()}"
max_total_cost_usd = 1.0
[agents.claude]
model = "claude-example"
[agents.codex]
model = "codex-example"
''',
        encoding="utf-8",
    )
    doctor = subprocess.run(
        [sys.executable, "-m", "claude_harness_eval", "doctor", "--config", str(live_config), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert doctor.returncode == 0, doctor.stderr
    assert json.loads(doctor.stdout)["qualification_id"] == qualified["qualification_id"]

    execute = subprocess.run(
        [
            sys.executable,
            "-m",
            "claude_harness_eval",
            "isolation",
            "run",
            "--qualification",
            str(qualification),
            "--workspace",
            str(workspace),
            "--json",
            "--",
            "python",
            "-c",
            "from pathlib import Path; Path('agent.txt').write_text('ok'); print('fake agent ok')",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert execute.returncode == 0, execute.stderr
    executed = json.loads(execute.stdout)
    assert executed["status"] == "completed"
    assert executed["succeeded"] is True
    assert executed["stdout"] == "fake agent ok\n"
    assert (workspace / "agent.txt").read_text(encoding="utf-8") == "ok"
