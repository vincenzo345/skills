# Architecture decision: isolated catalog runner

## Decision

Implement a small top-level Python package named `claude_harness_eval` with a public `python -m claude_harness_eval` CLI. Keep task definitions, seed files, reference overlays, and acceptance programs in an evaluator-owned catalog module. The runner materializes only the instruction and seed files into a caller-selected workspace.

## Public commands

- `list [--json]`: enumerate immutable task metadata.
- `stage TASK WORKSPACE [--json]`: create a new isolated agent workspace.
- `verify TASK WORKSPACE [--json]`: execute the hidden acceptance program in a subprocess and report the result.
- `apply-reference TASK WORKSPACE [--json]`: author-only overlay used to prove the green oracle.
- `validate [TASK ...] [--repeat N] [--json]`: prove untouched-seed failure and reference success through the public stage/verify path.

## Boundaries

```text
evaluator repository
  catalog: instruction + seed + reference + verifier
       |
       | stage copies instruction + seed only
       v
isolated workspace  <---- coding agent edits here
       |
       | workspace path only
       v
evaluator subprocess runs hidden acceptance program
       |
       v
machine-readable functional result
```

The agent-visible workspace contains `TASK.md`, `.harness-eval.json`, and seed files. It contains no verifier source, reference overlay, catalog source, or expected output beyond the stated contract.

## Catalog contract

Each immutable `TaskSpec` contains:

- stable ID, title, category, and tags;
- an agent-facing instruction with checkable completion criteria;
- a mapping of relative seed paths to UTF-8 text;
- a mapping of relative reference-overlay paths to UTF-8 text;
- an evaluator-owned Python acceptance program;
- a timeout.

Catalog construction validates IDs, relative paths, uniqueness, nonempty instructions, required fields, and disjoint evaluator boundaries. Task definitions use only original repository-owned content.

## Isolation and execution

- Exact catalog IDs replace arbitrary filesystem lookup.
- Relative fixture paths reject absolute paths and `..` traversal.
- `stage` accepts only a missing or empty destination and writes no file outside it.
- `verify` requires the staging marker and matching task ID.
- The acceptance program is written to an evaluator-owned temporary directory and executed with the host Python interpreter, the workspace as its only argument, a bounded timeout, captured output, and no shell.
- Candidate code executes as untrusted code; this runner provides filesystem separation from evaluator assets, not an OS sandbox. Real model trials still require a disposable VM or locked-down account with no credentials and restricted network.

## Result contract

Every command can emit JSON. Verification reports schema version, task ID, status, passed boolean, exit code, duration, stdout, stderr, and timeout state. `validate` reports baseline and reference dispositions per task and exits nonzero if any no-op unexpectedly passes or any reference unexpectedly fails.

## Alternatives rejected

- Vendoring public benchmark repositories: heavier, licensing-sensitive, contamination-prone, and not offline/cross-platform enough.
- Copying verifier files into the workspace: lets the evaluated agent inspect or modify the oracle.
- Grading from transcript claims: measures narration rather than achieved behavior.
- One directory with four files per task: transparent but needlessly repetitive for small text-only fixtures; immutable typed task definitions preserve the same boundary with substantially less repository sprawl.
