# ADR 0002: Proportional phases over stage ceremony

**Status:** Accepted  
**Date:** 2026-09-14

## Context

A real brownfield feature entered thirteen Workbench stages even though routing had marked process modeling and proposal not applicable. The same document was reused across several gates, substantial outputs were not registered, and roughly 20–30 minutes were spent constructing receipts and refreshing overlapping projections. The useful defects were found by implementation tests and independent review rather than by the extra transitions.

The problem was not that the work considered UX, architecture, standards, security, specification, and proof. Those concerns were appropriate. The problem was making every concern a separate operational checkpoint regardless of whether it created knowledge, required a decision, transferred ownership, granted authority, or proved a claim.

## Decision

Workbench v0.3 groups the existing domain activities into eight phases: frame, discover, design-decide, plan, implement, verify, release, and measure.

Routing compiles applicable activities through the selected destination. Each active phase has at most one checkpoint, represented by its last applicable activity and its registered exit gate. Not-applicable activities remain explicit in the immutable routing receipt but are never entered. A work item's depth grows through map nodes, evidence tasks, specialist work, and artifacts rather than through mandatory lifecycle transitions.

New routed work uses `profile-compiled` state. The five fixed route IDs remain supported only for replay and direct legacy starts. Greenfield is a routing context, proposal is a destination, and fast or full is a depth policy rather than a separate source of lifecycle truth.

The operational interface is also condensed:

- Preserve raw intake, then use atomic `route-and-start` when routing is ready.
- Let `status` and `resume` return the complete projection and frontier; `next` is optional.
- Accept one structured handoff bundle and register its output records atomically.
- Derive a gate envelope from an accepted handoff instead of requiring a hand-authored receipt.
- Treat unspecified authority as denied.
- Record proof once and render ticket or delivery views from it.

The event journal, replay projection, revision checks, idempotency, artifact integrity, decision authority, deployment authorization, and distinctions among local, deployed, and business proof remain unchanged in purpose.

## Consequences

- The manual-table feedback case compiles to six checkpoints instead of thirteen while retaining brownfield, evidence, UX, architecture, standards, specification, delivery, implementation, and verification activities.
- Workbench state ends at the selected destination rather than showing release and outcome work as pending.
- A registered artifact has a verified local path and digest; a filename alone cannot satisfy a v0.3 checkpoint.
- Required and achieved proof must match environment, seam, and journey. An isolated component harness cannot pass an authenticated application-flow requirement.
- Old event journals and direct legacy starts remain valid, so the migration can be forward-tested without rewriting history.
- Map-node creation, dependency-derived readiness, route correction, remote artifact retrieval, and validation loops remain later bounded slices.
