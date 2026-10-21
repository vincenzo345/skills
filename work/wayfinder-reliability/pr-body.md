## Summary

Planning and implementation previously used overlapping local issue locations, with no shared rule for selecting current work. This change carries one effort through the skills and validates readiness, spec basis, dependencies, and ownership before implementation.

```text
work/<effort>/
  README.md       current pointers and next action
  map.md          planning context
  decisions/      human decisions and retained answers
  spec.md         current specification
  tickets/        approved implementation issues
  history/        earlier specification bases

explicit reference or ordered queue
  -> authoritative eligibility checks
  -> exclusive local claim
  -> verified integration before completion
```

Preserves Wayfinder's charting stop and one-decision boundary. Adds shared local helpers, opt-in legacy adoption, remote capability diagnostics, synchronized skill documentation, and regression coverage. Historical repository work stays in place.

## Evidence

- **Before:** the recorded Articles investigation drifted into an unrelated article prerequisite, and continuation/storage were unclear. See [discovery](https://github.com/vincenzo345/skills/blob/integration/wayfinder-reliability/docs/plans/wayfinder-reliability.md).
  **After:** the fresh installed-source replay preserved human choices, superseded answers and anchored history links, rejected the unrelated rewrite prerequisite, and handed an approved issue to a fresh consumer. See [replay evidence](https://github.com/vincenzo345/skills/blob/integration/wayfinder-reliability/work/wayfinder-reliability/replay-2026-10-21/README.md).
- Fresh Windows verification passed 60 script tests in 123.480 seconds with pinned PyYAML 6.0.3, plus 27 preservation tests and package/version/manifest checks. Prior independent review corrections and detailed limits are recorded in [validation](https://github.com/vincenzo345/skills/blob/integration/wayfinder-reliability/work/wayfinder-reliability/validation.md).
- Installed source `00ff5b94ebab4fdd7d6fea9681e79957fcedbc57`: 32 skills and 111 files verified for each runtime. Codex comparison normalizes CRLF; Claude matches Git bytes exactly.
- Claude Code has no authenticated session for live behavior. Remote automatic concurrent claiming remains unsupported; remote fixtures are not provider exclusivity proof. Hosted [Windows and Linux validation passed](https://github.com/vincenzo345/skills/actions/runs/39615504001) at `2518eae`; subsequent head checks are visible on this PR.
- **Draft, with two unresolved replay findings:** spec publication retained a stale discovery stage, and the actor suggested unavailable `spec-to-issues` instead of `to-tickets`. Evidence is preserved; no fixes are included in this verification follow-up. Resolve or explicitly disposition both before merge readiness.

## Merge Danger

**Door:** two-way

Source changes can be reverted. Reverting the reader does not undo records created with the new contract; preserve those records and coordinate reader rollback. No historical migration or release is performed by this PR.

**Blast Radius:** workflow

Changes local planning, specification, ticket publication, and implementation selection across participating skills. Local ownership requires one authoritative checkout and shared Git coordinator. Merging to main triggers the existing Changesets release workflow; publication alone does not merge or release.
