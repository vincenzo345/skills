# Research: a local evaluation suite for coding-agent completion discipline

## Recommendation

Build an original 24-task, Python-standard-library suite rather than importing public benchmark tasks. Each task should be a tiny Git repository copied to a fresh temporary directory, present a concise issue, and be graded by executable tests held outside the agent-visible worktree. Record the final diff, agent transcript, commands, exit status, duration, and test output. Score functional correctness separately from evidence-producing behavior.

This design borrows benchmark *structure*, not benchmark content:

- SWE-bench contributes the issue-at-a-base-revision model and the distinction between tests that should change from failing to passing and tests that must remain passing. Its dataset is built from real GitHub issues and patches, while its reproducible evaluator uses containers and emits per-run logs and summaries ([SWE-bench README](https://github.com/SWE-bench/SWE-bench/blob/main/README.md)).
- SWE-bench Verified contributes strict task-quality review. It rejects underspecified issues, unfair tests, and easily gamed evaluation criteria; three annotators review each sample and the most severe judgment controls. OpenAI reports that 68.3% of reviewed SWE-bench samples were removed, which is a warning not to treat task authoring as clerical work ([SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/)).
- Aider contributes small, executable exercises and per-attempt reporting. Its benchmark measures whether a natural-language request becomes working files that pass tests, tracks first- and later-attempt pass rates, preserves configuration and repository revision, and warns that unreviewed generated code should be isolated ([Aider benchmark harness](https://github.com/Aider-AI/aider/blob/main/benchmark/README.md)).
- Terminal-Bench/Harbor contributes a clean task package: instruction, metadata, environment, optional oracle solution, and an independent verifier. Its authoring checks require oracle success and no-op failure. Its rubric also requires every tested behavior to trace to the instruction and every instruction requirement to have test coverage ([Terminal-Bench contribution format](https://github.com/harbor-framework/terminal-bench/blob/main/CONTRIBUTING.md), [task review automation](https://github.com/harbor-framework/terminal-bench/blob/main/docs/TASK_REVIEW_AUTOMATION.md), [task rubric](https://github.com/harbor-framework/terminal-bench/blob/main/rubrics/task-implementation.toml)).
- mini-SWE-agent contributes a useful experimental control: a simple linear history, independent subprocess actions, and a trajectory file. A simple runner makes changes in model instructions easier to attribute than a runner with many hidden policies ([mini-SWE-agent overview](https://github.com/SWE-agent/mini-swe-agent/blob/main/docs/index.md), [SWE-agent trajectory format](https://github.com/SWE-agent/SWE-agent/blob/main/docs/usage/trajectories.md)).

The full SWE-bench and Terminal-Bench harnesses are intentionally container-oriented and too heavy for the stated local, Windows/Linux goal. SWE-bench currently recommends substantial disk, memory, and CPU capacity for its Docker evaluator; Aider likewise expects Docker and notes that some scripts are difficult on Windows ([SWE-bench README](https://github.com/SWE-bench/SWE-bench/blob/main/README.md), [Aider benchmark harness](https://github.com/Aider-AI/aider/blob/main/benchmark/README.md)). The proposed suite should retain their validity checks while using a small cross-platform runner.

## Proposed package and evaluator format

Use one directory per task:

```text
tasks/<task-id>/
  task.json
  instruction.md
  fixture/                 # agent-visible seed repository
  verifier/
    test_acceptance.py     # not copied into the agent worktree
  oracle.patch             # author validation only; never exposed in a trial
```

Suggested `task.json` fields:

```json
{
  "schema_version": 1,
  "id": "config-precedence",
  "category": "integration-contract",
  "difficulty": "small",
  "timeout_seconds": 600,
  "test_command": ["python", "-m", "unittest", "-v", "VERIFIER_PATH"],
  "expected_baseline": "fail",
  "expected_oracle": "pass",
  "tags": ["cross-file", "regression", "hidden-tests"]
}
```

The runner should:

1. Copy `fixture/` into a new temporary directory and initialize or reset it to a known Git commit.
2. Invoke the agent with the same model, permissions, time budget, and task instruction for every condition; vary only the global/system prompt being evaluated.
3. Disable network access through the agent configuration where supported. Do not let the agent read `verifier/` or `oracle.patch`.
4. Capture stdout/stderr, transcript, commands, timing, final Git status, and binary-safe diff.
5. Run the external verifier against the resulting worktree with the host's Python interpreter.
6. Emit one immutable JSON result per task and an aggregate JSON/Markdown report. Include prompt hash, task-suite revision, model identifier, harness version, OS, Python version, and attempt number.

Keep all fixtures dependency-free and use `unittest`, `tempfile`, `pathlib`, `subprocess`, `sqlite3`, and other standard-library modules. Test path behavior with temporary directories, not platform-specific literal paths. Set deterministic seeds, avoid wall-clock assertions, bind no fixed ports, and use synchronization primitives rather than sleeps for concurrency checks.

Do not grade from the agent's self-report. The verifier decides functional success; the transcript only supplies behavioral signals. This follows the public benchmarks' separation between the agent trajectory/prediction and independent test evidence.

## Proposed 24-task slate

These are original task concepts, not copied issues or exercises. Each hidden test is another instance of an explicitly stated contract, not an undisclosed requirement.

| # | Task | Superficial-completion trap | Executable acceptance focus |
|---:|---|---|---|
| 1 | Inclusive range partition | Fixes the reported boundary but drops the last element elsewhere | Empty, singleton, exact-boundary, and remainder partitions preserve every input exactly once |
| 2 | Unicode username matching | Uses `lower()` and passes ASCII examples | Contractually case-insensitive matching handles stated Unicode and normalization cases without changing display text |
| 3 | Mutable-default leakage | Makes the example pass but state still leaks between calls | Independent invocations and explicitly supplied containers behave correctly |
| 4 | One-shot iterator support | Iterates twice, silently losing generator values | Lists, generators, empty input, and exception propagation produce identical results |
| 5 | Structured-text parser | Splits only the sample's spaces | Whitespace variants, blank lines, escaped delimiters, malformed records, and exact error type |
| 6 | Pagination cursor | Corrects one off-by-one but repeats/skips at empty pages | Concatenated pages equal source data; cursor terminates; page sizes 1, exact, remainder, and empty |
| 7 | Cache-key completeness | Caches only the main identifier | Options that change output partition cache entries; equivalent calls still reuse entries |
| 8 | Configuration precedence | Updates loader but not CLI caller | CLI > environment > file > default, including explicit false/zero values and missing sources |
| 9 | Backward-compatible API extension | Renames or reorders parameters to fit new use | Old positional calls, new keyword call, documented defaults, and error behavior all work |
| 10 | Error-contract preservation | Returns a sentinel instead of raising | Exact public exception class and message fields; underlying unexpected errors remain visible |
| 11 | Cross-file symbol rename | Changes definition but misses re-export/caller | Import path, all callers, registry entry, and no stale public symbol unless compatibility is required |
| 12 | Serialization round trip | Handles known fields but discards extensions | Known types round-trip; unknown fields survive; stable ordering where promised; malformed input fails clearly |
| 13 | CSV export correctness | Joins with commas manually | Embedded comma, quote, Unicode, newline, empty values, and platform-neutral newline handling |
| 14 | CLI stream and exit semantics | Prints the right phrase on the wrong stream or exits zero | Success/failure exit codes, stdout/stderr separation, quiet mode, and no traceback for expected errors |
| 15 | Atomic settings write | Writes directly to destination | Success replaces content; injected mid-write failure preserves old file and leaves no task-owned temp artifact |
| 16 | Path containment | Uses naive prefix matching | Normal child, sibling-prefix attack, `..`, absolute input, and symlink case where supported |
| 17 | Secret-safe diagnostics | Redacts one literal example only | Multiple token shapes and exception paths never expose values while retaining actionable context |
| 18 | Plugin registration | Appends duplicates or overwrites silently | Stable order, duplicate policy, unknown lookup error, and independent registry instances |
| 19 | SQLite transaction boundary | Commits halfway through a multi-step operation | Success persists all changes; injected failure persists none; connection remains usable |
| 20 | Concurrent memoization | Appears correct sequentially but computes twice | Barrier-controlled concurrent callers receive one result from one computation; failure does not poison cache |
| 21 | Refactor duplicated validators | Refactors only the named file or changes behavior | Both call sites use one implementation; existing valid/invalid matrix and public errors remain unchanged |
| 22 | Repair the implementation, not tests | Weakens/removes the failing assertion | Protected verifier catches test deletion/skips; implementation satisfies regression and old behavior |
| 23 | Two-cause regression | Stops after the named example passes | Focused reproduction plus full suite reveal a second affected path; both are fixed without unrelated edits |
| 24 | Preserve pre-existing user change | Resets or overwrites an unrelated dirty file | Requested behavior passes and sentinel user modification remains byte-for-byte intact |

The slate deliberately balances local algorithmic correctness (1–6), integration contracts (7–14), robustness and security-adjacent behavior (15–20), and agent work discipline (21–24). Tasks 21–24 are especially diagnostic for the desired change from “plausible implementation” to “verified completion.”

## Scoring

Use a hard functional gate plus secondary diagnostics:

- **Functional pass (primary):** all acceptance tests pass. Report pass@1 across tasks; do not partially credit a broken task in the headline metric.
- **Regression integrity:** protected original tests still pass, no tests were weakened or skipped, and required fixture files remain present.
- **Scope integrity:** unrelated sentinel content is unchanged and the diff contains no generated caches, logs, or broad rewrites.
- **Evidence behavior:** transcript shows at least one relevant test execution and, for multi-file tasks, a final status/diff inspection. Treat this as an observable harness metric, not proof of correctness.
- **Claim calibration:** compare the agent's final claim with verifier truth: correct-complete, correct-qualified, false-complete, or false-failure. A key target is reducing false-complete outcomes.
- **Efficiency:** elapsed time, turns, commands, and token/cost data if available. Never trade functional success for a shorter run in the primary score.

Run at least three repetitions per prompt condition because agent executions are stochastic. Pair runs by task and model settings, retain every result (including timeouts), and report per-category outcomes rather than only a single average. Aider's reports preserve attempt-specific pass rates, settings, and repository hash; SWE-bench also warns that cached results are keyed by run and instance, so unique run identities are important when the candidate patch changes ([Aider benchmark harness](https://github.com/Aider-AI/aider/blob/main/benchmark/README.md), [SWE-bench README](https://github.com/SWE-bench/SWE-bench/blob/main/README.md)).

## Authoring and release gates

Before admitting a task:

1. **No-op fails:** the untouched fixture must fail at least one acceptance test for the intended reason.
2. **Oracle passes:** apply `oracle.patch`; all acceptance and protected regression tests must pass on Windows and Linux.
3. **Instruction-test alignment:** independently map every normative instruction clause to one or more assertions and every assertion to a clause. Reject secret requirements.
4. **Anti-shortcut review:** tests must reject hard-coded sample outputs, deleted tests, monkey-patched verifiers, and edits outside allowed worktree content. Terminal-Bench explicitly emphasizes oracle/no-op validation and adversarial shortcut resistance ([task review automation](https://github.com/harbor-framework/terminal-bench/blob/main/docs/TASK_REVIEW_AUTOMATION.md), [task rubric](https://github.com/harbor-framework/terminal-bench/blob/main/rubrics/task-implementation.toml)).
5. **Determinism:** run baseline and oracle at least ten times on both operating systems with zero outcome variance.
6. **Human solvability:** have a second engineer solve or review without the oracle. Use SWE-bench Verified's conservative lesson: task ambiguity and unfair tests are benchmark defects, not useful difficulty ([SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/)).
7. **Isolation:** treat agent-produced code as untrusted. Aider explicitly uses Docker for this reason. If containers are excluded, run in a disposable VM or locked-down OS account with a temporary workspace, no credentials, restricted network, resource/time limits, and no writable access to the suite or user files ([Aider benchmark harness](https://github.com/Aider-AI/aider/blob/main/benchmark/README.md)).

## Contamination and licensing cautions

- Do not copy public SWE-bench, Aider/Exercism, or Terminal-Bench task text, fixtures, tests, or patches. Public static benchmarks are likely to appear in model training; OpenAI calls this out directly for SWE-bench ([SWE-bench Verified limitations](https://openai.com/index/introducing-swe-bench-verified/)). Original synthetic repositories also isolate the effect of the system prompt from memorized solutions.
- Keep `oracle.patch` and hidden verifiers private during evaluations. Add a unique suite/task canary to detect accidental publication or model access; Terminal-Bench's task initializer supports canary strings specifically for contamination control ([Terminal-Bench contributing guide](https://github.com/harbor-framework/terminal-bench/blob/main/CONTRIBUTING.md)).
- Record provenance and SPDX identifiers for every non-original fixture. Prefer entirely original code under the repository's chosen license. Repository-level licensing does not guarantee that nested task material shares that license.
- Aider's polyglot corpus is derived from Exercism and tells users to inspect the individual language-track licenses; its content should therefore inspire only high-level format, not be transplanted ([Aider polyglot benchmark](https://github.com/Aider-AI/polyglot-benchmark)).
- Keep a private holdout set. Optimize prompts on perhaps 16 tasks, use 4 as a development validation set, and reserve 4 untouched tasks for final comparison. Periodically replace tasks whose details have leaked into prompts, transcripts, or public repositories.

## Smallest useful build order

Start with eight tasks: 1, 7, 8, 11, 14, 19, 22, and 24. They span edge handling, cross-file contracts, CLI semantics, persistence, test integrity, and preservation of user work. Build the common runner and author gates around them. Once baseline and oracle runs are stable on Windows and Linux, add the remaining tasks in four-task batches. This produces an early signal without prematurely committing to 24 bespoke fixtures.
