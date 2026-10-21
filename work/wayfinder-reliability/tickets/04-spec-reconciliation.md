---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/04-spec-reconciliation.md
effort: work/wayfinder-reliability
order: 4
state: completed
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/01-local-issue-handoff.md
integration:
  ref: integration/wayfinder-reliability
  commit: f0f045dfe299485377c23c5d8fe5df3dea7ba0e9
  verified_tip: 4d07c8576b66de84e3d79339db688cad81fcca43
---

# 04: Revise specs without leaving obsolete issues actionable

## What to build

 A materially changed spec preserves its earlier basis and prevents unfinished issues from starting or completing against unreconciled requirements.

## Acceptance criteria

- [x] Material changes increment the revision and retain resolvable previous content. Editorial corrections do not require false material revisions.
- [x] Current spec and effort references agree; publication uses the same coordination boundary as claims. Interrupted publication fails closed and retries preserve retained history.
- [x] All mismatched unfinished issues initially fail currency checks. Unaffected issues advance with explicit no-impact rationale; affected issues update scope and readiness, with renewed approval when the breakdown materially changes.
- [x] Completed issues retain their historical basis. Follow-up requirements become new work rather than retroactively changing completed evidence.
- [x] Active consumers revalidate before publishing results or completing; changed bases pause dependent work without stealing claims or discarding existing work.
- [x] Fixtures cover affected and unaffected siblings, historical lookup, interrupted publication, concurrent publication/acquisition, and completed-work preservation.

## Boundary

 This slice implements the shared publication and validation operations. Other consumers, including implement-spec and remote adapters, must reuse them rather than invent revision policy.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.

## Completion evidence

Integrated in f0f045d. Combined 23 work tests pass, including interrupted publication recovery, immutable history, individual impact reconciliation, publication/acquisition race and stale active-claim rejection. Package validation passes.
