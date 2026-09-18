"""Docker-backed isolation policy and runner boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
import threading
import time
from typing import Sequence
import uuid

from .store import digest, write_immutable, write_immutable_bytes


QUALIFICATION_SCHEMA_VERSION = 1
_REQUIRED_CANARIES = (
    "workspace_writable",
    "root_read_only",
    "non_root",
    "capabilities_dropped",
    "no_new_privileges",
    "network_disabled",
    "host_secret_absent",
    "evaluator_absent",
    "memory_limited",
    "cpu_limited",
    "pids_limited",
)
_FORBIDDEN_WORKSPACE_ENTRIES = frozenset({
    ".git",
    ".workbench",
    ".claude",
    ".codex",
})
_CANARY_SCRIPT = r'''import json, os
def status_value(name):
    prefix = name + ":"
    with open("/proc/self/status", encoding="utf-8") as stream:
        for line in stream:
            if line.startswith(prefix):
                return line.split(":", 1)[1].strip()
    return ""
def read(path):
    try:
        with open(path, encoding="utf-8") as stream:
            return stream.read().strip()
    except OSError:
        return ""
def limited_number(value, ceiling):
    return value not in {"", "max"} and int(value) <= ceiling
values = {}
try:
    with open("/workspace/isolation-canary.txt", "w", encoding="utf-8") as stream:
        stream.write("ok")
    values["workspace_writable"] = True
except OSError:
    values["workspace_writable"] = False
try:
    with open("/isolation-canary", "w", encoding="utf-8") as stream:
        stream.write("bad")
    values["root_read_only"] = False
except OSError:
    values["root_read_only"] = True
values["non_root"] = os.geteuid() != 0
values["capabilities_dropped"] = int(status_value("CapEff") or "1", 16) == 0
values["no_new_privileges"] = status_value("NoNewPrivs") == "1"
routes = read("/proc/net/route").splitlines()[1:]
values["network_disabled"] = not any(line.split()[1] == "00000000" for line in routes if len(line.split()) > 1)
values["host_secret_absent"] = "HARNESS_HOST_SECRET" not in os.environ and not os.path.exists("/host-secret.txt")
values["evaluator_absent"] = not os.path.exists("/evaluator")
values["memory_limited"] = limited_number(read("/sys/fs/cgroup/memory.max"), __MEMORY_BYTES__)
cpu = read("/sys/fs/cgroup/cpu.max").split()
values["cpu_limited"] = len(cpu) == 2 and cpu[0] != "max" and int(cpu[0]) / int(cpu[1]) <= __CPUS__
values["pids_limited"] = limited_number(read("/sys/fs/cgroup/pids.max"), __PIDS__)
print(json.dumps(values, sort_keys=True))
'''


@dataclass(frozen=True)
class IsolationPolicy:
    image: str = "python:3.12-slim"
    user: str = "65534:65534"
    memory_mb: int = 256
    cpus: float = 1.0
    pids_limit: int = 64
    tmpfs_mb: int = 64
    timeout_seconds: float = 30.0
    max_output_bytes: int = 1_000_000

    @classmethod
    def from_dict(cls, value: dict) -> "IsolationPolicy":
        fields = {
            "image",
            "user",
            "memory_mb",
            "cpus",
            "pids_limit",
            "tmpfs_mb",
            "timeout_seconds",
            "max_output_bytes",
        }
        if not isinstance(value, dict):
            raise ValueError("qualification policy must be an object")
        try:
            policy = cls(**{name: value[name] for name in fields})
        except (KeyError, TypeError) as exc:
            raise ValueError("qualification policy fields are invalid") from exc
        if (
            not policy.image
            or not policy.user
            or policy.memory_mb < 1
            or policy.cpus <= 0
            or policy.pids_limit < 1
            or policy.tmpfs_mb < 1
            or policy.timeout_seconds <= 0
            or policy.max_output_bytes < 1
        ):
            raise ValueError("qualification policy limits must be positive")
        return policy

    def to_dict(self) -> dict:
        return {
            "image": self.image,
            "user": self.user,
            "memory_mb": self.memory_mb,
            "cpus": self.cpus,
            "pids_limit": self.pids_limit,
            "tmpfs_mb": self.tmpfs_mb,
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "network": "none",
            "read_only_root": True,
            "cap_drop": ["ALL"],
            "no_new_privileges": True,
        }


@dataclass(frozen=True)
class RunResult:
    container_name: str
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    output_exceeded: bool
    duration_seconds: float

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and not self.output_exceeded

    def to_dict(self) -> dict:
        return {
            "container_name": self.container_name,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timed_out": self.timed_out,
            "output_exceeded": self.output_exceeded,
            "duration_seconds": self.duration_seconds,
            "succeeded": self.succeeded,
        }


class DockerIsolationRunner:
    def __init__(
        self,
        policy: IsolationPolicy,
        *,
        docker_command: Sequence[str] = ("docker",),
    ) -> None:
        if not docker_command:
            raise ValueError("docker_command must not be empty")
        self.policy = policy
        self.docker_command = tuple(docker_command)

    def command(
        self,
        workspace: Path | str,
        command: Sequence[str],
        *,
        container_name: str,
    ) -> list[str]:
        if not command or not all(isinstance(item, str) and item for item in command):
            raise ValueError("container command must be a nonempty string sequence")
        source = Path(workspace).resolve()
        if not source.is_dir():
            raise ValueError("staged workspace must be an existing directory")
        present = sorted(item for item in _FORBIDDEN_WORKSPACE_ENTRIES if (source / item).exists())
        if present:
            raise ValueError(f"staged workspace contains control-plane entries: {', '.join(present)}")
        for item in source.rglob("*"):
            if item.is_symlink() or (hasattr(item, "is_junction") and item.is_junction()):
                raise ValueError(f"staged workspace contains a link: {item.relative_to(source)}")
        policy = self.policy
        return [
            *self.docker_command,
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--user",
            policy.user,
            "--memory",
            f"{policy.memory_mb}m",
            "--cpus",
            str(policy.cpus),
            "--pids-limit",
            str(policy.pids_limit),
            "--mount",
            f"type=bind,source={source},target=/workspace",
            "--workdir",
            "/workspace",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,size={policy.tmpfs_mb}m",
            policy.image,
            *command,
        ]

    def run(
        self,
        workspace: Path | str,
        command: Sequence[str],
        *,
        container_name: str | None = None,
        timeout_seconds: float | None = None,
    ) -> RunResult:
        name = container_name or f"harness-{uuid.uuid4().hex[:16]}"
        argv = self.command(workspace, command, container_name=name)
        started = time.monotonic()
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            raise ValueError("Docker executable is unavailable") from exc
        retained = {"stdout": bytearray(), "stderr": bytearray()}
        remaining = [self.policy.max_output_bytes]
        exceeded = [False]
        lock = threading.Lock()

        def drain(label: str, stream: object) -> None:
            while True:
                chunk = stream.read(65_536)  # type: ignore[attr-defined]
                if not chunk:
                    return
                with lock:
                    take = min(len(chunk), remaining[0])
                    retained[label].extend(chunk[:take])
                    remaining[0] -= take
                    if take < len(chunk):
                        exceeded[0] = True

        threads = [
            threading.Thread(target=drain, args=("stdout", process.stdout), daemon=True),
            threading.Thread(target=drain, args=("stderr", process.stderr), daemon=True),
        ]
        for thread in threads:
            thread.start()
        timed_out = False

        def force_remove() -> None:
            try:
                subprocess.run(
                    [*self.docker_command, "rm", "-f", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=10,
                )
            except subprocess.TimeoutExpired:
                pass

        try:
            process.wait(timeout=self.policy.timeout_seconds if timeout_seconds is None else timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            # The timeout can fire before Docker has registered the container,
            # especially through Docker Desktop. Remove both before and after
            # terminating the client so a late-created container cannot leak.
            force_remove()
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            force_remove()
        for thread in threads:
            thread.join(timeout=5)
        return RunResult(
            container_name=name,
            exit_code=process.returncode,
            stdout=retained["stdout"].decode("utf-8", errors="replace"),
            stderr=retained["stderr"].decode("utf-8", errors="replace"),
            timed_out=timed_out,
            output_exceeded=exceeded[0],
            duration_seconds=round(time.monotonic() - started, 6),
        )

    def _docker_json(self, arguments: Sequence[str]) -> dict:
        try:
            completed = subprocess.run(
                [*self.docker_command, *arguments],
                capture_output=True,
                check=False,
                timeout=15,
            )
        except FileNotFoundError as exc:
            raise ValueError("Docker executable is unavailable") from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Docker inspection timed out") from exc
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace")[:500].strip()
            raise ValueError(f"Docker inspection failed: {detail or completed.returncode}")
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("Docker inspection returned invalid JSON") from exc

    def inspect_environment(self) -> tuple[dict, dict]:
        info = self._docker_json(["info", "--format", "{{json .}}"])
        image = self._docker_json(["image", "inspect", self.policy.image, "--format", "{{json .}}"])
        return (
            {
                "id": info.get("ID"),
                "server_version": info.get("ServerVersion"),
                "os_type": info.get("OSType"),
                "architecture": info.get("Architecture"),
            },
            {
                "requested": self.policy.image,
                "id": image.get("Id"),
                "repo_digests": sorted(image.get("RepoDigests") or []),
            },
        )

    def container_exists(self, name: str) -> bool:
        try:
            completed = subprocess.run(
                [*self.docker_command, "container", "inspect", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        except FileNotFoundError as exc:
            raise ValueError("Docker executable is unavailable") from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Docker container inspection timed out") from exc
        return completed.returncode == 0


def qualify_isolation(
    destination: Path | str,
    *,
    runner: DockerIsolationRunner,
) -> dict:
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    runtime, image = runner.inspect_environment()
    policy = runner.policy.to_dict()
    script = (
        _CANARY_SCRIPT.replace("__MEMORY_BYTES__", str(runner.policy.memory_mb * 1024 * 1024))
        .replace("__CPUS__", str(runner.policy.cpus))
        .replace("__PIDS__", str(runner.policy.pids_limit))
    )
    host_secret = secrets.token_urlsafe(32)
    with tempfile.TemporaryDirectory(prefix="harness-qualify-") as temporary:
        temporary_root = Path(temporary)
        (temporary_root / "host-secret.txt").write_text(host_secret, encoding="utf-8")
        workspace = temporary_root / "workspace"
        workspace.mkdir()
        canary_result = runner.run(workspace, ["python", "-c", script], container_name=f"harness-canary-{uuid.uuid4().hex[:12]}")
        if not canary_result.succeeded:
            raise ValueError("isolation canary process failed")
        try:
            canaries = json.loads(canary_result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("isolation canary returned invalid JSON") from exc
        for name in _REQUIRED_CANARIES:
            if canaries.get(name) is not True:
                raise ValueError(f"isolation canary failed: {name}")
        timeout_name = f"harness-timeout-{uuid.uuid4().hex[:12]}"
        timeout_result = runner.run(
            workspace,
            ["python", "-c", "import time; time.sleep(30)"],
            container_name=timeout_name,
            timeout_seconds=0.25,
        )
        canaries["timeout_enforced"] = timeout_result.timed_out
        canaries["cleanup_succeeded"] = not runner.container_exists(timeout_name)
        for name in ("timeout_enforced", "cleanup_succeeded"):
            if canaries[name] is not True:
                raise ValueError(f"isolation canary failed: {name}")
    identity = {"runtime": runtime, "image": image, "policy": policy, "canaries": canaries}
    record = {
        "schema_version": QUALIFICATION_SCHEMA_VERSION,
        "command": "isolation-qualify",
        "status": "qualified",
        "qualification_id": digest(identity)[:24],
        "qualified_at": datetime.now(timezone.utc).isoformat(),
        "runtime": runtime,
        "image": image,
        "policy": policy,
        "policy_sha256": digest(policy),
        "canaries": canaries,
        "host_secret_sha256": hashlib.sha256(host_secret.encode("utf-8")).hexdigest(),
    }
    record_path = root / "qualification.json"
    write_immutable(record_path, record)
    record_hash = hashlib.sha256(record_path.read_bytes()).hexdigest()
    write_immutable_bytes(root / "qualification.sha256", (record_hash + "\n").encode("ascii"))
    return record


def validate_qualification(
    qualification: Path | str,
    *,
    runner: DockerIsolationRunner,
) -> dict:
    record = _read_qualification(qualification)
    if record.get("schema_version") != QUALIFICATION_SCHEMA_VERSION or record.get("status") != "qualified":
        raise ValueError("qualification artifact is not qualified")
    policy = runner.policy.to_dict()
    if record.get("policy") != policy or record.get("policy_sha256") != digest(policy):
        raise ValueError("qualification policy mismatch")
    canaries = record.get("canaries")
    required = (*_REQUIRED_CANARIES, "timeout_enforced", "cleanup_succeeded")
    if not isinstance(canaries, dict) or any(canaries.get(name) is not True for name in required):
        raise ValueError("qualification canaries are incomplete or failed")
    identity = {
        "runtime": record.get("runtime"),
        "image": record.get("image"),
        "policy": policy,
        "canaries": canaries,
    }
    if record.get("qualification_id") != digest(identity)[:24]:
        raise ValueError("qualification identity mismatch")
    runtime, image = runner.inspect_environment()
    if record.get("runtime") != runtime:
        raise ValueError("qualification runtime mismatch")
    if record.get("image") != image:
        raise ValueError("qualification image mismatch")
    return record


def _read_qualification(qualification: Path | str) -> dict:
    root = Path(qualification).resolve()
    record_path = root if root.name == "qualification.json" else root / "qualification.json"
    digest_path = record_path.with_name("qualification.sha256")
    if not record_path.is_file() or not digest_path.is_file():
        raise ValueError("qualification artifact or digest is missing")
    actual_digest = hashlib.sha256(record_path.read_bytes()).hexdigest()
    expected_digest = digest_path.read_text(encoding="ascii").strip()
    if actual_digest != expected_digest:
        raise ValueError("qualification digest mismatch")
    try:
        record = json.loads(record_path.read_bytes())
    except json.JSONDecodeError as exc:
        raise ValueError("qualification artifact is invalid JSON") from exc
    return record


def policy_from_qualification(qualification: Path | str) -> IsolationPolicy:
    return IsolationPolicy.from_dict(_read_qualification(qualification).get("policy"))


def run_qualified(
    qualification: Path | str,
    workspace: Path | str,
    command: Sequence[str],
    *,
    runner: DockerIsolationRunner,
) -> RunResult:
    validate_qualification(qualification, runner=runner)
    staged = Path(workspace).resolve()
    staged.mkdir(parents=True, exist_ok=True)
    return runner.run(staged, command)
