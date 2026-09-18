"""Agent adapter contracts and non-interactive vendor argv builders."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


_TASK_PROMPT = "Read TASK.md, implement the requested change, and verify it before claiming completion."


@dataclass(frozen=True)
class ClaudeAdapter:
    model: str
    effort: str = "high"
    prompt_file: Path | None = None

    def command(self, workspace: Path) -> list[str]:
        argv = [
            "claude", "-p", "--output-format", "stream-json", "--verbose",
            "--model", self.model, "--effort", self.effort,
            "--no-session-persistence", "--permission-prompts", "none",
        ]
        if self.prompt_file is not None:
            argv.extend(["--append-system-prompt-file", str(self.prompt_file)])
        argv.append(_TASK_PROMPT)
        return argv


@dataclass(frozen=True)
class CodexAdapter:
    model: str
    prompt_file: Path | None = None

    def command(self, workspace: Path) -> list[str]:
        argv = [
            "codex", "exec", "--json", "--ephemeral", "--sandbox", "workspace-write",
            "--model", self.model, "--cd", str(workspace),
        ]
        if self.prompt_file is not None:
            instruction = self.prompt_file.read_text(encoding="utf-8")
            argv.extend(["--config", f"developer_instructions={json.dumps(instruction, ensure_ascii=False)}"])
        argv.append(_TASK_PROMPT)
        return argv
