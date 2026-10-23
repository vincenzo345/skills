---
schema: 1
kind: spec
id: work/agent-housekeeping/spec.md
effort: work/agent-housekeeping
revision: 1
state: completed
readiness: ready-for-agent
---

# Agent housekeeping with minimal overhead

## Problem Statement

Agents leave one-off validation scripts, test output, processes and Docker resources behind, and sometimes create unnecessary verification infrastructure. Cleanup must preserve maintained linting and regression tests, shared resources and other agents' work. A solution that adds lengthy instructions, recurring scans or reporting rituals would create another maintenance burden.

## Solution

Extend /setup-repo to establish a repository housekeeping convention and temporary workspace. A short persistent baseline applies during ordinary agent work. Detailed resource and recovery guidance loads only when relevant. Existing skills reuse the same policy and native lifecycle mechanisms. Agents classify verification before creating it, clean their disposable resources, and retain only justified deliverables or diagnostic evidence. Interrupted tasks can reconcile resources when resumed.

## User Stories

1. As a maintainer, I want setup to reuse or establish a temporary workspace so agents do not scatter scratch files through the repo.
2. As a maintainer, I want existing checks reused so simple changes do not acquire unnecessary tooling.
3. As a maintainer, I want useful lint rules and regression tests maintained so verification improves over time.
4. As a maintainer, I want one-off checks removed after use so completed tasks leave no disposable clutter.
5. As a maintainer, I want owned services and their disposable data cleaned up so passing and failing tests both release resources.
6. As a collaborator, I want shared resources and active agents' work preserved so cleanup cannot disrupt other work.
7. As a debugging user, I want only useful failure evidence retained with a reason so I can resume without unexplained leftovers.
8. As a returning user, I want an interrupted task to find its recovery information so it can safely reconcile resources.
9. As a user of an unconfigured repo, I want ordinary authorized work to continue using temporary storage so housekeeping setup does not become a universal prerequisite.
10. As a maintainer, I want minimal context and tool-call overhead so housekeeping remains proportionate to the task.

## Implementation Decisions

### Setup and integration

- Extend the existing /setup-repo exploration, review and configuration flow. Discover existing verification commands and temporary-workspace conventions; preserve valid choices and existing contents. When absent, configure a dedicated temporary subtree with narrow ignore rules and unique task directories. Select a collision-free location; never ignore or clean an entire legacy scratch area that may contain durable records.
- Configure the temporary root, how task recovery records are located, and a reference to specialized guidance. Put the concise core obligations and configured location in the existing persistent agent instruction surface. Update the existing block rather than duplicate it. Repeated setup must preserve user changes and avoid duplicate configuration. Create task directories only when used.
- Maintain one policy source. Review integration with /implement, /implement-spec, /tdd, /diagnosing-bugs, /prototype and /wizard; add only necessary pointers or local exceptions. Preserve intentional prototype evidence and established worktree rules. Re-sync affected human docs, catalogs and /guide-me as required by repository conventions.
- No new cleanup skill, registry service, runtime hook or acquisition helper in the initial design. If behavioral evaluation exposes a gap, record the failing case and propose the smallest targeted change before expanding the design. Do not silently weaken an accepted criterion.

### Verification lifetime

- Before creating additional verification resources, identify the behavior or failure being checked and why existing checks are insufficient. Make the lifetime and cleanup choice as part of the existing task plan; do not require a separate planning artifact or narration for each check.
- Maintain a check when it protects a concrete recurring behavior or supplies a repeatable project check, integrated into existing tooling. Useful lint rules, configuration and regression tests remain. A small change alone does not justify extra tests or infrastructure; hypothetical future usefulness does not justify retaining a one-off script.
- One-off validation answers a bounded current question. Use the configured task workspace or a native temporary fixture, attach teardown before or alongside acquisition, and remove disposable scripts and outputs after use. Classify generated output independently from its maintained checker. Promote a reproduction into the existing test suite only when it establishes an actual reusable regression case.
- These rules operate within existing task and environment authorization. They do not grant unrelated installation, service changes or deletion authority.

