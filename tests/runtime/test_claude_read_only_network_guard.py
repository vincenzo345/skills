"""Executable contract for the deployed-application mutation backstop."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


HOOK = Path(__file__).parents[2] / "skills" / "claude-rigor" / "hooks" / "read_only_network_guard.js"


def run_hook(tmp_path: Path, request: str, command: str) -> tuple[int, dict, str]:
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(json.dumps({
        "type": "user", "message": {"content": request},
    }) + "\n", encoding="utf-8")
    payload = {
        "hook_event_name": "PreToolUse", "tool_name": "Bash",
        "tool_input": {"command": command}, "transcript_path": str(transcript),
        "cwd": str(tmp_path),
    }
    result = subprocess.run(
        ["node", str(HOOK)], input=json.dumps(payload), capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    return result.returncode, json.loads(result.stdout) if result.stdout.strip() else {}, result.stderr


def test_blocks_direct_remote_request_for_options_investigation(tmp_path: Path) -> None:
    code, output, stderr = run_hook(
        tmp_path, "Investigate the latency and give me options.",
        "curl https://deployed.example/api/page-preview",
    )

    assert code == 0 and stderr == ""
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "GET and ordinary application usage are not exemptions" in output["hookSpecificOutput"]["permissionDecisionReason"]


def test_blocks_remote_probe_script_but_allows_local_benchmark(tmp_path: Path) -> None:
    remote = tmp_path / "probe_live.py"
    remote.write_text('requests.get("https://deployed.example/api/page-preview")\n', encoding="utf-8")
    local = tmp_path / "benchmark.py"
    local.write_text("print(sum(range(10)))\n", encoding="utf-8")

    _, blocked, _ = run_hook(tmp_path, "Diagnose this slow path.", "python probe_live.py")
    _, allowed, _ = run_hook(tmp_path, "Diagnose this slow path.", "python benchmark.py")

    assert blocked["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert allowed == {}


def test_allows_local_benchmark_that_names_the_investigated_route(tmp_path: Path) -> None:
    local = tmp_path / "benchmark.py"
    local.write_text(
        '"""Benchmark the manual_extraction page_preview render seam."""\nprint(1)\n',
        encoding="utf-8",
    )

    _, output, _ = run_hook(
        tmp_path, "Investigate the latency and give me options.", "python benchmark.py",
    )

    assert output == {}


def test_reading_a_script_that_contains_network_code_is_not_execution(tmp_path: Path) -> None:
    script = tmp_path / "deploy.ps1"
    script.write_text('Invoke-WebRequest "https://deployed.example/api/status"\n', encoding="utf-8")

    _, output, _ = run_hook(
        tmp_path, "Investigate the latency and give me options.",
        "grep -n Invoke-WebRequest deploy.ps1",
    )

    assert output == {}


def test_allows_passive_telemetry_and_explicit_live_authority(tmp_path: Path) -> None:
    _, passive, _ = run_hook(
        tmp_path, "Investigate the latency and give me options.",
        "aws logs start-query --log-group-name api",
    )
    _, authorized, _ = run_hook(
        tmp_path,
        "Investigate the latency. You may probe the deployed test app even if requests warm its cache.",
        "curl https://deployed.example/api/page-preview",
    )

    assert passive == {}
    assert authorized == {}


def test_allows_inline_parsing_of_passive_logs_with_route_text(tmp_path: Path) -> None:
    _, output, _ = run_hook(
        tmp_path,
        "Investigate the latency and give me options.",
        "aws logs start-query --query-string '/page-preview/' | python -c \"import json,sys; print(json.load(sys.stdin))\"",
    )

    assert output == {}


def test_change_request_is_not_treated_as_read_only(tmp_path: Path) -> None:
    _, output, _ = run_hook(
        tmp_path, "Investigate and implement the fix.",
        "curl https://deployed.example/api/page-preview",
    )

    assert output == {}
