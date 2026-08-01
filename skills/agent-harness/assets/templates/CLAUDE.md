# CLAUDE.md — {{PROJECT_NAME}} build harness

This project is built by a **Planner → Generator → Evaluator** long-running-agent harness: a
file-based, adversarially-verified build loop. Three roles with separate context windows
coordinate only through files in `.harness/`, so no single agent both builds and grades its own
work — the reason the loop stays honest over long runs.

{{PITCH}}

You may be invoked as one of three roles. Which one is stated in your system prompt (see
`.claude/agents/`) or by the `/harness-run` command. This file holds the shared rules for every role.

## The loop (source of truth)

1. **Plan** — if `.harness/plan.json` is missing, the Planner writes it: high-level sprints only.
2. **For each sprint** whose state in `.harness/progress.json` is not `passed`:
   a. **Negotiate the contract.** Generator proposes `.harness/contract.json` (concrete, testable
      criteria + the exact tests that prove them). Evaluator reviews into
      `.harness/contract_review.json`. Loop until `agreed: true`.
   b. **Build.** Generator implements ONLY this sprint against the agreed contract, writes/updates
      tests, runs them, and commits when green.
   c. **Evaluate.** Evaluator independently builds, runs the tests, EXERCISES the artifact (see
      below), captures evidence, and writes `.harness/verdict.json` scoring against the contract and
      `.harness/rubric.md`.
   d. **Branch on verdict:** `pass` → mark the sprint `passed`, move on. `revise` → Generator reads
      the critique and tries again. `restart` → reset the sprint (`git reset --hard sprint-N-start`)
      and rebuild from scratch.
3. Every round, append one line to `.harness/journal.jsonl` (schema below).

## Invariants — never violate these

{{INVARIANTS}}

## How the artifact is built & exercised

- **Build:** `ci/build.sh` — wraps: `{{BUILD_CMD}}`
- **Test:**  `ci/test.sh`  — wraps: `{{TEST_CMD}}`
- **Exercise (how the Evaluator actually USES the artifact, not just reads code):** {{EXERCISE}}

The split matters: tests prove the *mechanism*; exercising proves it actually *works and feels right*.
Anything with a mechanism should be a test; anything that is taste is evidence the Evaluator captures
and grades against the rubric and the calibration references in `.harness/references/`.

## Guardrails for every role

- Touch only source code, tests, `ci/`, and `.harness/`. Never edit `CLAUDE.md`, `docs/`, or
  `.claude/` unless explicitly asked.
- Build artifacts/config in code where you can, so everything is reviewable in the diff.
- Commit after every green sprint: `sprint N: <name> — passed`. Tag each sprint start
  `sprint-N-start` so a `restart` can reset to it.
- State lives on disk, not in your context. Before acting, read `.harness/progress.json`,
  `.harness/plan.json`, and the current `.harness/contract.json`. Leave breadcrumbs in
  `journal.jsonl` so a fresh context can pick up.
- Prefer JSON for state files (models overwrite Markdown too eagerly).

## Files

```
.harness/plan.json          # sprints
.harness/progress.json      # {"current": N, "sprints": {"1":"passed","2":"pending",...}}
.harness/contract.json      # current sprint's proposed/agreed criteria + tests
.harness/contract_review.json  # evaluator's review of a proposed contract
.harness/verdict.json       # evaluator's grade for the latest build round
.harness/rubric.md          # taste + functionality rubric
.harness/journal.jsonl      # append-only breadcrumb log
.harness/references/        # calibration examples (GOOD / BAD)
ci/build.sh  ci/test.sh     # thin wrappers around your stack's build/test
orchestrator/run_harness.py # headless driver (spawns claude -p per role)
```

## journal.jsonl line schema

```json
{"ts":"<iso>","sprint":3,"role":"evaluator","round":2,"action":"graded","verdict":"revise","weighted":6.8,"note":"specific, actionable"}
```
