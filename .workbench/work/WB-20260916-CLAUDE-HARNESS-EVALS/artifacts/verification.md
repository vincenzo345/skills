# Local verification

## Result

The 20-task evaluation suite is locally implemented and verified at its public CLI and staged-workspace seams on Windows.

## Executed evidence

### Focused public-seam suite

```text
python -m pytest -p no:cacheprovider tests/runtime/test_claude_harness_eval.py -q
.........                                                                [100%]
9 passed in 8.88s
```

The tests cover tracer red/green behavior, evaluator exclusion, owned-destination protection, marker mismatch, CLI JSON and exit status, exact task/category coverage, every staged file set, repeated author validation, and full-catalog validation.

### Repeated author gate

```text
validate_tasks(repeat=2)
passed: True
tasks: 20
attempts: 40
baseline failures: 40
reference passes: 40
```

Every untouched task failed its evaluator-owned acceptance program on both attempts; every reference overlay passed the same verifier on both attempts.

### Repository runtime regression

```text
python -m pytest -p no:cacheprovider tests/runtime -q
105 passed in 122.69s
```

### Repository validators

```text
python scripts/validate-workbench.py
Workbench foundation validation passed: 10 comparison cases, 10 negative contract cases, 14 record instances, 5 scenarios, 12 schemas.

python scripts/validate-skills.py
Validated 9 skills: names, metadata shape, invocation policies, nested references, links, catalog, manifest, and portability checks pass.
```

### Static and change-surface review

- `git diff --check` reported no whitespace errors.
- Python AST parsing succeeded for all package modules and the focused test module.
- Final status review confirmed unrelated Workbench runtime, schema, adherence, and diagnosis-hook changes were not edited as part of this implementation.
- The catalog lists exactly 20 unique tasks across four categories.

## Non-vacuity

The untouched fixtures are intentionally defective and all 40 repeated baseline checks failed. The evaluator then changed only the task-defined reference-overlay files and all 40 corresponding checks passed. Staging tests enumerate the complete file set for every task and prove that evaluator and reference-only files are absent.

## Dispositions

- Feature-focused behavior: passed locally.
- Repository runtime health: 105 tests passed locally.
- Structural repository validators: passed.
- Cross-platform parity: unverified; Linux CI was not run.
- Model behavior: unverified; no Claude, Codex, or DSPy trial was executed.
- Human task fairness: unverified; no independent engineer reviewed or solved all tasks.
- Security isolation: bounded; evaluator files are separated, but candidate code execution is not an OS sandbox.
- User acceptance: not yet recorded.

## Most plausible residual risk

Synthetic reference solutions and tests were authored together, so shared author assumptions may make a task internally consistent but less representative or fair than intended. The next meaningful proof is an independent instruction-to-assertion review and blind human solve, followed by Windows/Linux CI and paired model trials.
