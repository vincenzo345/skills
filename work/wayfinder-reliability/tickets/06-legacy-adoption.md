---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/06-legacy-adoption.md
effort: work/wayfinder-reliability
order: 6
state: open
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
  - work/wayfinder-reliability/tickets/02-work-selection.md
  - work/wayfinder-reliability/tickets/04-spec-reconciliation.md
---

# 06: Adopt legacy records without breaking references

## What to build

 Explicit legacy inputs remain usable, and an opt-in migration can bring classified records into the stable effort layout without losing identities or historical bases.

## Acceptance criteria

- [ ] Explicit legacy references normalize recognized kinds, readiness, parents, and dependencies without changing their originals. Ambiguous records remain blocked with precise missing-information explanations.
- [ ] A read-only migration plan classifies records and reports identity collisions, ambiguous types, input fingerprints, and inbound references.
- [ ] Applying a reviewed plan checks for changed inputs, preserves IDs and history, maintains forwarding references where needed, and leaves one writable authority.
- [ ] Adoption sequencing prevents old readers from mutating forwarding copies. Interrupted application is resumable or leaves an explicit recovery state.
- [ ] Fixtures demonstrate resumption from a legacy reference, decision/implementation separation, preserved dependency IDs, valid inbound links, and rejection of stale or ambiguous plans.

## Boundary

 No automatic migration, renumbering, or moving remote issues. The implementation fixture is not permission to migrate unrelated user repositories.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.
