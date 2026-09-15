---
name: implement
description: Implement an executable ticket or a fully specified one-session request test-first, preserving original criteria and producing truthful proof receipts before reporting completion.
disable-model-invocation: true
---

# Implement

Implement the work the user named. A passing command or commit is not enough: use `/delivery-proof` to prove the ticket at the level its criteria require. If that companion skill is not installed, apply the evidence checklist and closure rules in this skill directly; proof requirements never become optional.

Verify `/tdd`, `/code-review`, `/delivery-proof`, and `/grilling` are installed before starting. Name any missing companion. Do not claim that a missing nested review or proof phase ran; use the embedded fallback only where this skill defines one.

## Process

1. **Pin the starting state.** Record the starting commit, branch, staged and unstaged changes, and in-scope untracked files. Treat pre-existing work as user-owned and keep it distinct from this ticket.
2. **Establish the execution contract.** When the source is a ticket, read its complete spec, decisions, blockers, comments, and original criteria; verify the spec is ready, the ticket is open, and every start blocker is satisfied; then claim it through the configured tracker and re-read it for concurrent changes before editing. A direct conversation request may proceed without a tracker artifact only when it clearly fits one session, contains no unresolved consequential choice, and its behavior and proof can be enumerated without invention. Write a compact in-turn execution contract with stable `AC-*` criteria and `OBL-*` items before editing. Otherwise route through `/to-spec` and `/to-tickets`.
3. **Build the evidence checklist.** Map every source criterion and implementation-artifact-owned `OBL-*` obligation to its required proof level, environment, seam, independent oracle, expected population, named terminal state/destination, procedure, and artifact. Candidate, quarantined, staged, dead-letter, or rejected output does not satisfy a criterion for accepted or published output.
4. **Preflight prerequisites.** If an implementation prerequisite is absent, stop and report the exact blocker. If only a later environment or human validation is unavailable, complete safe lower-level work but do not close a ticket whose criteria require the unavailable proof.
5. **Work test-first.** Use `/tdd` at the approved public seams, one vertical red-green-refactor slice at a time. A harness or environment error is not the intended red state.
6. **Verify progressively.** Run focused type and test checks regularly, then the repository's complete relevant checks. Enforce independent expectations and nonzero expected populations.
7. **Review the actual change set.** Use `/code-review` against the pinned state, including committed, staged, unstaged, and in-scope untracked changes. Address blocking Standards and Spec findings, then rerun the affected proof and review. Closure requires the final intended delta to have no blocking finding.
8. **Produce proof receipts.** Record actual population, achieved proof level, result, artifact or log, and `passed`, `failed`, or `blocked` for every criterion. `Failed` means evidence was obtained and did not meet the criterion; `blocked` means the required evidence could not be obtained. Report levels per criterion and an overall state bounded by every unmet required criterion—never summarize only by the maximum achieved level.
9. **Close truthfully.** Close only when every criterion and obligation owned by the implementation ticket or in-turn direct execution contract is proven. Keep or reopen a tracker source; for direct work, report the unresolved contract items and do not claim completion when evidence or a blocking finding remains.

Do not weaken a criterion to make the implementation pass. Preserve its original ID and wording, propose the change upstream, and use `/grilling` for an outcome-reducing decision.

Legacy specs or tickets without readiness, traceability, or proof fields are not implicitly ready. Audit their source and evidence, preserve their history, and create a corrective artifact when needed.

Commit the reviewed intended change to the current branch when the user or repository workflow authorizes commits. A commit is a checkpoint, not completion evidence.