### Ownership, cleanup and retention

- Cover disposable files/reports, task-owned local processes, and Docker containers with their disposable networks and volumes. Prefer native fixtures, structured teardown and scoped service commands. Do not rely on a final conversational reminder as the sole cleanup path.
- Use unique task identity and exact resource identity. Before starting resources that can outlive the command, record recoverable intent and the intended namespace or location; capture resulting identities promptly. Reconcile partial acquisition only where native identity or ownership evidence permits it. Unknown leftovers remain reported, never guessed away.
- Remove only proven owned, no-longer-needed disposable resources. Validate resolved filesystem boundaries and avoid traversing links into unrelated locations. A name, untracked status, ignore rule, old timestamp or reused process ID is insufficient authority. Confirm process identity and Docker ownership before stopping or deleting them.
- Preserve pre-existing/shared resources, other active tasks, maintained tooling, caches, durable effort records and requested deliverables. No broad filesystem cleanup or global Docker pruning. Worktree cleanup remains governed by its existing integration and ownership rules.
- On success or failure, stop disposable services when no longer needed. Retain minimum diagnostic evidence for unresolved work; keep a live environment only for ongoing debugging or user review. Record its purpose and revisit condition. Remove disposable evidence and recovery state when reconciled, while preserving useful regression tests. Report intentional retention or cleanup failure briefly; never claim cleanup succeeded when inspection was unavailable.

### Recovery and missing configuration

- Keep at most one small recovery note per resource-producing task when resources or evidence may survive interruption. It names repository/task identity, owner evidence, owned locations/resources, cleanup action and retained-evidence reason. Reuse available task context; do not create per-command logs or a second task tracker.
- On resuming an interrupted task or an explicit recovery request, consult its configured recovery location. Reconcile only after establishing that the prior owner is inactive and the resource is not shared or in use. Use available controller/process evidence; if identity or inactivity cannot be verified, preserve and report the resource. Age alone never authorizes recovery.
- In an unconfigured repository, use a dedicated OS temporary namespace discoverable from canonical repository identity, with unique task children. Keep the recovery note there when required, and retain a pointer in the task handoff when available. A resumed task uses that bounded namespace, not a scan of the whole machine. Suggest /setup-repo once; if verification requires repo-local files, resolve the setup choice before inventing a lasting convention.
- Recovery is scoped to the next session resuming affected work. Ordinary unrelated tasks do not perform speculative background inventories. No guarantee covers automatic cleanup while Codex is closed, inaccessible hosts or absent ownership evidence. Platform-specific instructions must use available native facilities and report unsupported observations rather than treating them as clean state.

### Context and execution cost

- Aim for approximately 150-250 tokens in the always-loaded baseline, including configured path and reference. This is a design target, not an approved hard limit. Measure with a named tokenizer; if unavailable, report a labeled estimate and character count. Explain deviations without dropping ownership or lifetime obligations.
- Load resource-specific guidance only when creating that resource, recovering an interrupted task or resolving retention ambiguity. Explicit triggers must be discoverable in the baseline. Do not load this specification, interview history or research as routine housekeeping context.
- Ordinary edits creating no disposable resources add zero housekeeping inventory tool calls, recovery files or mandatory reporting artifacts. Resource-producing work uses only scoped ownership and cleanup observations; combine observations with existing verification where possible. Do not repeatedly rediscover setup or reread the same unchanged guidance within a task.

## Testing Decisions

### Confirmed behavioral seam

One end-to-end seam: /setup-repo output is consumed by an agent performing or resuming work, and the evaluator observes filesystem/resource outcomes, retained verification and execution overhead. The user explicitly confirmed this seam. Exercise ordinary work without requiring a named cleanup skill.

Use the repository's existing temporary-repository behavioral replay pattern with supplied human turns and independently captured outcomes. Existing package and installer checks support packaging integrity; text matching or directory-creation tests alone cannot establish housekeeping behavior. Test external outcomes rather than private implementation details or the model's claimed compliance.

