---
schema: 1
kind: spec
id: work/agent-workflow-reliability/spec.md
effort: work/agent-workflow-reliability
revision: 5
state: current
readiness: ready-for-agent
---

# Durable knowledge, safe completion, and lightweight agent guidance

## Problem Statement

Agents can scatter design knowledge, leave disposable execution work behind, or discard useful plans and findings. Guidance can also exist in a file the active agent never loads. Adding more policy, folders and reporting can make these problems harder to manage.

Users need discoverable project knowledge, safe task completion and concise guidance that applies during ordinary work.

## Solution

Deliver three objectives through existing skills:

1. **Give durable knowledge a clear home.** Setup reuses appropriate documentation locations and a short index, and makes the essential guidance discoverable in Codex and Claude.
2. **Define what survives completion.** Preserve maintained verification, deliverables, plans and useful findings while retiring owned disposable work through existing housekeeping.
3. **Prove the outcomes with minimal burden.** Observe setup, one bounded design/prototype lifecycle and a matched ordinary edit at the confirmed end-to-end seam.

Repository instructions guide behavior; they do not guarantee compliance or provide an enforcement boundary. Validate in isolated fixtures before any separately authorized live adoption.

## User Stories

1. As a maintainer, I want setup to reuse suitable locations and preserve my instructions, so that configuration does not create competing structures or policies.
2. As a Codex or Claude user, I want fresh sessions to discover the repository guidance, so that behavior does not depend on which agent I open.
3. As a contributor, I want a short index to current architecture, module, data-model and decision knowledge, so that I can find the relevant material selectively.
4. As a designer, I want accepted decisions linked to their evidence and distinguished from proposals and implementation, so that future work uses the correct authority.
5. As a planner, I want approved plans, effort history and unique reasoning retained at stable paths, so that cleanup preserves context.
6. As a developer, I want maintained linting, regression tests, fixtures and requested deliverables preserved, so that useful verification and outcomes survive.
7. As an experimenter, I want findings and source references captured before disposal, so that the answer outlives the prototype environment.
8. As a collaborator, I want cleanup and recovery to respect ownership and active use, so that shared resources and other agents' work remain safe.
9. As a user, I want ordinary edits to incur no added housekeeping actions or bookkeeping, so that reliability stays lightweight.
10. As a reviewer, I want observed outcomes and comparable overhead measurements, so that completion claims are credible.

## Implementation Decisions

### Setup and knowledge authority

Extend the existing reviewed setup flow. Reuse suitable documentation, domain, decision, tracker and temporary locations before proposing new ones. Establish a usable temporary workspace when absent; create task children on demand. Create documentation collections only when useful content belongs there.

Provide one short current-knowledge index. Architecture records system responsibilities and runtime boundaries; codebase design records module interfaces, dependencies, invariants and testing seams; data-model design records identity, relationships, integrity and lifecycle; decision records explain consequential choices and supersession. Keep editable diagrams beside their document and reusable synthetic data with maintained fixtures.

Existing domain records own business meaning; schemas and migrations own implemented structure. Documents explain intent and constraints rather than duplicating a glossary or schema. Distinguish proposed intent, accepted choices and implemented behavior in concise prose where material.

Keep proposals, approved plans, research and evidence in the existing effort. Promote accepted current knowledge into its maintained document with a link to the effort evidence. Preserve stable effort paths and prior revisions; remove completed efforts from the active queue instead of relocating them.

Repeated setup preserves content, custom paths, tracker authority, user edits and narrow ignore rules. Confirm that published references resolve and intended permanent documents are visible to Git. Resolve ignore conflicts through a targeted reviewed change that preserves unrelated protected/generated content.

### Instruction discovery and placement

Setup inspects the instruction entry points used by Codex and Claude and proposes the smallest compatible connection to one authoritative guidance source. Replace the filename-preference assumption with verified discovery. Preserve existing instruction structure and scope; when both entry points are needed, use brief appropriate references rather than duplicated policy blocks.

