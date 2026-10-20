---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/02-work-selection.md
effort: work/wayfinder-reliability
order: 2
state: in-progress
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/01-local-issue-handoff.md
---

# 02: Select eligible work by queue priority or explicit scope

## What to build

 Bare implement finds the first eligible implementation issue; explicit effort, issue, and spec inputs reliably constrain selection.

## Acceptance criteria

- [ ] Queue order controls cross-effort priority; issue order controls selection within an effort. Blocked or claimed issues do not prevent independent eligible work.
- [ ] Explicit references override queue position and membership without bypassing eligibility. An invalid explicit target never falls through to unrelated work.
- [ ] Bare selection excludes decisions, history, waiting/terminal efforts, stale bases, and undecomposed specs. Missing readiness, invalid ordering, and unavailable authority have distinct diagnostics.
- [ ] An indeterminate higher-priority effort prevents claiming that a lower effort is first eligible. Known ineligibility permits traversal to continue.
- [ ] An explicitly selected undecomposed spec and a self-contained issue remain supported. Decomposed spec selection uses its issue graph.
- [ ] Whole-spec and child-issue claims conflict. Completed specs cannot authorize repeat execution; completed efforts leave the queue without changing paths.
- [ ] Fixtures cover multiple efforts, independent blocked work, explicit overrides, optional inputs, scope conflicts, and no-eligible-work explanations.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.
