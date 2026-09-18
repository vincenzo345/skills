"""Command-line interface for the local coding-agent evaluation suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .catalog import list_tasks
from .experiment.config import load_campaign
from .experiment.controller import initialize_campaign, report_campaign, run_campaign, stop_campaign, validate_campaign_isolation
from .experiment.isolation import (
    DockerIsolationRunner,
    IsolationPolicy,
    policy_from_qualification,
    qualify_isolation,
    run_qualified,
)
from .experiment.optimization import (
    initialize_optimization,
    load_optimization_config,
    report_optimization,
    run_optimization,
    stop_optimization,
)
from .runner import SCHEMA_VERSION, apply_reference, stage_task, validate_tasks, verify_task


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m claude_harness_eval")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list", help="list available evaluation tasks")
    listing.add_argument("--json", action="store_true")

    for name in ("stage", "verify", "apply-reference"):
        command = commands.add_parser(name)
        command.add_argument("task_id")
        command.add_argument("workspace", type=Path)
        command.add_argument("--json", action="store_true")
    validation = commands.add_parser("validate", help="prove baseline failure and reference success")
    validation.add_argument("task_ids", nargs="*")
    validation.add_argument("--repeat", type=int, default=1)
    validation.add_argument("--json", action="store_true")

    doctor = commands.add_parser("doctor", help="validate an experiment configuration without model calls")
    doctor.add_argument("--config", type=Path, required=True)
    doctor.add_argument("--json", action="store_true")

    isolation = commands.add_parser("isolation", help="qualify and exercise the Docker isolation boundary")
    isolation_commands = isolation.add_subparsers(dest="isolation_command", required=True)
    qualification = isolation_commands.add_parser("qualify")
    qualification.add_argument("--root", type=Path, required=True)
    qualification.add_argument("--image", default="python:3.12-slim")
    qualification.add_argument("--timeout-seconds", type=float, default=30.0)
    qualification.add_argument("--json", action="store_true")
    isolated_run = isolation_commands.add_parser("run")
    isolated_run.add_argument("--qualification", type=Path, required=True)
    isolated_run.add_argument("--workspace", type=Path, required=True)
    isolated_run.add_argument("--json", action="store_true")
    isolated_run.add_argument("container_command", nargs=argparse.REMAINDER)

    experiment = commands.add_parser("experiment", help="manage a durable coding-agent experiment")
    experiment_commands = experiment.add_subparsers(dest="experiment_command", required=True)
    initialization = experiment_commands.add_parser("init")
    initialization.add_argument("--config", type=Path, required=True)
    initialization.add_argument("--root", type=Path, required=True)
    initialization.add_argument("--json", action="store_true")
    for name in ("run", "resume", "report"):
        command = experiment_commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--json", action="store_true")
    stopping = experiment_commands.add_parser("stop")
    stopping.add_argument("--root", type=Path, required=True)
    stopping.add_argument("--reason", required=True)
    stopping.add_argument("--json", action="store_true")

    optimize = commands.add_parser("optimize", help="run a durable Claude harness optimization loop")
    optimize_commands = optimize.add_subparsers(dest="optimize_command", required=True)
    optimize_init = optimize_commands.add_parser("init")
    optimize_init.add_argument("--config", type=Path, required=True)
    optimize_init.add_argument("--root", type=Path, required=True)
    optimize_init.add_argument("--json", action="store_true")
    for name in ("run", "resume", "report"):
        command = optimize_commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--json", action="store_true")
    optimize_stop = optimize_commands.add_parser("stop")
    optimize_stop.add_argument("--root", type=Path, required=True)
    optimize_stop.add_argument("--reason", required=True)
    optimize_stop.add_argument("--json", action="store_true")
    return parser


def _emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if result["command"] == "list":
        for task in result["tasks"]:
            print(f"{task['id']}: {task['title']} [{task['category']}]")
    else:
        print(f"{result['command']} {result.get('task_id', '')}: {result.get('status', 'ok')}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "list":
            result = {
                "schema_version": SCHEMA_VERSION,
                "command": "list",
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "category": task.category,
                        "tags": list(task.tags),
                    }
                    for task in list_tasks()
                ],
            }
        elif args.command == "stage":
            result = stage_task(args.task_id, args.workspace)
        elif args.command == "verify":
            result = verify_task(args.task_id, args.workspace)
        elif args.command == "apply-reference":
            result = apply_reference(args.task_id, args.workspace)
        elif args.command == "doctor":
            config = load_campaign(args.config)
            qualification_id = None
            if config.mode == "live":
                qualification_id = validate_campaign_isolation(config)["qualification_id"]
            result = {
                "schema_version": 1,
                "command": "doctor",
                "status": "ready" if config.mode == "fake" else "live-config-valid",
                "mode": config.mode,
                "scheduled_runs": len(config.task_ids) * len(config.agents) * config.repetitions,
            }
            if qualification_id is not None:
                result["qualification_id"] = qualification_id
        elif args.command == "isolation":
            if args.isolation_command == "qualify":
                if args.timeout_seconds <= 0:
                    raise ValueError("timeout-seconds must be positive")
                policy = IsolationPolicy(image=args.image, timeout_seconds=args.timeout_seconds)
                result = qualify_isolation(args.root, runner=DockerIsolationRunner(policy))
            else:
                command = list(args.container_command)
                if command[:1] == ["--"]:
                    command = command[1:]
                if not command:
                    raise ValueError("isolation run requires a command after --")
                policy = policy_from_qualification(args.qualification)
                execution = run_qualified(
                    args.qualification,
                    args.workspace,
                    command,
                    runner=DockerIsolationRunner(policy),
                )
                result = {
                    "schema_version": 1,
                    "command": "isolation-run",
                    "status": "completed" if execution.succeeded else "failed",
                    **execution.to_dict(),
                }
        elif args.command == "experiment":
            if args.experiment_command == "init":
                result = initialize_campaign(load_campaign(args.config), args.root)
            elif args.experiment_command in {"run", "resume"}:
                result = run_campaign(args.root)
            elif args.experiment_command == "report":
                result = report_campaign(args.root)
            else:
                result = stop_campaign(args.root, args.reason)
        elif args.command == "optimize":
            if args.optimize_command == "init":
                result = initialize_optimization(load_optimization_config(args.config), args.root)
            elif args.optimize_command in {"run", "resume"}:
                result = run_optimization(args.root)
            elif args.optimize_command == "report":
                result = report_optimization(args.root)
            else:
                result = stop_optimization(args.root, args.reason)
        else:
            result = validate_tasks(args.task_ids or None, repeat=args.repeat)
        _emit(result, args.json)
        if args.command in {"verify", "validate"} and not result["passed"]:
            return 1
        if args.command == "isolation" and result["status"] == "failed":
            return 1
        if args.command == "optimize" and result.get("status") == "blocked":
            return 1
        return 0
    except (KeyError, ValueError) as exc:
        error = {
            "schema_version": SCHEMA_VERSION,
            "command": args.command,
            "status": "error",
            "error": str(exc),
        }
        _emit(error, getattr(args, "json", False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
