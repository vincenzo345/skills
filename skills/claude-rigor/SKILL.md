---
name: claude-rigor
description: Install and inspect the correctness-focused Claude Code harness distributed with this skill.
disable-model-invocation: true
---

# Claude Rigor

This folder is both an Agent Skill and a self-contained Claude Code skills-directory
plugin. When installed under `~/.claude/skills/claude-rigor`, Claude Code automatically
loads its one-shot diagnosis preflight and task-aware completion review in new sessions.
The installer also adds a managed import to global `CLAUDE.md`, making the
`rigorous-engineer` file the single canonical, always-on operating contract while preserving
personal instructions. The agent definition remains available for explicit isolated use.

Use this skill when the user explicitly asks to inspect, verify, or explain the installed
harness. Inspect the sibling plugin files and report their actual configuration. Do not
claim the harness is active in an existing session; plugin activation occurs on a new
Claude Code session or after the /reload-plugins command.
