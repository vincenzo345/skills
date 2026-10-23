---
schema: 1
kind: implementation
id: work/agent-housekeeping/tickets/03-interruption-recovery.md
effort: work/agent-housekeeping
order: 3
state: open
readiness: ready-for-agent
basis:
  ref: work/agent-housekeeping/spec.md
  revision: 1
blocked_by:
- work/agent-housekeeping/tickets/02-owned-service-cleanup.md
---

# Recover interrupted tasks with bounded overhead

**Blocked by:** 2.

**Dependency reason:** Recovery consumes ticket 2's acquisition identities and retention state, plus ticket 1's discoverable workspace/fallback conventions. Recovery of files, processes and Docker must use the same ownership model as ordinary cleanup.

**What it delivers:** A fresh session resuming an interrupted task can find and reconcile its resources, without relying solely on the prior conversation, disrupting active work or scanning unrelated tasks and machine resources.

**Acceptance criteria:**

- A fresh session resuming affected work locates the task note/resources through the configured workspace or the bounded OS temporary fallback. Exercise both locations without supplying lost conversation-only resource IDs.
- Independently establish prior-owner inactivity and current resource identity/use before recovery cleanup. Proven inactive owned resources are removed; active, shared or unverifiable resources are preserved and reported. Time elapsed and filename matching never authorize deletion.
- Exercise interrupted file/process/container work, including a creation/recording interruption boundary and stale process identity. Recover only what can be independently attributed; explicitly retain/report ambiguous partial creation rather than claiming an absolute crash guarantee.
- Retained evidence remains available while needed. On resolution, keep maintained checks and requested deliverables, remove disposable resources and recovery state, and provide only a brief useful summary of exceptions.
- Recovery guidance loads on resumption or explicit recovery, not every unrelated edit. No speculative machine-wide inventory, new registry/helper/hook or perpetual background cleanup is introduced.
- Record recovery-reference and tool-call overhead with comparable model/harness baseline tasks. Consolidate the existing evaluation summary with these cases and account for every specification acceptance row; reuse valid earlier evidence and recheck only behavior affected by integration.
- Update relevant resumed-work instructions and human docs; package checks and final reference consistency pass. Disclose unavailable platform observations. Verify all evaluation fixtures are cleaned or explicitly retained for unresolved evidence.

## Shared delivery requirements

- Preserve the confirmed seam: setup produces guidance, then an agent performs or resumes a task, and the evaluator observes resources, retained verification and overhead. Use the existing temporary-repository replay approach with actual supplied prompts and independent observations; distinguish deterministic checks from model behavior.
- Keep useful maintained lint/configuration and regression tests; classify and clean disposable validation independently from reusable tooling. Core policy applies without invoking a cleanup skill. Use native lifecycle facilities first, with no new helper, hook or skill unless an observed gap is documented and a targeted design change agreed.
- Target approximately 150-250 baseline tokens without treating that target as a hard limit. Record measurement method and scoped incremental reference/tool-call costs for the cases each slice adds. Ordinary tasks with no disposable resources add no housekeeping inventories, recovery files or compulsory reports.
- Each slice includes necessary updates to affected skill instructions, human docs, catalogs and /guide-me, relevant existing package checks, and repository-required installation/delivery checks when applicable. Avoid duplicated policy text.
- Retain one bounded evaluation summary for the effort. Include model/harness, operating system, supplied turns, loaded guidance, outcomes, limitations and fixture cleanup evidence. Do not rerun unaffected scenarios without changed behavior or an unresolved concern. Actual process/Docker observations are required for corresponding claims; unavailable environments remain unmet evidence, not a simulated pass.
- Preserve shared state, other agents' work, durable effort records, prototype evidence and existing worktree rules. Clean only proven owned disposable resources within current task/environment authorization. General machine cleanup and cloud resources are out of scope.


## Basis

[Specification revision 1](../spec.md); [approved breakdown](../issue-plan.md). The recorded behavioral seam is already confirmed. Read /writing-for-agents and its skill-mechanics reference before editing instructions.

## Approval

User explicitly approved the three-ticket breakdown and dependency chain 1 -> 2 -> 3 in issue-plan.md, based on specification revision 1, and authorized implementation on feat/agent-housekeeping with a draft PR targeting main. Keep the PR draft; no merge or auto-merge.
