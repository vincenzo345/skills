"""Check the promoted skill package used by the v2 pilot."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping
)


def _yaml(text: str, path: Path) -> dict:
    try:
        value = yaml.load(text, Loader=UniqueKeyLoader)
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def _skill_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"{path}: missing YAML frontmatter")
    return _yaml(parts[1], path)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{manifest_path}: {exc}"]

    entries = manifest.get("skills")
    if not isinstance(entries, list) or not all(isinstance(x, str) for x in entries):
        return [f"{manifest_path}: skills must be a list of paths"]
    if len(entries) != len(set(entries)):
        errors.append(f"{manifest_path}: duplicate skill path")

    promoted = {
        f"./skills/{bucket}/{path.name}"
        for bucket in ("engineering", "productivity")
        for path in (root / "skills" / bucket).iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    listed = set(entries)
    for missing in sorted(promoted - listed):
        errors.append(f"{manifest_path}: promoted skill missing: {missing}")
    for extra in sorted(listed - promoted):
        errors.append(f"{manifest_path}: non-promoted or missing skill: {extra}")

    top_readme = (root / "README.md").read_text(encoding="utf-8")
    for entry in sorted(promoted):
        folder = root / entry.removeprefix("./")
        name = folder.name
        bucket = folder.parent.name
        skill_path = folder / "SKILL.md"
        ui_path = folder / "agents" / "openai.yaml"
        try:
            metadata = _skill_metadata(skill_path)
            ui = _yaml(ui_path.read_text(encoding="utf-8"), ui_path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        if metadata.get("name") != name:
            errors.append(f"{skill_path}: name must be {name}")
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            errors.append(f"{skill_path}: description must be nonempty text")
        explicit = metadata.get("disable-model-invocation", False)
        if not isinstance(explicit, bool):
            errors.append(f"{skill_path}: disable-model-invocation must be boolean")
        policy = ui.get("policy", {})
        if not isinstance(policy, dict):
            errors.append(f"{ui_path}: policy must be a mapping")
        else:
            implicit = policy.get("allow_implicit_invocation", True)
            if not isinstance(implicit, bool) or implicit == explicit:
                errors.append(f"{ui_path}: invocation policy disagrees with SKILL.md")
        interface = ui.get("interface")
        if not isinstance(interface, dict) or not all(
            isinstance(interface.get(key), str) and interface[key].strip()
            for key in ("display_name", "short_description")
        ):
            errors.append(f"{ui_path}: missing display_name or short_description")
        if f"({entry}/SKILL.md)" not in top_readme:
            errors.append(f"README.md: missing link to {entry}")
        bucket_readme = (root / "skills" / bucket / "README.md").read_text(encoding="utf-8")
        if f"(./{name}/SKILL.md)" not in bucket_readme:
            errors.append(f"skills/{bucket}/README.md: missing link to {name}")
        if not (root / "docs" / bucket / f"{name}.md").is_file():
            errors.append(f"docs/{bucket}/{name}.md: missing promoted skill page")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = validate(repository)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("Promoted skill package is consistent")
