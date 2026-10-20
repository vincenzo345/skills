---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/07-remote-authority.md
effort: work/wayfinder-reliability
order: 7
state: completed
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/03-planning-continuity.md
- work/wayfinder-reliability/tickets/05-concurrent-implementation.md
integration:
  ref: integration/wayfinder-reliability
  commit: 2535dedfd85b359948780083b8e15f10bb9edd67
  verified_tip: 2535dedfd85b359948780083b8e15f10bb9edd67
---

# 07: Respect remote authority and bound remote concurrency

## What to build

 The configured remote tracker participates in the same planning-to-implementation handoff while keeping remote state authoritative and enforcing the documented concurrency boundary.

## Acceptance criteria

- [x] Existing supported remote adapter guidance maps the shared record facts, current spec basis, readiness, native dependencies, ordering, and completion semantics without creating a mutable local status mirror.
- [x] The complete handoff preserves remote map/decision authority and local asset links. Implementation queries current remote state before selection and before completion.
- [x] For each supported claim path, document and verify conditional exclusive acquisition or one established shared controller. A two-contender test is required before claiming concurrent support.
- [x] If a provider lacks the required capability, automatic concurrent claiming reports unsupported behavior. Assignment alone and per-worktree claims are not accepted as proof of exclusivity.
- [x] Unavailable remote records, incomplete dependency queries, stale revisions, canceled blockers, and conflicting existing claims fail with specific explanations.
- [x] Adapter contract fixtures cover authority and failure behavior. Any actual provider verification is reported separately from mocks; unavailable credentials or unverified capabilities remain explicit delivery limitations.

## Boundary

 Use existing configured mainstream trackers. Do not add a distributed lock service, new tracker, or new authority to work around provider limitations without returning the consequential choice to the user.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.

## Completion evidence

Six remote contract fixtures and package validation passed. GitHub/GitLab primary documentation checked; authoritative fresh reads, outcome distinctions, incomplete dependencies and conflicting ownership exercised. Both contenders fail closed for unsupported automatic claiming. No live provider write or exclusive claim proof; evaluator is read-only, not an API client.

## Integrated review follow-up

Reopened for two read-only preview discrepancies: accept explicit self-contained null effort/basis, and reject unknown or unready specification readiness. Local blockers have been reverified and completed.

## Completion evidence

Review corrections integrated at 2535ded. All nine remote fixtures passed; independent reviewer confirmed explicit-null standalone handling, missing-field diagnostics, independent spec readiness, and acquired-null basis continuity. Inspection remains read-only; automatic remote claiming remains unsupported.
