---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Before starting an individual ticket, explicit undecomposed spec, or direct conversation request, apply [ticket sizing and readiness](../setup-repo/TICKET-SIZING.md) to the entire selected scope. Record its evidence and estimate before implementation; direct-spec ownership does not bypass this gate. Refine oversized or uncertain work within the existing authorization before proceeding.

Read the configured tracker and [shared work-record contract](../setup-repo/WORK-RECORDS.md) before resolving work. Resolve an explicit issue, effort, or spec first; without one, follow the ordered effort queue. For remote trackers, use [the remote adapter contract](../setup-repo/REMOTE-WORK.md), refresh provider authority and establish the supported ownership path before work. For local trackers, use the shared consumer's `select-and-claim` operation, passing the explicit target when provided, so authoritative selection and acquisition share a lock. An explicit issue selects only itself; an effort or decomposed spec selects its first eligible issue. Only an explicitly selected undecomposed spec permits whole-spec execution. Never infer work from history, filenames, or directory recency.

Report the selected title, effort, basis and authority, and preserve its ownership token. Known blocked, claimed, stale, or unready work permits trying independent work inside the requested scope. Missing readiness, malformed ordering, unavailable authority, and unknown dependency outcomes stop selection with their specific diagnostic. Invalid explicit targets never fall through to unrelated work. Resolve ambiguous identity before execution. A preview from `select` is not ownership; acquire before implementing.

Before starting the acquired issue, apply the shared sizing reference's discovery-impact and scope-change check using its current basis and relevant integrated evidence. Preserve the explicit scope and follow existing token-checked reconciliation or release if the acquired work becomes stale or unready.

Call the Skill tool with "tdd" where possible, reusing agreed seams and following its guidance for new boundaries.

For disposable validation or interrupted work, read the housekeeping reference named by repository instructions, or the [shared fallback](../setup-repo/housekeeping.md#without-repository-configuration) if none is configured.

Use the shared sizing reference's verification policy: repository-required and affected checks, with whole-spec checks at appropriate integration boundaries. Preserve mandatory checks and invalidate reused evidence when relevant code or environment changes.

Report scope-changing discoveries as they arise and follow the shared reference's re-estimation and authorization rules instead of silently expanding implementation. Preserve unfinished work and ownership for reconciliation; continue independent ready work only within the requested scope.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.

After verification and review, provide the shared reference's completion handoff, including downstream implications and whether work awaits integration. Record completion evidence and complete through the token-checked consumer only when the work is available under the tracker's integration rules. Release unfinished work with its token; retain blocked or abandoned ownership for explicit recovery.
