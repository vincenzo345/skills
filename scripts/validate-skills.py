#!/usr/bin/env python3
"""Validate the portable skill collection without third-party dependencies."""

from __future__ import annotations

import re
import sys
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
BUILT_IN_COMMANDS = {"compact", "tmp"}  # `tmp` appears as a documented path, not a skill.
PORTABLE_FLOW_SKILLS = {
    "code-review",
    "diagnosing-bugs",
    "feature-planner",
    "openai-docs",
    "prototype",
    "research",
    "resolving-merge-conflicts",
    "tdd",
    "workbench",
}
WORKBENCH_COMPANION_SKILLS = {
    "code-review",
    "diagnosing-bugs",
    "feature-planner",
    "openai-docs",
    "prototype",
    "research",
    "resolving-merge-conflicts",
    "tdd",
}
A4L_MARKERS = re.compile(
    r"(?i)a4l-|applications4life|illustration report generator|nationwide|\baig\b|"
    r"\bsqs\b|\brls\b|\bphi\b|42/42|term csv"
)
WORKFLOW_CONTRACTS: dict[str, list[tuple[str, str]]] = {
    "skills/code-review/SKILL.md": [
        ("review includes untracked work", r"in-scope untracked files"),
        ("review reopens the proof owner", r"artifact that owns the unmet criterion"),
    ],
    "skills/prototype/SKILL.md": [
        ("prototypes are production-excluded", r"production-excluded from day one"),
        ("prototype data defaults synthetic", r"Synthetic, disposable state by default"),
    ],
    "skills/workbench/SKILL.md": [
        ("new work requires an explicit signal", r"Start a new work item only when the user explicitly names Workbench"),
        ("ordinary requests are valid intake", r"Treat the user's natural description as valid intake"),
        ("inspect before questions", r"Inspect the current repository and every accessible reference.*before asking questions"),
        ("captured intake uses atomic route start", r"start atomically with `route-and-start`"),
        ("specialists do not imply subagents", r"specialist method normally runs in the current agent"),
        ("artifacts can cover several activities", r"One canonical artifact may satisfy several included activities"),
    ],
}

MAX_ENTRYPOINT_BYTES = {
    "workbench": 8500,
}


def frontmatter(text: str, path: Path) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from error

    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*?)\s*$", line)
        if not match:
            raise ValueError(f"{path}: unsupported frontmatter line {line!r}")
        key, value = match.groups()
        if key in values:
            raise ValueError(f"{path}: duplicate frontmatter key {key!r}")
        values[key] = value.strip('"\'')
    return values


def parse_openai_yaml(text: str, path: Path) -> dict[str, dict[str, str]]:
    """Parse the deliberately small two-level mapping used by agents/openai.yaml."""
    result: dict[str, dict[str, str]] = {}
    section: str | None = None

    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise ValueError(f"{path}:{number}: tabs are not valid indentation")
        top = re.fullmatch(r"([a-z][a-z0-9_]*):\s*", raw)
        if top:
            section = top.group(1)
            if section in result:
                raise ValueError(f"{path}:{number}: duplicate section {section!r}")
            result[section] = {}
            continue
        child = re.fullmatch(r"  ([a-z][a-z0-9_]*):\s*(.+?)\s*", raw)
        if not child or section is None:
            raise ValueError(f"{path}:{number}: unsupported YAML shape {raw!r}")
        key, value = child.groups()
        if key in result[section]:
            raise ValueError(f"{path}:{number}: duplicate key {section}.{key}")
        if value[0:1] in {'"', "'"} and value[-1:] != value[0]:
            raise ValueError(f"{path}:{number}: unclosed quoted value")
        result[section][key] = value.strip('"\'')

    return result


def relative_links(text: str) -> list[str]:
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    return [
        link.split("#", 1)[0]
        for link in links
        if link
        and not link.startswith(("http://", "https://", "mailto:", "#", "/"))
        and not link.startswith("<")
    ]


