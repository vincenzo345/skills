# Claude instruction optimization outcome frame

## Outcome

Improve Claude Code's coding-task reliability through global instructions, measured by executable acceptance tests rather than transcript appearance. Continue the test → diagnose → revise → retest loop until the promoted instructions reach the Codex reference band on held-out tasks or targeted prompt-level interventions reach a reproducible plateau.

## Conditions

- **Claude clean baseline:** the same installed CLI, account, model, effort, task, and workspace policy invoked with `--safe-mode`, which disables `CLAUDE.md` and other customizations.
- **Claude champion/challenger:** fresh sessions using a content-hashed instruction candidate, with no session persistence.
- **Codex reference:** fresh ephemeral Codex sessions on the same task revision and executable evaluator.
- **Oracle:** evaluator-owned acceptance tests run after the agent exits; agents cannot read the oracle.

## Promotion and completion

A challenger is promoted only when it improves validation by at least one whole task over the current champion and does not worsen scope violations or false completion. Development-only gains do not count.

The result is satisfactory when an untouched holdout, repeated three times, shows promoted Claude within one whole accepted task of Codex and no worse on scope-violation or false-completion guardrails. If that threshold is not reached, plateau is established only after three consecutive failure-derived, materially distinct candidates fail to improve validation by at least one task.

The winning candidate must then be installed verbatim in `C:\Users\vince\.claude\CLAUDE.md`, preserving the original Graphify instructions, and rerun in fresh sessions. The final report must identify concrete before-fail/after-pass cases. Static prompt checks and harness unit tests are supporting evidence only, never behavioral proof.

## Operational boundary

Use only synthetic repositories. Bound each live run by wall time, fresh workspace, non-persistent session, and least privilege. Checkpoint after each 24-invocation tranche; provider throttling or authentication expiry pauses resumably. Commit, external publication, and deployment outside the local global instruction installation are excluded.