### Measurable acceptance criteria

| Case | Required observation |
| --- | --- |
| Fresh and existing setup | A usable temporary convention is configured when absent; an existing valid convention and user content survive; rerunning setup adds no duplicate block or ignore rule. Durable tracker content remains visible and unchanged. |
| Ordinary edit | Existing verification is used; no unjustified script/service is created. Zero added housekeeping inventory calls, recovery notes, permanent reports or specialized-reference reads when their triggers do not apply. |
| Maintained verification | A justified reusable lint/configuration change or regression test is integrated and remains runnable after cleanup; disposable outputs do not become permanent merely because the checker is maintained. |
| One-off validation | On task completion, zero owned disposable files, processes or service resources remain unless explicitly retained with purpose and revisit condition. Useful deliverables remain unchanged. |
| Failed test and partial startup | Teardown handles already-acquired resources; minimal useful evidence is retained. Any uncertain or inaccessible resource is reported as unresolved, not counted as cleaned. |
| Interrupted task | A fresh session resuming the task locates recovery state without relying solely on lost conversation context. Proven inactive, owned resources are reconciled; unknown or live ownership remains untouched and reported. Exercise configured and OS-temporary fallback locations. |
| Concurrent tasks | Cleaning one task changes zero resources belonging to another active task or shared/pre-existing state. Include similar names, stale process identity and a filesystem link escaping the temporary boundary. |
| Intentional retention | A requested deliverable, prototype evidence and useful regression checks survive; retained diagnostics have an actionable revisit condition. Disposable bookkeeping disappears once all task resources are reconciled. |
| Overhead | Record baseline instruction tokens, triggered reference tokens, housekeeping tool calls and artifacts for ordinary-edit, one-off, container and recovery cases. Compare equivalent baseline tasks on the same recorded model/harness. Explain increases; do not claim savings without measurements. |
| Package integration | Existing relevant package checks pass; changed skill docs, discovery metadata and router descriptions agree with delivered behavior. |

Use isolated disposable fixtures and verify their cleanup. Include actual local process and Docker resource observations for claims about those resource types; unavailable environments are evidence gaps, not passing simulations. Record runtime/model, operating system, loaded instructions, supplied turns, before/after observations and failures in one bounded evaluation summary. Report deterministic checks and model behavior separately. Each acceptance case needs an observed run; a bounded pass is not proof of universal agent compliance. Use existing tooling rather than building a general evaluation platform.

## Out of Scope

Implementation tickets or implementation during specification publication; historical repository-wide cleanup; cloud resource lifecycle; global caches or installed-tool removal; replacement of worktree ownership rules; background crash reapers; guaranteed cleanup without a running agent; new hooks/helpers/skills without demonstrated need; new approval rituals for routine owned cleanup.

## Further Notes

The user confirmed the design and explicitly required token efficiency. The testing seam was separately confirmed through the question tool. Publication may therefore mark this specification ready-for-agent; this denotes specification readiness and does not authorize implementation or a ticket breakdown.

This extends established skills to address an observed failure in this fork. Preserve the stable-effort-workspace decision and the distinction between hard setup dependencies and guidance that degrades gracefully.

Sources and authority: [effort](README.md), [accepted answers and efficiency requirement](discovery.md), [primary-source research](research/cleanup-patterns.md), [existing behavioral validation](../wayfinder-reliability/validation.md), [replay prior art](../../scripts/fixtures/wayfinder-replays.md), [stable workspace decision](../../docs/adr/0001-stable-effort-workspaces.md), and [setup dependency decision](../../.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md). Superseded research proposals and earlier unanswered interview rounds do not override the later accepted answers.

## Completion evidence

All three approved issues integrated on feat/agent-housekeeping with verified receipts; final review corrections integrated at515e825. Standards findings resolved and Spec review clear. Behavioral cases, measured overhead, passing repository checks and bounded evidence limitations are recorded in validation.md. DraftPR7 remains unmerged. Two empty hidden fixture directories remain policy-blocked; no live test resources remain.
