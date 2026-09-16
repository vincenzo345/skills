# Workbench adherence hardening reconnaissance

## Existing seams

- `skills/workbench/SKILL.md` is the smallest always-read location for repository preflight, method composition, and decision-fidelity guardrails.
- `references/intake.md` currently begins with `capture-intake` and has no repository/store resolution prerequisite.
- `references/routing.md` makes optional specialist use sound discretionary even when another installed skill independently triggers.
- `references/stage-gates.md` protects consent and authorization but does not say that one question should cover one decision dimension.
- `tests/runtime/conftest.py` exposes the Workbench CLI and file-backed records as black-box seams.
- `tests/comparison/` contains structured behavioral oracles, but no runner invokes a model; adherence regressions therefore need explicit conformance cases plus a validator, with that limitation stated.
- `docs/agents/issue-tracker.md` places unpublished implementation issues under `.scratch/<effort>/issues/`.

## Bounded change

Edit only the Workbench instructions and add conformance-eval fixtures plus their repository validator. Record, but do not implement, runtime changes for typed claim provenance, proof-bound obligations and post-start amendments, and repository/authorization source identity.

No persistence schema, Workbench runtime behavior, installed skill metadata, or external manual-extraction work item changes in this increment.
