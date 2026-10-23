# Proposed implementation breakdown

Status: approved by the user; implementation issues published against revision 1. Implementation is authorized on the feature branch with a draft PR, without merging to main.

Basis: [specification revision 1](spec.md). Reuse this effort. The proposed dependency chain is 1 -> 2 -> 3. Each slice delivers behavior, its relevant instruction/doc integration and observable validation; there is no separate prose, documentation or testing layer. No preliminary refactor is justified by the inspected integration points.

## Shared delivery requirements

- Preserve the confirmed seam: setup produces guidance, then an agent performs or resumes a task, and the evaluator observes resources, retained verification and overhead. Use the existing temporary-repository replay approach with actual supplied prompts and independent observations; distinguish deterministic checks from model behavior.
- Keep useful maintained lint/configuration and regression tests; classify and clean disposable validation independently from reusable tooling. Core policy applies without invoking a cleanup skill. Use native lifecycle facilities first, with no new helper, hook or skill unless an observed gap is documented and a targeted design change agreed.
- Target approximately 150-250 baseline tokens without treating that target as a hard limit. Record measurement method and scoped incremental reference/tool-call costs for the cases each slice adds. Ordinary tasks with no disposable resources add no housekeeping inventories, recovery files or compulsory reports.
- Each slice includes necessary updates to affected skill instructions, human docs, catalogs and /guide-me, relevant existing package checks, and repository-required installation/delivery checks when applicable. Avoid duplicated policy text.
- Retain one bounded evaluation summary for the effort. Include model/harness, operating system, supplied turns, loaded guidance, outcomes, limitations and fixture cleanup evidence. Do not rerun unaffected scenarios without changed behavior or an unresolved concern. Actual process/Docker observations are required for corresponding claims; unavailable environments remain unmet evidence, not a simulated pass.
- Preserve shared state, other agents' work, durable effort records, prototype evidence and existing worktree rules. Clean only proven owned disposable resources within current task/environment authorization. General machine cleanup and cloud resources are out of scope.

## 1. Configure housekeeping and complete ordinary verification cleanly

**Blocked by:** None.

**What it delivers:** After setup, an agent performing an ordinary edit or a file-based verification task uses a known temporary workspace, retains useful maintained checks and removes one-off validation artifacts. An unconfigured repository can use the OS-temporary fallback without silently installing lasting configuration.

**Scope:** Extend setup discovery and configuration, supply the concise persistent baseline and conditional guidance entry points, define the task namespace/recovery-record location for later resource cases, and integrate lifetime rules into relevant existing workflows. This slice must demonstrate actual file behavior, not merely create configuration. Recovery execution and service-specific lifecycle handling follow in tickets 2 and 3; avoid dangling references or claiming those capabilities complete before they land.

**Acceptance criteria:**

- Fresh setup establishes a usable isolated temporary convention with narrow ignore rules. Existing setup, user customizations, legacy scratch/tracker records and repeated setup are preserved without duplicated blocks or broad ignore rules.
- Ordinary work reuses existing checks and creates no unjustified script/service. A task creating no disposable resources incurs zero housekeeping inventory calls, recovery files, mandatory reporting artifacts or untriggered specialized-reference reads.
- A useful reusable lint/configuration change and a regression check remain integrated and runnable after cleanup. A genuinely one-off validation script and its disposable outputs are removed on completion; the output lifetime is independent of the maintained checker.
- Ownership is task-specific; another task's files and shared/pre-existing files survive. Cleanup does not follow a filesystem link outside the temporary boundary. Requested deliverables and retained prototype evidence survive.
- Minimal useful file-based failure evidence has a reason and revisit condition. Disposable evidence is removed when resolved; it is not retained merely for hypothetical reuse.
- Unconfigured work uses a bounded OS temporary namespace derived from repository identity with unique task children, suggests /setup-repo once, and resolves any actual repo-local workspace requirement before creating a convention. Task recovery locations are discoverable for ticket 3.
- Replay setup -> ordinary task -> observed files for fresh/existing/repeated setup, reusable checks, one-off validation and fallback cases. Record baseline size and ordinary-edit/one-off overhead, relevant docs/package consistency and fixture cleanup.

## 2. Release task-owned processes and Docker resources

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

## 3. Recover interrupted tasks with bounded overhead

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

## Coverage and publication

| Specification acceptance case | Owning slice |
| --- | --- |
| Fresh/existing setup and ordinary edit | 1 |
| Maintained verification and one-off files | 1 |
| One-off service resources, failed test and partial startup | 2 |
| Interrupted task, configured and fallback | 3 |
| Concurrent ownership and intentional retention | 1 for files; 2 for active services; 3 for recovery |
| Context/tool-call overhead and package integration | Every slice for its behavior; 3 consolidates coverage |

After the user approves this exact breakdown or its revision, publish three self-contained implementation issues through the configured producer, blockers first, with specification revision 1 as their basis and the actual approval recorded. Each published body must include its applicable shared delivery requirements rather than relying on this draft alone. Stop after publication; implementation requires a subsequent user instruction.

## Published issues

- [01-setup-and-file-lifetime](tickets/01-setup-and-file-lifetime.md)
- [02-owned-service-cleanup](tickets/02-owned-service-cleanup.md)
- [03-interruption-recovery](tickets/03-interruption-recovery.md)
