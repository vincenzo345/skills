# Zero-cost parity controller implementation

## Implemented

- Added strict versioned TOML configuration with exact Claude/Codex agents, deterministic task schedule, usage/run ceilings, and fail-closed live-mode prerequisites.
- Added immutable campaign and per-run manifests, append-only events, atomic state/report writes, stable SHA-256 run IDs, result digests, conflict detection, durable stop, and crash reconciliation.
- Added deterministic fake conditions that exercise all existing tasks through the real stage/apply-reference/verify seam without a model call.
- Added Claude Code and Codex non-interactive argv builders without launching either vendor.
- Added `doctor` and `experiment init|run|resume|stop|report` CLI commands while preserving every existing command.
- Added JSON and Markdown reporting, a checked-in 20-task fake campaign, documentation, and `.harness-runs/` exclusion.
- Added eight public-seam tests covering fake execution, resume idempotency, lost-state reconciliation, stop, immutable-root conflict, result tamper detection, live-mode rejection, vendor argv, and CLI round trip.

## Deliberately withheld

Live subprocess execution remains disabled even for a syntactically valid live configuration. No model was invoked, no credential was read, no quota was spent, and no global Claude/Codex prompt or hook was changed. External isolation qualification, sealed task stores, live baselines, optimizer rounds, and final global promotion remain later authorized work.

## Changed surfaces

- `claude_harness_eval/experiment/`
- `claude_harness_eval/__main__.py`
- `tests/runtime/test_claude_harness_experiment.py`
- `docs/examples/claude-harness-campaign.toml`
- `docs/claude-harness-evals.md`
- `.gitignore`
