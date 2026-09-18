# Local verification

## Passed checks

- `python -B -m pytest tests/runtime -q -p no:cacheprovider`: 115 passed in 125.21 seconds.
- Focused experiment and evaluator tests: 17 passed in 13.10 seconds.
- `python -B -m claude_harness_eval validate --repeat 2 --json`: all 20 tasks passed the author gate twice; 40 untouched baselines failed and 40 reference overlays passed.
- Full fake campaign: 40 runs completed; fake Claude/reference passed 20/20 and fake Codex/no-op passed 0/20.
- Campaign resume after completion launched 0 runs.
- Independent digest scan verified all 40 stored `result.json` artifacts against their SHA-256 sidecars.
- Workbench foundation validator passed 10 comparison cases, 10 negative contract cases, 14 record instances, 5 scenarios, and 12 schemas.
- Skill validator passed all 11 skills.
- Python bytecode compilation and `git diff --check` passed.

## Behavior covered

Strict configuration, fail-closed live prerequisites, immutable-root conflict, stable scheduling, public verifier integration, result hashing and tamper rejection, lost-state reconciliation, idempotent resume, durable stop, vendor argv construction, JSON/Markdown reporting, CLI compatibility, and the existing evaluation suite.

## Proof boundary

No Claude or Codex model ran. The labels `fake-claude` and `fake-codex` identify deterministic controller fixtures, not vendor results. No enterprise credential, API access, spend, external isolation backend, sealed task set, global prompt, or hook was used. This proof establishes a locally verified zero-cost controller foundation only.
