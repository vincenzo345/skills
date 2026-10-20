---
schema: 1
kind: implementation
id: work/wayfinder-reliability/tickets/05-concurrent-implementation.md
effort: work/wayfinder-reliability
order: 5
state: in-progress
readiness: ready-for-agent
basis:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
blocked_by:
- work/wayfinder-reliability/tickets/02-work-selection.md
- work/wayfinder-reliability/tickets/04-spec-reconciliation.md
integration:
  ref: integration/wayfinder-reliability
  commit: 39aa75dfb4adad3a3fe38b1f796761c6a0f82f30
  verified_tip: 4d07c8576b66de84e3d79339db688cad81fcca43
---

# 05: Resume claims and integrate concurrent implement-spec workers safely

## What to build

 Multiple local implementation sessions and implement-spec workers share live authority, safely resume work, and expose dependencies only after integration.

## Acceptance criteria

- [x] Worktrees share the authoritative record source and claim coordinator; stale worktree metadata cannot grant ownership or overwrite live status.
- [x] Resume validates the ownership token, current scope, basis, and dependencies. Same user/branch and elapsed time never substitute for ownership.
- [x] Explicit recovery establishes that the old worker has stopped, preserves its work pointer, invalidates its token, and grants replacement ownership atomically. If stoppage cannot be established, the claim remains blocking.
- [x] implement-spec claims individual frontier issues through the same protocol. Independent issues can proceed concurrently; a dependent issue waits until blocker work is available on the integration branch.
- [x] Process/crash and stale-copy fixtures establish exclusive acquisition, token-safe release, interrupted-operation behavior, scope conflicts, and integrated dependency readiness on supported local platforms.
- [x] Unsupported independent-clone or multi-machine local concurrency is reported clearly. Git ownership errors remain access failures, not empty frontiers.

## Basis and approval

Basis: [specification revision 2](../spec.md) and [shared work-record contract](../design.md).

Vince approved the seven-slice breakdown and its dependency graph on 2026-10-20 with "sounds good" in response to the proposal review. See the [approval record](../issue-plan.md#approval-and-publication). This issue is published from that approved breakdown; readiness does not bypass blockers or the standing planning-only boundary. Implementation requires a subsequent implementation instruction.

## Delivery requirements

Apply the [shared delivery requirements](../issue-plan.md#delivery-requirements-shared-by-every-slice), including synchronized skill documentation/router guidance, appropriate tests, package validation, and integration-branch confirmation. No work has been claimed or started by publishing this record.

## Completion evidence

Integrated at 39aa75d. Five ownership/integration scenarios and the combined 29-test work-record suite passed on Windows; token resume, stopped-worker recovery, stale worktrees, killed lock holder, and verified commit ancestry exercised.

## Integrated review follow-up

Reopened under the user-authorized discrepancy fix: Spec review reproduced direct-spec completion after child publication, stranding the child.
