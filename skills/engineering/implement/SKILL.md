---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Read the configured tracker and [shared work-record contract](../setup-repo/WORK-RECORDS.md) before resolving work. Resolve an explicit issue, effort, or spec first; without one, follow the ordered effort queue. For remote trackers, use [the remote adapter contract](../setup-repo/REMOTE-WORK.md), refresh provider authority and establish the supported ownership path before work. For local trackers, use the shared consumer's `select-and-claim` operation, passing the explicit target when provided, so authoritative selection and acquisition share a lock. An explicit issue selects only itself; an effort or decomposed spec selects its first eligible issue. Only an explicitly selected undecomposed spec permits whole-spec execution. Never infer work from history, filenames, or directory recency.

Report the selected title, effort, basis and authority, and preserve its ownership token. Known blocked, claimed, stale, or unready work permits trying independent work inside the requested scope. Missing readiness, malformed ordering, unavailable authority, and unknown dependency outcomes stop selection with their specific diagnostic. Invalid explicit targets never fall through to unrelated work. Resolve ambiguous identity before execution. A preview from `select` is not ownership; acquire before implementing.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.

After verification and review, record completion evidence and complete through the token-checked consumer only when the work is available under the tracker's integration rules. Release unfinished work with its token; retain blocked or abandoned ownership for explicit recovery.
