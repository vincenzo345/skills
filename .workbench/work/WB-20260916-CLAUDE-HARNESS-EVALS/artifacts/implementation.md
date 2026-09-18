# Implementation record

## Added surface

- `claude_harness_eval/catalog.py`: immutable 20-task catalog, task/file validation, original seed repositories, evaluator-owned reference overlays, and executable acceptance programs.
- `claude_harness_eval/runner.py`: isolated staging, marker verification, evaluator-temporary acceptance execution, reference overlay, timeout/result handling, and aggregate author validation.
- `claude_harness_eval/__main__.py`: `list`, `stage`, `verify`, `apply-reference`, and `validate` commands with JSON results and meaningful exit codes.
- `tests/runtime/test_claude_harness_eval.py`: public-seam pytest coverage for red/green staging, evaluator exclusion, owned-destination protection, marker identity, CLI JSON, fixed catalog coverage, repeated author validation, and all-task red/green acceptance.
- `docs/claude-harness-evals.md`: operating, comparison, safety, and proof-boundary guidance.
- `docs/research/claude-harness-eval-benchmarks.md`: primary-source benchmark research and provenance.
- `README.md`: documentation entry point.

## TDD evidence

1. The first test failed because `claude_harness_eval` did not exist; the tracer implementation made it pass.
2. Isolation/CLI tests failed because the package lacked `__main__`; the CLI implementation made them pass.
3. Fixed catalog coverage failed with only one task; four task batches expanded it to the required 20.
4. Batch author checks caught a filename-encoding defect, two embedded verifier escaping defects, and one incorrect temp-file assertion before the catalog was admitted.
5. Aggregate validation tests failed because `validate_tasks` did not exist; the public `validate` command made them pass.

## Current evidence

- Focused repository suite: 8 passed.
- Catalog listing: exactly 20 tasks across algorithmic, integration, robustness, and work-discipline categories.
- Direct author gate: every untouched seed failed and every reference overlay passed once.

## Boundaries preserved

The implementation did not modify the unrelated Workbench runtime, schemas, adherence cases, or diagnosis-hook changes already present in the worktree. No model was invoked, no global Claude setting changed, and no commit, deployment, or publication occurred.

## Remaining verification

The verification checkpoint must still run repeated aggregate validation, relevant repository regression tests, and a final diff/status review. Linux parity, independent human task review, and real model trials remain outside this local implementation claim.
