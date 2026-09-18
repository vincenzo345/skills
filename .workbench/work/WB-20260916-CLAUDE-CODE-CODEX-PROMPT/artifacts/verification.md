# Specification verification

## Static result

- Prompt length: 74 lines and 897 words, below Claude Code's recommended 200-line ceiling for `CLAUDE.md`.
- Placement: copy the specification to `~/.claude/CLAUDE.md` for personal instructions across all projects.
- Loading check: start a fresh Claude Code session and run `/memory`; the user-level file should be listed.
- Literal system-prompt distinction: Claude Code injects `CLAUDE.md` as user context after its built-in system prompt. Use `--append-system-prompt` on each invocation only when literal system-message placement is required.

## Acceptance mapping

| Reported risk or requirement | Operative instruction |
| --- | --- |
| Implementation is mistaken for completion | Editing ends at “ready to be challenged”; completion requires the Close gate. |
| Insufficient investigation | Orient requires instructions, repository state, affected implementation, callers, tests, configuration, data boundaries, error paths, and relevant variants. |
| Convenient test is overclaimed | Falsify requires a meaningful public seam, actual output inspection, and evidence matching the claimed environment, seam, and journey. |
| Happy-path confidence hides defects | Falsify requires realistic failure cases, skeptical diff review, and checking the most plausible remaining failure. |
| Claude stops after planning | Request interpretation requires implementation and verification when a change was requested and safe in-scope work remains. |
| Failures are hidden in “done” | Close separates verified, inferred, unverified, blocked, and pre-existing failures. |
| Thoroughness becomes ceremony | Proportionality scales evidence with uncertainty, blast radius, and risk. |
| Prompt is treated as enforcement | Enforcement boundary assigns critical invariants to tests, hooks, permissions, types, linters, and CI. |

## Review disposition

All requested static criteria are represented by concrete, checkable instructions. The wording uses four repeated leading terms—Orient, Act, Falsify, Close—to anchor execution while keeping each completion boundary co-located with its rules. No repository-specific commands are cached globally.

The remaining uncertainty is behavioral efficacy: only repeated comparative tasks against representative repositories can measure how strongly a specific Claude model follows the contract. That evaluation would consume Claude usage and may expose repository content, so it was not run without separate authorization.