Keep the essential survival and ownership obligations inline in the authoritative baseline, with precise conditional pointers:

| Material | Authoritative home and trigger |
| --- | --- |
| Core housekeeping obligations and repository locations | Concise repository guidance, reached through each supported agent's loaded entry point |
| Current project knowledge | Short index; follow the relevant entry when the task needs design context |
| Temporary placement and retention detail | Existing common housekeeping reference, when creating disposable resources or resolving retention ambiguity |
| Process/container acquisition or reconciliation | Existing service branch, before the relevant resource operation |
| Interrupted-task resumption | Existing recovery branch, when resuming or explicitly reconciling interrupted work |
| Implementation dependency, risk controls and evaluation | This effort's implementation handoff and evidence, not routine task context |

Repository-wide guidance applies within the configured project. Personal defaults across repositories and user-level configuration remain outside this effort.

Connect design's existing compact decision record and prototype's existing findings/source capture to the configured locations. Keep each obligation in one authoritative place. Load only the relevant branch and reuse unchanged configuration and task state.

### Retention and cleanup

| Retain | Remove when no longer needed |
| --- | --- |
| Maintained documentation, consequential decisions and unique useful reasoning | Alternate drafts or scratch notes with no remaining unique value |
| Approved plans, specifications, approvals and stable effort history | One-off validators and raw generated output |
| Maintained linting, regression tests and reusable fixtures | Disposable prototype execution files and owned temporary environments |
| Requested deliverables, prototype conclusions and necessary source references | Resolved temporary bookkeeping and recovery state |

Classify purpose and choose ownership, lifetime and cleanup before creating disposable work through existing planning, without a new form or per-file metadata. Names, extension, age and ignored status do not establish disposability. A useful unaccepted proposal may still deserve retention.

Capture the prototype's question, findings, limitations and necessary source/reproducibility reference before retiring its execution environment. Preserve the existing prototype source-branch convention; a framework-dependent experiment may need an owned throwaway worktree near its module.

Reuse existing housekeeping for native teardown, exact resource identities, partial acquisition, resolved path boundaries, links/junctions, shared resources and next-session recovery. Clean no-longer-needed owned work after success or failure. Retained diagnostics or review environments need a purpose and revisit condition in existing context or the existing recovery note. Reconcile them when that condition is met.

Retire disposable worktrees through the existing Git ownership/integration workflow after accounting for unique work. Ambiguous ownership or active use prevents deletion and requires a truthful unresolved outcome. A session ending does not establish safe disposal; a clean Git status does not prove resource absence.

### Lightweight operation and enforcement boundary

An ordinary edit without relevant documentation or disposable work adds zero housekeeping calls, specialized-reference reads, recovery notes, mandatory reports or other bookkeeping. The specification, retrospective and implementation controls are not ordinary loaded guidance.

Treat 150-250 baseline tokens as a proposed design target, not a hard limit. Measure actual persistent text, cumulative triggered context and execution overhead separately. Every retained artifact must serve a reader, reusable purpose, history obligation or necessary evidence.

Prefer existing checks and native lifecycle mechanisms. Keep new hooks, helpers and separate cleanup skills deferred. A potential hook requires an observed failure, a precisely checkable condition, verified runtime/event coverage, defined failure behavior, false-positive handling and measured execution/context overhead. Judgments such as whether a test remains useful belong in contextual guidance.

A demonstrated gap permits a targeted proposal, not implementation approval. Any hook/helper/new skill needs separate approved scope before implementation. Automatic deletion and repeated policy-injection hooks are excluded.

### Delivery prerequisite and scope control

skillsrepo is the sole implementation, work-record and integration authority. Preserve existing invocation, installation, domain, security and compliance requirements.

Before dependent implementation, record the exact accepted housekeeping commit and verify that it is an ancestor of the authorized integration branch. Identify applicable prior evidence and only the behavior this effort changes. If the basis is absent, block dependent work; planning may continue. Revalidate if the basis changes.

