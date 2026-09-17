---
name: claude-rigor
description: Install and inspect the correctness-focused Claude Code harness distributed with this skill.
disable-model-invocation: true
---

# Claude Rigor

This folder is both an Agent Skill and a self-contained Claude Code skills-directory
plugin. When installed under `~/.claude/skills/claude-rigor`, Claude Code automatically
loads its default `rigorous-engineer` agent and task-aware one-shot completion-review hook in new
sessions. It does not edit or replace the user's global `CLAUDE.md` or `settings.json`.

Use this skill when the user explicitly asks to inspect, verify, or explain the installed
harness. Inspect the sibling plugin files and report their actual configuration. Do not
claim the harness is active in an existing session; plugin activation occurs on a new
Claude Code session or after the /reload-plugins command.
