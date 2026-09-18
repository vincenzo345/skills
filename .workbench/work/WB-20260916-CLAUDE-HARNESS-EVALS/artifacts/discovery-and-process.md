# Discovery and evaluation process

## Repository fit

The repository already treats synthetic comparison fixtures as executable oracles and explicitly separates structural fixture validity from actual model-behavior claims. Its runtime tests use pytest, but task fixtures should depend only on the Python standard library so staged repositories remain offline and portable. Existing unrelated Workbench changes are present and must not be rewritten.

## Primary-source lessons

The research note at `docs/research/claude-harness-eval-benchmarks.md` records the evidence:

- SWE-bench contributes issue-at-base-state evaluation and FAIL_TO_PASS/PASS_TO_PASS thinking.
- SWE-bench Verified contributes conservative review for ambiguity, unfair hidden requirements, and weak tests.
- Aider contributes small executable exercises, per-attempt reporting, and isolation warnings.
- Terminal-Bench/Harbor contributes task packages, evaluator-owned tests, oracle success, no-op failure, and instruction-to-assertion traceability.
- mini-SWE-agent contributes a simple trajectory boundary that makes prompt changes easier to attribute.

Original synthetic tasks are preferable to copied public tasks because they avoid licensing ambiguity, memorized solutions, heavyweight containers, and network dependencies.

## Public evaluation loop

1. `list` discovers the immutable catalog and returns task metadata.
2. `stage <task> <workspace>` rejects unsafe or non-empty destinations, then copies only the instruction and agent-visible seed files.
3. An external harness launches the coding agent with the staged directory as its working directory. The suite repository, verifier, and reference solution are outside that directory and should not be exposed to the agent process.
4. `verify <task> <workspace>` resolves the task by exact ID, runs its evaluator-owned Python acceptance script in a subprocess with a timeout, and emits JSON containing task ID, pass/fail, exit code, duration, and captured output.
5. `apply-reference <task> <workspace>` is an author-only validation operation that overlays the evaluator-owned known-good files.
6. `validate` proves every untouched seed fails and every reference overlay passes through the same verifier. Optional repetition detects local nondeterminism.
7. A future model runner may attach transcript, commands, timing, claims, prompt hash, model ID, and token/cost data without changing functional acceptance.

## Selected 20-task coverage

The implementation will use these original concepts from the research slate:

1. inclusive range partition;
2. Unicode username matching;
3. one-shot iterator support;
4. pagination cursor termination;
5. cache-key completeness;
6. configuration precedence with falsey values;
7. backward-compatible API extension;
8. public error-contract preservation;
9. cross-file symbol rename and compatibility export;
10. serialization round-trip with extension fields;
11. CLI stdout/stderr and exit semantics;
12. atomic settings write;
13. path containment including sibling-prefix attacks;
14. secret-safe diagnostics;
15. SQLite transaction rollback;
16. concurrent memoization;
17. duplicated-validator refactor;
18. repair implementation without weakening tests;
19. two-cause regression;
20. preservation of an unrelated dirty file.

This selection retains the four work-discipline tasks that are most diagnostic of premature completion while dropping four lower-leverage micro-bugs from the 24-task research slate.

## Admission and proof rules

- No-op failure and reference success are mandatory for every task.
- Every instruction requirement maps to a verifier assertion; hidden tests vary stated inputs but add no secret requirement.
- Staging never includes evaluator or reference material.
- Verifiers execute in subprocesses and receive only the staged workspace path.
- Functional pass is binary per task. Transcript and claim calibration are separate dimensions.
- Local repeated validation establishes fixture determinism only on the current OS; Windows/Linux CI and human-solvability review remain follow-up evidence.
