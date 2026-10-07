"""Install promoted v2 skills for Codex and retire conflicting global entries on Windows.

Existing real directories are moved outside skill-discovery roots as a recovery backup.
The repository remains the live source for the installed junctions.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
USER_DIR = Path.home()
AGENTS = USER_DIR / ".agents" / "skills"
CODEX = USER_DIR / ".codex" / "skills"
CLAUDE = USER_DIR / ".claude" / "skills"
BACKUP = USER_DIR / ".agents" / "skills-backups" / (
    "before-v2-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
)


def contained(path: Path, parent: Path) -> bool:
    return os.path.commonpath((os.path.abspath(path), os.path.abspath(parent))) == os.path.abspath(parent)


def retire(path: Path, parent: Path) -> None:
    if not contained(path, parent):
        raise ValueError(f"refusing path outside {parent}: {path}")
    if not os.path.lexists(path):
        return
    if os.path.isjunction(path):
        os.rmdir(path)  # Removes the junction itself; the target stays intact.
    elif path.is_symlink():
        path.unlink()
    else:
        destination = BACKUP / parent.parent.name / parent.name / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(destination)
        shutil.move(str(path), str(destination))
        print(f"Backed up {path} -> {destination}")


def junction(path: Path, target: Path) -> None:
    if not target.is_dir() or not (target / "SKILL.md").is_file():
        raise FileNotFoundError(target / "SKILL.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(path), str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode or not os.path.isjunction(path):
        raise RuntimeError(f"could not link {path} to {target}: {result.stdout} {result.stderr}")


def retire_workbench_hooks() -> None:
    config = CLAUDE / "claude-rigor" / "hooks" / "hooks.json"
    if not config.is_file():
        return
    data = json.loads(config.read_text(encoding="utf-8"))
    hooks = data.get("hooks", {})
    removed = 0
    for event, groups in list(hooks.items()):
        kept = []
        for group in groups:
            commands = group.get("hooks", [])
            active = [
                item for item in commands
                if not any(
                    token in item.get("command", "")
                    for token in (
                        "workbench_prompt_router.js",
                        "workbench_new_item_guard.js",
                        "performance_budget_guard.js",
                    )
                )
            ]
            removed += len(commands) - len(active)
            if active:
                kept.append({**group, "hooks": active})
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    if removed:
        destination = BACKUP / "claude-rigor-hooks.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config, destination)
        config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Retired {removed} Workbench hook registrations; backup: {destination}")


def main() -> None:
    if os.name != "nt":
        raise SystemExit("This installer uses Windows junctions; install manually on other systems.")
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    sources = {Path(entry).name: ROOT / entry.removeprefix("./") for entry in manifest["skills"]}
    if len(sources) != len(manifest["skills"]):
        raise ValueError("duplicate skill name across buckets")
    for source in sources.values():
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(source / "SKILL.md")

    for base in (AGENTS, CODEX, CLAUDE):
        base.mkdir(parents=True, exist_ok=True)
    for name, source in sorted(sources.items()):
        retire(AGENTS / name, AGENTS)
        retire(CODEX / name, CODEX)
        junction(AGENTS / name, source)
        junction(CODEX / name, AGENTS / name)

    # Claude receives v2 through its plugin; retire older standalone copies.
    for name in ("workbench", "wait-what", "ask-matt", "setup-matt-pocock-skills", "implement", "diagnosing-bugs", "to-record", "to-scope"):
        retire(CLAUDE / name, CLAUDE)
    for base in (AGENTS, CODEX):
        for name in ("workbench", "wait-what", "ask-matt", "setup-matt-pocock-skills"):
            retire(base / name, base)
    retire_workbench_hooks()
    print(f"Installed {len(sources)} v2 skills for Codex from {ROOT}")
    print("Retired superseded global skill entry points. Restart Codex and Claude Code.")


if __name__ == "__main__":
    main()