Each proposed implementation Issue maps to an objective and T1-T3 criteria, with relevant human documentation, catalogs/router changes and validation in the same slice. Review the final diff against those deliverables. Supporting changes need a direct acceptance reason; deferred improvements remain separate.

## Testing Decisions

### Confirmed seam and acceptance cases

Reuse the confirmed seam: setup generates guidance, a fresh agent uses it to perform or resume authorized design/prototype work, and an evaluator inspects durable artifacts, resource outcomes and overhead. Codex/Claude discovery adds runtime coverage within this seam, not a new testing seam.

| Case | Observable acceptance |
| --- | --- |
| **T1: Setup and discovery** | Fresh setup provides usable knowledge locations/index and a temporary convention. Custom/repeated setup preserves content, user choices, tracker authority and one policy source. References resolve; permanent documents are Git-visible. Fresh Codex and Claude sessions discover the generated guidance without the task explicitly supplying the policy or telling the actor to read a particular instruction file |
| **T2: Design/prototype through cleanup** | One coherent question yields relevant architecture/module/data reasoning, accepted conclusions linked to evidence and retained effort history. Maintained lint/checks, a reusable fixture and requested deliverable survive. Findings and source reference remain after owned one-off files, raw output and disposable environment are retired. A diagnostic is retained with a reason/revisit condition and reconciled afterward. Another task's sentinel is unchanged; an ambiguous-ownership artifact is preserved and reported unresolved |
| **T3: Ordinary edit** | Matched baseline/candidate edits complete with zero added housekeeping calls, specialized reads, notes or mandatory reporting. Persistent/triggered context and execution differences are recorded separately |

Bound T2 before execution to one question, one lifecycle, one module interface, minimum synthetic data and one disposable environment using existing tooling. A small case-record lifecycle is sufficient; the actor's task asks the design question rather than dictating files or success claims. Stop extending the example once the required observations are obtained.

Use existing temporary-repository replay patterns and relevant package checks. T1 covers fresh and custom/repeated variants, with fresh discovery evidence in both runtimes. Unavailable runtime validation is reported as unresolved acceptance, not inferred from file content or another runtime's success.

For T3 hold task, initial fixture, permissions, model/configuration and observation method constant within each baseline/candidate pair. Record unavoidable differences; a confounded or incomplete pair establishes neither an overhead pass nor savings. Measure text with a named tokenizer, document reads, tool/command invocations and created bookkeeping artifacts. Measure execution latency if a newly proposed mechanism introduces it.

Keep one compact evaluation summary: tested revision and dependency basis, platform/runtime and available model identity, supplied task, loaded guidance, before/after observations, overhead and fixture disposition. Separate actor behavior from evaluator assistance. Evaluator teardown removes the ambiguous artifact only after establishing fixture ownership; that assistance is not autonomous cleanup success.

Reuse identified prior evidence for unchanged housekeeping behavior, including recovery. If service/recovery behavior changes, rerun only the affected prior scenario with native resource observations. Do not start Docker merely to demonstrate documentation placement. Repeat checks only for changed inputs, failures, unresolved uncertainty, required independent review or relevant final integration.

Delivery requires T1-T3, relevant checks, resolved review findings, integrated implementation and verified task-owned fixture cleanup. Missing mandatory observations remain unresolved. Only the user may accept a recorded deviation with its exact criterion and consequence; material acceptance changes require a spec revision. Observed cases support this version, not a guarantee for all future agent runs.

## Out of Scope

- New hooks/helpers/cleanup skills, background reapers, periodic reviews/schedules, registries or a new evaluation platform.
- Broad documentation tooling, elaborate status metadata, orchestration repairs, CI preflight/run monitoring or inherited test repair.
- Personal/global configuration, installation redesign, cross-repository receipts or live adoption in other repositories.
- Historical migration, broad unignore, global/age-only cleanup, weakening ownership/security requirements or production feature work.
- Implementation, new implementation Issue publication, installation, branch creation or PR changes during this planning task.

