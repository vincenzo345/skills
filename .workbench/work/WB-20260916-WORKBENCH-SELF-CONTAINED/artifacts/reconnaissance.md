# Reconnaissance and standards

- `research` was already present in `skills/`, the README catalog, and the Claude plugin manifest.
- `feature-planner` and `openai-docs` were available only from the active Codex environment, so a different harness or a selective repository installation could not reproduce the observed method set.
- Workbench routing allowed arbitrary installed specialists and converted a missing suitable skill into a blocker. That made environment composition part of an otherwise portable route.
- Repository conventions require a flat skill directory, `SKILL.md`, `agents/openai.yaml`, README and plugin entries, a plugin version bump, and both repository and plugin validation.

The bounded design is to ship original harness-neutral versions of the two missing companions, retain the existing research skill, describe bundled companions by capability, and enforce the companion set in repository validation. Workbench runtime schemas and persisted data are unaffected.
