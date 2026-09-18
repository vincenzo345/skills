# Outcome frame: Claude Code parity loop

## Outcome

Produce an implementation-ready plan for a resumable experiment controller that compares Claude Code with a fixed Codex baseline, improves Claude's explicit instruction and completion-gate configuration, and stops with one of two bounded conclusions:

1. **Operational parity:** Claude meets the pre-registered suite-level non-inferiority and reliability gates against the frozen Codex baseline.
2. **Plateau within scope:** Claude does not meet parity, but the authorized search space, rounds, and usage budget have been exhausted without a qualifying improvement.

“Parity” applies only to the pinned models, CLI versions, permissions, task distribution, resource limits, and campaign manifest. “Plateau” replaces the unverifiable claim that Claude is universally “maxed.”

## Observable completion evidence

- A named module and CLI design covers preflight, baseline, candidate generation, evaluation, promotion, reporting, interruption, and resume.
- Metrics and terminal rules are fixed before a credentialed run.
- Existing public tasks are development evidence; final claims use separately sealed validation and holdout tasks.
- Each run has an immutable manifest, raw event log, final diff, verifier result, claim-calibration result, usage data, and content hashes.
- No paid or enterprise-authenticated run can start without explicit model identifiers, a total usage cap, concurrency and time limits, and a passed isolation preflight.
- Codex optimization starts only after the Claude result and comparison baseline are frozen.

## Boundaries

In scope: a repository implementation plan, current product research, statistical and safety defaults, durable artifact semantics, and a phased delivery/test plan.

Out of scope for this destination: invoking either model, changing global prompts, provisioning credentials, spending quota or money, implementing the controller, publishing results, committing, or deploying.

## Defaults

- The current 20 tasks are development/smoke material because they are already visible.
- Actual campaign access, models, and budget are required configuration with no paid defaults.
- The first optimizer is deterministic champion–challenger search; GEPA is an optional adapter after the evaluator is qualified.
- Results are append-only JSONL plus immutable JSON/text artifacts; no database is introduced.
