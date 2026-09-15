---
name: code-review
description: Review a branch or worktree since a fixed point along separate Standards and Spec axes, including uncommitted files and the sufficiency of delivery evidence. Use for PR, branch, or work-in-progress reviews.
---

# Code Review

Review the intended change set along two independent axes:

- **Standards** — conformity with repository rules and maintainable design.
- **Spec** — fidelity to the original requirements, decisions, obligations, and proof contracts.

Use parallel sub-agents for the axes when agent capacity exists; otherwise run them sequentially while preserving separate reports. Never let a clean Standards result hide a Spec failure or vice versa.

Apply the evidence checks below directly; the review has no companion-skill dependency.

## 1. Pin the review set

Resolve the fixed point supplied by the user. If none is supplied, infer the repository's normal merge base when unambiguous; otherwise ask. Record the resolved commit, branch, and commits since it.

Review the merge-base-to-HEAD diff **plus** staged changes, unstaged changes, and in-scope untracked files. Inventory pre-existing dirty work so it is not silently attributed to the implementation. Fail early on a bad reference, but do not call an apparently empty committed diff empty until the working tree and untracked inventory are checked.

## 2. Find the source of truth

Use tracker conventions to load the full originating ticket/spec, comments, accepted decisions, original criteria, coverage matrix, and proof receipts. Prefer explicit user references, then commit/branch references and repository conventions. If no spec exists, report that limitation; do not manufacture one.

## 3. Standards axis

Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and coding standards. Check the actual diff for violations and regressions. Where the repository is silent, use these as judgment-call smells, not hard rules:

- mysterious names, duplicated logic, feature envy, data clumps, primitive obsession;
- repeated switches, shotgun surgery, divergent change, speculative generality;
- message chains, needless middlemen, and inheritance that does not honor its contract.

Repository policy overrides the smell baseline. Skip issues already enforced by tooling unless the enforcement was bypassed.

## 4. Spec axis

Build a criterion-to-change-to-proof table. Check:

- missing, partial, incorrect, or unrequested behavior;
- source criteria that were weakened, waived, reworded, or dropped without authorized source change;
- contradictions with accepted decisions or decision provenance;
- orphan outcomes, invariants, dependencies, or `OBL-*` obligations;
- wrong proof level, environment, journey, seam, or artifact;
- self-derived or implementation-generated oracles;
- empty or unexpectedly reduced populations;
- intermediate, candidate, quarantined, staged, dead-letter, or rejected artifacts counted as accepted/published terminal output;
- skipped, disabled, harness-failed, mock-only, or non-executed evidence presented as success;
- missing target-environment, rollout, compatibility/parity, cutover, rollback, migration, or human-validation work;
- intended files missing from the review set, especially untracked files.

Judge evidence by proof level, environment, independence, non-vacuity, terminal destination, and status. A test-suite pass does not replace criterion-specific proof.

## 5. Report separately

For each axis, list findings by severity with file/hunk or criterion references, evidence, consequence, and the smallest safe corrective action. Distinguish hard violations from judgment calls. If there are no findings, say what was reviewed and any proof limitations.

End with counts and the worst finding within each axis; do not collapse them into one score. A blocking finding keeps or reopens the artifact that owns the unmet criterion or obligation. Do not reopen an upstream locally scoped ticket when its contract is satisfied and a valid downstream proof ticket owns the missing evidence. A review itself does not authorize fixes, acceptance changes, commits, or ticket closure.
