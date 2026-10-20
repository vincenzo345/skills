---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/07-remote-authority.md
effort: work/wayfinder-reliability
order: 7
state: in-progress
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/03-planning-continuity.md
- work/wayfinder-reliability/tickets/05-concurrent-implementation.md
---

# 07: Respect remote authority and bound remote concurrency

## What to build

 The configured remote tracker participates in the same planning-to-implementation handoff while keeping remote state authoritative and enforcing the documented concurrency boundary.

## Acceptance criteria

- [ ] Existing supported remote adapter guidance maps the shared record facts, current spec basis, readiness, native dependencies, ordering, and completion semantics without creating a mutable local status mirror.
- [ ] The complete handoff preserves remote map/decision authority and local asset links. Implementation queries current remote state before selection and before completion.
- [ ] For each supported claim path, document and verify conditional exclusive acquisition or one established shared controller. A two-contender test is required before claiming concurrent support.
- [ ] If a provider lacks the required capability, automatic concurrent claiming reports unsupported behavior. Assignment alone and per-worktree claims are not accepted as proof of exclusivity.
- [ ] Unavailable remote records, incomplete dependency queries, stale revisions, canceled blockers, and conflicting existing claims fail with specific explanations.
- [ ] Adapter contract fixtures cover authority and failure behavior. Any actual provider verification is reported separately from mocks; unavailable credentials or unverified capabilities remain explicit delivery limitations.

## Boundary

 Use existing configured mainstream trackers. Do not add a distributed lock service, new tracker, or new authority to work around provider limitations without returning the consequential choice to the user.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.
