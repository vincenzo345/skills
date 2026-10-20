---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/01-local-issue-handoff.md
effort: work/wayfinder-reliability
order: 1
state: in-progress
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by: []
---

# 01: Produce and claim a local implementation issue in one stable effort

## What to build

 A small request can become a current spec and approved implementation issue in a stable effort, and implement can resolve and claim that explicitly named issue.

## Acceptance criteria

- [ ] The local setup convention and shared contract agree on typed records, identities, lifecycle, readiness, and authority. Participating producers and consumers reference one contract.
- [ ] to-spec and to-tickets reuse identified effort context, keep request/outcome/current pointers durable, and create only needed artifacts. Similar titles do not merge unrelated efforts.
- [ ] An approved breakdown produces separate implementation issues with current spec basis, explicit dependencies, deterministic order, and durable approval context. Spec readiness does not approve its children.
- [ ] Explicit implementation selection validates kind, readiness, active effort where applicable, basis, and completed blockers, then acquires an exclusive claim before beginning. Missing metadata yields a precise explanation.
- [ ] The minimum local coordinator reads from one authoritative checkout, serializes acquisition, and persists token ownership. Two competing explicit consumers cannot both start. Unsupported access fails closed.
- [ ] A temporary repository fixture runs the producer-to-consumer path and verifies the selected issue and durable records. No map or fabricated decision is required.

## Boundary

 Initial spec publication and an explicit issue path only. Queue selection and whole-spec claims arrive in slice 2; full resume/recovery and implement-spec orchestration arrive in slice 5. Until then, an abandoned claim remains blocking rather than being stolen.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.

## Execution

Implementation authorized by the current implement-spec invocation. Bootstrap ownership: root orchestrator assigned ticket 01 exclusively to implementer `issue01` on branch `implement/wayfinder-01`, in its separate worktree. The shared coordinator is the deliverable of this first slice; no other worker is assigned this issue. Completion will be recorded only after integration and verification.
