---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/02-work-selection.md
effort: work/wayfinder-reliability
order: 2
state: completed
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/01-local-issue-handoff.md
integration:
  ref: integration/wayfinder-reliability
  commit: 4481b939df9427e909f6aeb55d8af61f9f91b67d
  verified_tip: 4d07c8576b66de84e3d79339db688cad81fcca43
---

# 02: Select eligible work by queue priority or explicit scope

## What to build

 Bare implement finds the first eligible implementation issue; explicit effort, issue, and spec inputs reliably constrain selection.

## Acceptance criteria

- [x] Queue order controls cross-effort priority; issue order controls selection within an effort. Blocked or claimed issues do not prevent independent eligible work.
- [x] Explicit references override queue position and membership without bypassing eligibility. An invalid explicit target never falls through to unrelated work.
- [x] Bare selection excludes decisions, history, waiting/terminal efforts, stale bases, and undecomposed specs. Missing readiness, invalid ordering, and unavailable authority have distinct diagnostics.
- [x] An indeterminate higher-priority effort prevents claiming that a lower effort is first eligible. Known ineligibility permits traversal to continue.
- [x] An explicitly selected undecomposed spec and a self-contained issue remain supported. Decomposed spec selection uses its issue graph.
- [x] Whole-spec and child-issue claims conflict. Completed specs cannot authorize repeat execution; completed efforts leave the queue without changing paths.
- [x] Fixtures cover multiple efforts, independent blocked work, explicit overrides, optional inputs, scope conflicts, and no-eligible-work explanations.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.

## Completion evidence

Integrated in 4481b93. Eight selection tests plus six handoff tests pass; package validation passes. Covers explicit scope, queue priority, independent blocked work, historical and stale inputs, unavailable authority, claim conflicts and completion.
