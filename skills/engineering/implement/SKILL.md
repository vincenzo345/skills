---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Read the configured tracker and [shared work-record contract](../setup-repo/WORK-RECORDS.md) before resolving work. For an explicit local issue, read through the declared authority, validate and claim it with the shared consumer before starting. Report its title, effort, basis and authority, and preserve the ownership token. An ineligible or unavailable target yields its specific reason; it never falls through to unrelated work. Resolve ambiguous identity before execution.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.

After verification and review, record completion evidence and complete through the token-checked consumer only when the work is available under the tracker's integration rules. Release unfinished work with its token; retain blocked or abandoned ownership for explicit recovery.
