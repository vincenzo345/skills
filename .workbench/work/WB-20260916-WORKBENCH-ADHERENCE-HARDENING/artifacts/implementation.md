# Workbench adherence hardening implementation

## Skill patch

`skills/workbench/SKILL.md` now requires repository/store preflight before capture, preserves every independently triggered installed method, and keeps each human question to one decision dimension without interpreting silence or non-selection.

## Runtime issues

- `.scratch/workbench-adherence-hardening/issues/01-evidence-provenance.md`
- `.scratch/workbench-adherence-hardening/issues/02-proof-bound-obligations-and-amendments.md`
- `.scratch/workbench-adherence-hardening/issues/03-repository-store-identity.md`

These are open local issues. No runtime or schema change is claimed.

## Regression evals

`tests/comparison/workbench-adherence/cases.json` defines six behavior-oriented cases. `tests/runtime/test_workbench_adherence_evals.py` validates their required coverage and invariants. The focused red state failed because the catalog was absent; after adding the fixtures, all seven focused checks passed.

The eval catalog is an oracle for future model evaluation. Its structural tests do not themselves invoke a model or prove agent compliance.
