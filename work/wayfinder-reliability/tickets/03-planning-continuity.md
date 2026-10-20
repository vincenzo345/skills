---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/03-planning-continuity.md
effort: work/wayfinder-reliability
order: 3
state: in-progress
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/01-local-issue-handoff.md
---

# 03: Preserve planning context and Wayfinder session boundaries

## What to build

 Wayfinder and grill-with-docs carry durable planning context into the same effort that to-spec and to-tickets already consume.

## Acceptance criteria

- [ ] Maps and decision tickets live separately from implementation issues and remain authoritative for planning answers. Discovery holds ordinary requirements and findings; glossary and qualifying ADRs remain project-wide.
- [ ] Charting records the destination, breadth-first decisions, and fog, then stops with the map link, next decision by name, and next invocation or required input.
- [ ] Replies to an unresolved decision continue that decision. One non-research resolution per session and the research exception remain intact.
- [ ] Human judgments stay unresolved until answered. Proposed experiments name the destination decision and explain how possible results inform it before becoming prerequisites.
- [ ] Invalidated decisions preserve earlier answers, identify replacements, update current references, and trigger dependent review. A session ending never marks the map complete by itself.
- [ ] Structural fixtures verify artifact identity and handoff links. Separate synthetic behavioral replays cover continuation, human judgment, legitimate stops, and the Articles scope-drift regression; reports distinguish observed behavior from structural proof.

## Boundary

 Preserve upstream planning behavior. This slice does not authorize automatic multi-decision planning or application implementation.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.
