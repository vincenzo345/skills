---
schema: 1
kind: implementation
id: work/agent-housekeeping/tickets/01-setup-and-file-lifetime.md
effort: work/agent-housekeeping
order: 1
state: open
readiness: ready-for-agent
basis:
  ref: work/agent-housekeeping/spec.md
  revision: 1
blocked_by: []
---

# Configure housekeeping and complete ordinary verification cleanly

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
