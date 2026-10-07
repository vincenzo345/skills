# Installation for this fork

The top-level [README](../README.md) is the user-facing installation guide. This file records the maintainer steps and their reason.

## Codex on Windows

Run `python scripts/install_global_v2.py` from this checkout. The script reads the promoted skill list from `.claude-plugin/plugin.json`, links those skills into `~/.agents/skills` and `~/.codex/skills`, and retires names removed or renamed by this fork. Re-run it after a promoted-skill change and start a new Codex session to refresh discovery.

## Claude Code

Commit the change first, then run `python scripts/prepare_claude_plugin.py` to get a clean snapshot path for that commit. Add the path as the `skillsrepo-v2` marketplace and install `skillsrepo-v2@skillsrepo-v2`.

For an update, remove the existing `skillsrepo-v2` marketplace, add the new snapshot path, and install the plugin again. Removing the marketplace also uninstalls its plugin. Verify the version and skill inventory with `claude plugin details skillsrepo-v2@skillsrepo-v2`, then start a new Claude Code session.

The old `mattpocock-skills@claude-plugins-official` plugin is not this fork and must remain uninstalled to avoid duplicate skills. Matt's repository is a read-only source; releases and pushes belong to `vincenzo345/skills`.
