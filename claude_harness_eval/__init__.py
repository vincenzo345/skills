"""Offline coding-agent task staging and acceptance verification."""

from .catalog import TaskSpec, get_task, list_tasks
from .runner import apply_reference, stage_task, validate_tasks, verify_task

__all__ = [
    "TaskSpec",
    "apply_reference",
    "get_task",
    "list_tasks",
    "stage_task",
    "validate_tasks",
    "verify_task",
]