def command_references(text: str) -> set[str]:
    return set(re.findall(r"`/([a-z0-9][a-z0-9-]*)`", text))


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS_ROOT.glob("*/SKILL.md"))
    parsed: list[tuple[Path, str, str, dict[str, str]]] = []
    names: defaultdict[str, list[Path]] = defaultdict(list)

    if not skill_files:
        errors.append("No skills found under skills/<name>/SKILL.md")

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        try:
            metadata = frontmatter(text, skill_file)
        except ValueError as error:
            errors.append(str(error))
            continue
        expected_name = skill_file.parent.name
        parsed.append((skill_file, expected_name, text, metadata))
        if metadata.get("name"):
            names[metadata["name"]].append(skill_file)

    for name, paths in names.items():
        if len(paths) > 1:
            errors.append(f"duplicate skill name {name!r}: {', '.join(map(str, paths))}")

    known_commands = set(names) | BUILT_IN_COMMANDS

    for relative_path, checks in WORKFLOW_CONTRACTS.items():
        contract_path = ROOT / relative_path
        if not contract_path.is_file():
            errors.append(f"{contract_path}: missing workflow contract source")
            continue
        contract_text = contract_path.read_text(encoding="utf-8")
        for label, pattern in checks:
            if not re.search(pattern, contract_text, re.IGNORECASE | re.DOTALL):
                errors.append(f"{contract_path}: missing invariant: {label}")

    for skill_file, expected_name, text, metadata in parsed:
        skill_dir = skill_file.parent
        if metadata.get("name") != expected_name:
            errors.append(
                f"{skill_file}: name {metadata.get('name')!r} does not match folder {expected_name!r}"
            )
        if not metadata.get("description"):
            errors.append(f"{skill_file}: missing description")
        if limit := MAX_ENTRYPOINT_BYTES.get(expected_name):
            size = len(text.encode("utf-8"))
            if size > limit:
                errors.append(
                    f"{skill_file}: {size} bytes exceeds the {limit}-byte entrypoint budget"
                )

        openai_yaml = skill_dir / "agents" / "openai.yaml"
        openai_data: dict[str, dict[str, str]] = {}
        if not openai_yaml.is_file():
            errors.append(f"{openai_yaml}: missing companion metadata")
        else:
            try:
                openai_data = parse_openai_yaml(
                    openai_yaml.read_text(encoding="utf-8"), openai_yaml
                )
            except ValueError as error:
                errors.append(str(error))

            interface = openai_data.get("interface", {})
            if not interface.get("display_name"):
                errors.append(f"{openai_yaml}: missing interface.display_name")
            if not interface.get("short_description"):
                errors.append(f"{openai_yaml}: missing interface.short_description")

            explicit_only = metadata.get("disable-model-invocation") == "true"
            codex_explicit_only = (
                openai_data.get("policy", {}).get("allow_implicit_invocation") == "false"
            )
            if explicit_only != codex_explicit_only:
                errors.append(f"{skill_dir}: Claude/Codex invocation policies disagree")

        for link in relative_links(text):
            if link == "link":  # Placeholder in Markdown templates.
                continue
            if not (skill_dir / link).resolve().exists():
                errors.append(f"{skill_file}: broken relative link {link!r}")

        for command in sorted(command_references(text) - known_commands):
            errors.append(f"{skill_file}: unknown nested skill reference `/{command}`")

        if expected_name in PORTABLE_FLOW_SKILLS:
            if ".scratch/" in text:
                errors.append(f"{skill_file}: hardcodes the local tracker path")
            if A4L_MARKERS.search(text):
                errors.append(f"{skill_file}: contains repository-specific A4L language")

        catalog = ROOT / "README.md"
        catalog_text = catalog.read_text(encoding="utf-8")
        entry = f"./skills/{expected_name}/SKILL.md"
        if entry not in catalog_text:
            errors.append(f"{catalog}: missing {expected_name} catalog entry")

    manifest_path = ROOT / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        declared = {Path(value).name for value in manifest.get("skills", [])}
        discovered = {skill_file.parent.name for skill_file in skill_files}
        missing_companions = WORKBENCH_COMPANION_SKILLS - discovered
        if missing_companions:
            errors.append(
                f"Workbench companion skills are missing from disk: {sorted(missing_companions)}"
            )
        if declared != discovered:
            errors.append(
                f"{manifest_path}: declared skills differ from disk "
                f"(missing={sorted(discovered - declared)}, extra={sorted(declared - discovered)})"
            )
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{manifest_path}: cannot read valid JSON: {error}")

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(parsed)} skills: names, metadata shape, invocation policies, "
        "nested references, links, catalog, manifest, and portability checks pass."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
