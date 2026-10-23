---
schema: 1
kind: implementation
id: work/agent-housekeeping/tickets/02-owned-service-cleanup.md
effort: work/agent-housekeeping
order: 2
state: open
readiness: ready-for-agent
basis:
  ref: work/agent-housekeeping/spec.md
  revision: 1
blocked_by:
- work/agent-housekeeping/tickets/01-setup-and-file-lifetime.md
---

# Release task-owned processes and Docker resources

**Blocked by:** 1.

**Dependency reason:** Consumes ticket 1's configured/fallback task namespace, core ownership/lifetime rules and conditional reference entry points. A separate service path should not invent competing setup or policy.

**What it delivers:** An agent that needs a local process or Docker service acquires it with scoped ownership and native teardown, then releases owned disposable resources on successful verification, failed tests and partial startup, while preserving shared services and intentional diagnostics.

**Acceptance criteria:**

- The need for a new service is tied to a concrete verification gap. Only relevant service guidance loads; service-free work retains ticket 1's no-extra-inventory behavior.
- Establish task namespace and recoverable intent before acquisition, then capture exact resulting identities promptly. Use at most one small task recovery note when required, rather than per-command logs or another tracker. Identify resources sufficiently for later recovery without claiming the note proves inactivity.
- Actual local process and Docker cases leave zero owned, unneeded disposable processes, containers, networks and volumes after normal completion or ordinary failure. Scope teardown precisely; shared caches, external/persistent volumes, maintained tooling and pre-existing services survive.
- Partial startup cleans already-acquired resources where ownership is established. Unknown identity, inaccessible runtime or incomplete cleanup is reported honestly with necessary recovery information, never as clean state.
- Concurrent active tasks and similarly named resources survive another task's cleanup. Stale/reused process identity is insufficient grounds for termination. Native identity checks distinguish current resources from recorded identifiers alone.
- Keep live resources only for continuing debugging or requested review, with purpose and revisit condition. Remove completed tasks' disposable evidence and bookkeeping once all resources are reconciled.
- Replay configured task execution with real local process/Docker observations across success, failure, partial acquisition and concurrent ownership. Measure added service-reference tokens and scoped tool calls, update relevant docs/package checks, and verify fixture cleanup. Missing runtime access prevents claiming the corresponding acceptance case passed.

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
