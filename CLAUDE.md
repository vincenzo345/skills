# Conventions for this repo

This repo holds agent skills. One skill, one folder, flat under `skills/`:

```
skills/<skill-name>/
  SKILL.md            <- required
  agents/openai.yaml  <- required (Codex metadata)
  <anything else>     <- reference docs, scripts, assets
```

Flat, no bucket folders. If this ever passes roughly ten skills, reorganise into
buckets then — `skills/<bucket>/<skill-name>/` is also supported by the installer.

## SKILL.md frontmatter

```yaml
---
name: <skill-name>          # must equal the folder name
description: <one line>     # see invocation below
---
```

## Invocation: user-invoked vs model-invoked

Every skill is one or the other. Pick deliberately and keep both harnesses in sync
— a skill is user-invoked in Claude Code and Codex, or in neither.

**Model-invoked** (the default) — the model or the human can reach it. Omit
`disable-model-invocation` from the frontmatter and omit the `policy` block from
`agents/openai.yaml`. The `description` is **model-facing**: keep rich trigger
phrasing ("Use when the user wants..., mentions..., asks for...") so auto-invocation
actually fires.

The test: *could the model usefully reach for this on its own?*

**User-invoked** — only the human typing its name can reach it. Set
`disable-model-invocation: true` in the frontmatter **and**
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The
`description` is **human-facing**: a one-line summary for someone browsing slash
commands. Strip the trigger lists.

## agents/openai.yaml

Required beside every `SKILL.md`. Holds Codex picker metadata, plus the policy
block for user-invoked skills.

Model-invoked:

```yaml
interface:
  display_name: "Agent Harness"
  short_description: "Scaffold a self-verifying build loop"
```

User-invoked adds:

```yaml
policy:
  allow_implicit_invocation: false
```

## When you add, rename, or remove a skill

1. Add or update its entry in `.claude-plugin/plugin.json`'s `skills` array.
   That array is the plugin's shipped set — a skill missing from it does not ship.
2. Add or update its entry in the top-level `README.md`, under **User-invoked** or
   **Model-invoked**, with the name linked to its `SKILL.md`.
3. Bump `version` in `.claude-plugin/plugin.json`. Claude Code uses that version to
   decide when installed users see an update.
4. Validate both manifests:

   ```bash
   claude plugin validate .claude-plugin/marketplace.json --strict
   claude plugin validate .claude-plugin/plugin.json
   ```

   The plugin manifest is validated **without** `--strict` on purpose. It emits one
   warning — "CLAUDE.md at the plugin root is not loaded as project context" — which
   is expected and intended: this file is authoring guidance for working *in* this
   repo, and deliberately does not ship as plugin context. Exit code is 0. Any
   *other* warning is a real problem.
5. Re-run `scripts/link-skills.ps1` so the local junctions match.

## Name collisions with skills from elsewhere

Skills from other packs may already be installed under the same name (for example
in `~/.claude/skills` or `~/.codex/skills`). **A skill in this repo wins.**
`link-skills.ps1` removes whatever occupies the slot and junctions ours in its
place. This is intended: the version we ship is the version we wrote and
understand. The script prints a line whenever it replaces a real directory.

## Local development

`scripts/link-skills.ps1` junctions every skill in this repo into `~/.claude/skills`
and `~/.codex/skills`. Junctions, not copies — so an edit here is live in the next
session, and a `git pull` updates every installed skill at once.

Do not use a `ln -s` based script on Windows: on this setup `ln -s` silently
creates real directory copies rather than links, which breaks the whole point.

## Style

No emojis, anywhere — including in scripts and printed output.