Deferred work requires concrete evidence and separate authorization; it is not a hidden acceptance condition.

## Further Notes

### Dependency observation and implementation path

Read-only verification on 2026-10-28: [housekeeping PR #7](https://github.com/vincenzo345/skills/pull/7) remains OPEN and draft, with head b86774500cdcc5cca98de791573cd6106b6eeeb2 and no merge commit. GitHub main and local main are a3dc1bb8acda362a6d8078f36d83c2e517468407; the housekeeping head is not an ancestor of local main. The existing implementation is available on its review branch, not the current main basis. This snapshot is not authority to merge, integrate or activate it.

Resolve the accepted housekeeping basis through separate review/authorization; approve and publish the proposed breakdown; implement on an isolated feature branch; validate and review through a draft PR; obtain separate merge approval. Keep the globally linked checkout on main and preserve unrelated work.

The [proposed breakdown](issue-plan.md) is review material, not published implementation Issues. This specification is ready-for-agent as a definition of work; readiness does not bypass its dependency or grant implementation authorization.

### Illustrative folder outcomes

Names illustrate roles. Reuse suitable existing paths and create only needed content.

**Before completion**

```text
project/
  AGENTS.md                         # Loaded entry point to shared guidance
  CLAUDE.md                         # Existing or needed Claude entry point
  docs/
    README.md                       # Short current-knowledge index
    architecture/system.md
    codebase/cases-module.md
    data-model/cases.md              # Links to authoritative schema
    adr/0042-case-ownership.md
    agents/housekeeping.md           # Existing conditional policy and branches
  work/case-redesign/
    README.md
    design.md
    spec.md
    evidence/prototype-findings.md   # Conclusions and retained source reference
  tests/                            # Maintained checks and fixtures
  .scratch/agent-tmp/task-42/        # Owned disposable work
    prototype.html
    validate-once.py
    raw-result.json
    recovery.md                     # Only when interruption requires it
```

**After completion**

```text
project/
  AGENTS.md
  CLAUDE.md
  docs/                             # Current knowledge remains
  work/case-redesign/                # Stable plans, findings and history remain
  tests/                            # Maintained verification remains
  .scratch/agent-tmp/                # task-42 removed; root may be absent
```

A framework-dependent prototype may instead execute in an owned throwaway worktree. Its source reference survives; its execution environment retires. Intentional retained diagnostics remain explicit exceptions.

**Possible future existing-repository mapping**

```text
applications4life/
  app/
    docs/                           # Reuse current docs and index
    wayfinder/                      # Existing authoritative effort tracker
    backend/
    frontend/
  .local/agent-tmp/task-id/          # Reuse a suitable temporary subtree
  worktrees/active-task/             # Retire after accounting for unique work
  archive/                          # Protected retained material
```

This illustration authorizes no live migration or cleanup. Articles retains its content/source-ledger conventions; these engineering examples prescribe no coaching structure.

### Existing authority and evidence

- [Housekeeping effort](../agent-housekeeping/README.md), [spec](../agent-housekeeping/spec.md) and [validation](../agent-housekeeping/validation.md).
- [Stable workspaces](../../docs/adr/0001-stable-effort-workspaces.md), [setup dependency rule](../../.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md) and [installation authority](../../.agents/install-block.md).
- [Existing replay prior art](../wayfinder-reliability/validation.md).

Revision 5 synthesizes the confirmed recommendations, preserving the three objectives, testing seam and prior history. No child implementation Issues existed at publication, so no basis reconciliation was needed.

## Revision note

User-authorized rewrite: verified Codex/Claude instruction discovery, one shared guidance source, configured knowledge locations, precise conditional triggers, findings-before-cleanup integration and evidence-based hook deferral. Preserve the three objectives and confirmed seam; propose two implementation slices without approving or publishing Issues.
