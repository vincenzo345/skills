# Specification and delivery plan

## Standards profile

- Python 3.10+ standard library for the installed package and every staged task.
- Pytest only for repository-level acceptance of the runner; staged tasks and hidden acceptance programs use plain Python assertions or `unittest`.
- Public seam: `python -m claude_harness_eval`.
- Subprocess argument arrays only; no shell, network, containers, fixed ports, sleeps, credentials, or writes outside a caller-selected workspace/evaluator temporary directory.
- UTF-8 text, `pathlib`, deterministic literals, synchronization primitives for concurrency, and temporary paths for filesystem behavior.
- Exact task IDs, validated relative file paths, immutable task specifications, and JSON schema version `1` for command results.
- Agent instructions state observable behavior and completion criteria without revealing evaluator cases or reference code.

## Functional requirements

### Catalog

The catalog exposes exactly 20 unique task specifications. Each has a stable kebab-case ID, title, one of four categories (`algorithmic`, `integration`, `robustness`, `work-discipline`), nonempty tags, an instruction, seed files, reference overlay files, an acceptance program, and a positive timeout. Paths are relative, normalized, and containment-safe.

### Staging

`stage TASK WORKSPACE` creates or uses an empty destination and writes only:

- `TASK.md` containing the agent instruction;
- `.harness-eval.json` containing public task metadata and a suite canary;
- the task's seed files.

It rejects an unknown task, nonempty destination, unsafe task path, or file collision. It never materializes acceptance or reference content.

### Verification

`verify TASK WORKSPACE` checks the staging marker and task identity, then runs the evaluator-owned acceptance program under the host interpreter with a timeout and no shell. JSON output reports `schema_version`, `command`, `task_id`, `status`, `passed`, `exit_code`, `timed_out`, `duration_seconds`, `stdout`, and `stderr`. Functional pass means exit code zero without timeout.

### Author validation

`apply-reference` overlays only the task's known-good changed files. `validate` creates fresh temporary workspaces and requires:

- baseline verification to fail;
- reference verification to pass;
- repeated runs to keep the same disposition.

`validate` returns a per-task matrix and a nonzero process exit when any authoring gate fails.

### Documentation

User documentation explains the isolation boundary, commands, result semantics, authoring gates, safe model-run environment, and current proof limitations. It explicitly says local staging is not an OS sandbox.

## Task coverage matrix

| ID | Category | Primary trap |
|---|---|---|
| `inclusive-range-partition` | algorithmic | boundary fix loses or duplicates elements |
| `unicode-username-match` | algorithmic | ASCII-only lowercase comparison |
| `one-shot-iterator` | algorithmic | second iteration silently consumes nothing |
| `pagination-cursor` | integration | cursor repeats, skips, or fails to terminate |
| `cache-key-completeness` | integration | output-changing option absent from cache key |
| `config-precedence` | integration | false and zero treated as missing |
| `backward-compatible-api` | integration | new option breaks old positional callers |
| `error-contract` | integration | sentinel replaces documented exception |
| `cross-file-symbol-rename` | integration | definition changed but export/registry/caller missed |
| `serialization-extensions` | integration | unknown extension fields discarded |
| `cli-stream-semantics` | integration | correct text on wrong stream or exit code |
| `atomic-settings-write` | robustness | partial write destroys prior configuration |
| `path-containment` | robustness | naive prefix check accepts sibling traversal |
| `secret-safe-diagnostics` | robustness | one literal redacted but variants leak |
| `sqlite-transaction` | robustness | partial commit survives second-step failure |
| `concurrent-memoization` | robustness | duplicate computation under contention |
| `shared-validator-refactor` | work-discipline | one duplicated caller remains or behavior drifts |
| `implementation-not-tests` | work-discipline | visible regression test weakened or removed |
| `two-cause-regression` | work-discipline | named path fixed while sibling path remains broken |
| `preserve-dirty-file` | work-discipline | unrelated user content overwritten |

## Repository acceptance tests

The fixed public-seam test set will establish:

1. catalog validity and exact coverage;
2. CLI listing and machine-readable results;
3. staging exclusion of acceptance/reference canaries;
4. rejection of nonempty or mismatched workspaces;
5. one tracer task goes red on untouched seed and green after reference overlay;
6. all 20 tasks go red on untouched seed and green after reference overlay;
7. repeated full validation is disposition-stable;
8. unknown task and verifier timeout/error paths are truthful;
9. unrelated repository files are not mutated by validation.

## TDD delivery slices

1. **Tracer runner:** write failing public-seam tests for catalog/list/stage/verify using `inclusive-range-partition`; implement the smallest package and task needed to pass.
2. **Isolation and results:** add failing tests for nonempty destinations, marker mismatch, evaluator/reference exclusion, JSON shape, and errors; implement the boundaries.
3. **Catalog breadth:** add catalog-contract tests requiring the fixed 20-task matrix; add tasks in four small batches, checking each baseline/reference pair before the next batch.
4. **Author validation:** add failing tests for aggregate validation and repetition; implement `apply-reference` and `validate` through the same stage/verify seams.
5. **Closure checks:** document use, run the focused suite twice, then run relevant existing repository validation without conflating pre-existing failures.

## Deferred obligations

- Run the suite in Linux CI; the current session can prove Windows only.
- Obtain independent human-solvability and instruction/test-alignment review before treating tasks as a stable benchmark.
- Run controlled Claude/Codex trials in disposable environments and record prompt/model/config hashes.
- Add transcript and claim-calibration adapters only after functional evaluation is stable.
