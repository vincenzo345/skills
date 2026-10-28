---
schema: 1
kind: spec
id: work/agent-workflow-reliability/spec.md
effort: work/agent-workflow-reliability
revision: 3
state: current
readiness: ready-for-agent
---

# Durable knowledge, clean task completion, and lightweight ordinary work

## Problem Statement

Useful architecture, module and data-model decisions can be scattered among effort records and temporary files. Agents can leave one-off scripts, raw output and disposable environments behind, or remove planning material that should survive. Extra folders, instructions and reporting are not improvements if they make everyday work harder.

The requested outcome is simple: users can find what matters, completed work leaves no unexplained clutter, and ordinary tasks remain lightweight.

## Solution

Deliver exactly three objectives through existing skills:

1. **Give durable knowledge a clear home.** Setup reuses or establishes appropriate documentation locations and one short index. Approved plans and effort history keep stable paths.
2. **Define what survives task completion.** Retain maintained checks, requested deliverables, accepted decisions and useful prototype findings; remove owned disposable execution work through existing housekeeping.
3. **Prove these outcomes without routine burden.** Demonstrate one small design/prototype-to-cleanup example, preservation of existing layouts during setup, and zero added housekeeping actions for an ordinary edit.

Implement within skillsrepo's existing authority and validate through isolated repository fixtures. Live rollout into other repositories is a separate activity.

## User Stories

1. As a maintainer, I want setup to reuse suitable documentation locations, so that it does not create competing structures.
2. As a contributor, I want one short index to current knowledge, so that I can find the relevant document without loading everything.
3. As an architect, I want system responsibilities and runtime boundaries recorded, so that later changes respect the design.
4. As a developer, I want module interfaces, dependencies and invariants recorded, so that implementation choices are understandable.
5. As a data designer, I want identity, relationships, constraints and lifecycle decisions recorded, so that schema changes preserve their meaning.
6. As a reviewer, I want design rationale linked to its evidence, so that accepted intent is not mistaken for delivered behavior.
7. As a user, I want approved plans and effort records to retain stable paths, so that historical references and resumption still work.
8. As a planner, I want scratch notes distinguished from durable plans and unique reasoning, so that cleanup does not erase needed context.
9. As a designer, I want prototype findings preserved before its environment is retired, so that the experiment's answer survives.
10. As a developer, I want maintained tests and reusable fixtures retained, so that verification remains useful.
11. As a maintainer, I want one-off scripts and raw outputs removed when no longer needed, so that completed work leaves no unexplained clutter.
12. As a collaborator, I want ownership and active use respected during cleanup, so that shared resources and other agents remain safe.
13. As a user, I want retained diagnostics to have a purpose and revisit condition, so that exceptions can be understood and reconciled.
14. As a user, I want ordinary edits to add no housekeeping actions or bookkeeping, so that reliability stays lightweight.
15. As a reviewer, I want observed outcomes and overhead measurements, so that completion and efficiency claims are credible.

## Implementation Decisions

### Objective 1: a clear home for durable knowledge

- Extend the existing setup discovery and reviewed configuration flow. Reuse suitable documentation, domain, decision, tracker and temporary locations before proposing new ones. Create only collections that actually contain useful material.
- Provide one short current-knowledge index and conditional pointers from the repository's existing loaded instruction surface. Keep detailed guidance out of ordinary task context.
- Organize by responsibility:

| Knowledge | What belongs there |
| --- | --- |
| Architecture | System responsibilities, runtime boundaries, interactions, ownership and important constraints |
| Codebase design | Module interfaces, dependencies, invariants and testing seams |
| Data model | Identity, relationships, integrity, lifecycle/history and links to implemented schema |
| Decisions | Consequential choices, rationale, alternatives and supersession |

- Existing domain records own business meaning; schemas and migrations own implemented physical structure. Documentation explains intent and constraints rather than becoming a second schema or glossary.
- Reuse the current effort record for proposals, findings and approved plans. When a decision becomes current project knowledge, update the relevant maintained document and link back to its effort evidence. Avoid competing current copies.
- Make the distinction between proposed intent, accepted choices and actual implementation clear in concise prose when it matters. Do not introduce a mandatory status schema or elaborate metadata.
- Preserve stable effort paths and historical evidence. Completed efforts leave the active queue rather than being relocated for cosmetic consistency.
- Keep editable diagrams beside their document. Reusable synthetic data stays with maintained fixtures; operational dumps and temporary databases are not design documentation.
- Repeated setup preserves user choices, custom paths, content, authority and narrow ignore rules without duplicate policy blocks. As part of setup verification, confirm published references resolve and intended permanent documents are visible to Git.
- An ignore conflict is a diagnostic. Any targeted correction belongs in the existing reviewed setup change, preserves unrelated protected/generated content, and does not authorize wholesale unignore or historical migration.

### Objective 2: an explicit survival rule

| Retain | Remove when no longer needed |
| --- | --- |
| Maintained project documentation and decisions | Disposable alternate drafts and scratch notes with no remaining unique value |
| Approved plans, specifications, approvals and durable effort history | One-off validators and raw generated outputs |
| Maintained regression tests and reusable fixtures | Disposable prototype execution files and owned temporary environments |
| Requested deliverables and useful prototype conclusions | Resolved temporary bookkeeping and recovery state |

Classify purpose before creation through existing task planning, not a new form. Age, extension, ignored status or the word plan does not establish disposability. A useful unaccepted proposal may still contain reasoning worth retaining.

Capture a prototype's question, findings, limitations and necessary source/reproducibility reference before retiring its environment. Follow existing prototype placement rules: representative framework-dependent experiments may require an owned throwaway worktree rather than an isolated scratch file.

Reuse the existing housekeeping policy for task ownership, native teardown, retention, exact identities, partial acquisition, path boundaries, shared resources and interruption recovery. Do not duplicate those rules across skills or introduce another cleanup mechanism.

At completion or failure, remove owned disposable work that is no longer needed. Preserve maintained checks, durable records, requested deliverables, other active work and shared resources. Retained diagnostics or review environments have a purpose and revisit condition in existing context or the existing recovery note when required.

Retire worktrees through the existing Git ownership/integration workflow after accounting for unique work. Report inaccessible, ambiguous or blocked cleanup accurately; neither a clean Git status nor an agent's assertion proves resource absence.

### Objective 3: lightweight behavior with observable proof

Mandatory routine-work constraints:

- An ordinary edit with no relevant documentation or disposable work adds zero housekeeping calls, specialized-reference reads, recovery notes, mandatory reports or other bookkeeping.
- Load only guidance triggered by the task. Do not load this specification, the retrospective or historical research as ordinary context.
- Reuse existing configuration, task state and evidence; keep one authority for each current fact. Avoid unchanged rediscovery or rereading.
- Repeat validation only for a changed input, failure, unresolved question, required independent review or relevant final integration check.
- Every retained artifact serves a reader, reusable purpose, history obligation or necessary evidence.

Measure generated persistent text and cumulative triggered references with a named tokenizer, plus reads, tool/command invocations and created bookkeeping artifacts. Compare equivalent ordinary edits under the same recorded harness conditions. Report increases honestly; there is no new numeric token ceiling and no claimed saving from an incomplete comparison.

### Delivery boundary and dependency

skillsrepo is the sole implementation and integration authority. Use its existing tracker, claims, review and receipts; no cross-repository completion protocol is needed.

Build on the existing agent-housekeeping implementation rather than recreate it. Before dependent work starts, identify the integrated housekeeping basis or record its absence as a blocker. This specification does not authorize merging its existing draft PR or activating development worktrees globally.

Update only the setup, design, prototype and existing housekeeping integration points needed for these objectives, with relevant human documentation, catalogs and router guidance. Preserve invocation, installation, domain, security and compliance boundaries. Run existing relevant checks; broader documentation-check tooling is deferred.

## Testing Decisions

### Confirmed seam

Reuse the user's confirmed end-to-end seam: setup generates guidance, an agent uses it to design/prototype and complete work, and the evaluator inspects durable artifacts, cleanup and overhead. This revision selects a smaller subset of that seam; no new seam is introduced.

Prefer existing temporary-repository replay, package checks and housekeeping evidence. Observe external behavior, not whether instructions contain preferred wording.

### Three acceptance cases

| Case | Required outcome |
| --- | --- |
| T1: Setup and existing-layout preservation | A fresh fixture receives a usable knowledge index and temporary convention. Repeating setup in a custom-layout fixture preserves existing content, user choices, tracker authority and one policy source. Published links resolve and intended permanent documents are visible to Git |
| T2: One design/prototype-to-cleanup example | One small, coherent question produces appropriately placed architecture/module/data-model reasoning where relevant, accepted conclusions linked to evidence, and retained effort history. A maintained check/fixture and requested deliverable survive. Owned one-off files, raw output and disposable environment are removed; a retained diagnostic is justified and reconciled once its revisit condition is met. Another task's sentinel remains unchanged |
| T3: Ordinary-edit overhead | A matched baseline/candidate ordinary edit completes with zero additional housekeeping calls, specialized reads, notes or mandatory reports. Record loaded-context and execution differences separately |

Use one bounded example for T2, not a new application or three independent design projects. A small case-record lifecycle can expose system responsibility, module interface and data identity naturally. The supplied task must ask the real design question, not tell the actor which files to create or what outcome to claim.

Run one observed candidate case for each changed behavior; T1 includes fresh and custom/repeated variants. Use fresh context when testing whether setup output is discoverable. Reuse applicable prior evidence for unchanged behavior, identifying its basis. Repeat only cases affected by changes, failures or unresolved uncertainty.

Use native observations for any process or service cleanup actually claimed. Do not start Docker or build extra infrastructure merely to demonstrate documentation placement. If this implementation changes existing service/recovery behavior, rerun the affected prior housekeeping scenario rather than expanding the whole test program.

Keep one compact evaluation summary: tested revision, harness/platform and available model identity, supplied task, loaded guidance, before/after observations, overhead and fixture disposition. Separate evaluator assistance from autonomous actor behavior. Run existing relevant package and repository checks. Prose checks alone do not establish agent behavior.

Delivery requires T1-T3, relevant checks, resolved review findings, integrated implementation and verified task-owned fixture cleanup. Missing mandatory observations remain unresolved. Only the user may accept a deviation from mandatory acceptance, recording the exact criterion and consequence; agents can report exceptions but cannot approve them. Material acceptance changes require specification revision.

These observations support the delivered version; they do not guarantee every future model run.

## Out of Scope

- Periodic cleanup reviews, schedules, background reapers, new helpers/hooks/cleanup skills or registries.
- Broader documentation linting, link-check platforms, general retired-skill discovery, or elaborate status metadata.
- Autonomous continuation/orchestration repairs, CI preflight/run-observability work, installation redesign or cross-repository receipt mechanisms.
- Live rollout into Applications4Life, Articles, coaching or other repositories; fixture demonstrations are not adoption claims.
- Automatic migration of historical records, broad unignore, global cleanup, age-only deletion, or weakening security/ownership requirements.
- Production feature work, comprehensive inherited test repair or a new evaluation platform.
- Creating implementation Issues, modifying skills/code, installing changes, merging PRs or scheduling work during specification publication.

These deferred items may become separate efforts if the three objectives expose a concrete gap. They are not hidden conditions for closing this effort.

## Further Notes

### Existing decisions and evidence

- [Housekeeping effort](../agent-housekeeping/README.md), [specification](../agent-housekeeping/spec.md), [behavioral evidence](../agent-housekeeping/validation.md), and [existing PR #7](https://github.com/vincenzo345/skills/pull/7).
- [Stable effort workspace decision](../../docs/adr/0001-stable-effort-workspaces.md), [setup dependency decision](../../.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md), and [installation authority](../../.agents/install-block.md).
- [Wayfinder reliability validation](../wayfinder-reliability/validation.md) supplies existing handoff/repository-fixture prior art.

The concrete folder examples below remain illustrative. Create only needed artifacts and preserve existing conventions. They do not prescribe implementation source paths or authorize live migration.

### Illustrative folder outcomes

These concrete examples illustrate the accepted role/lifetime rules. Names are examples, not a mandate to relocate existing records or precreate empty folders. Unrelated source, assets, dependencies and repository configuration are omitted. Setup maps roles to existing suitable locations first.

**Example 1: a repository while a design effort is active**

```text
project/
  AGENTS.md                         # Short entry point and conditional pointers
  docs/
    README.md                       # Current documentation index
    architecture/
      system-overview.md            # Responsibilities, boundaries, runtime
      case-processing.md            # Current behavior and accepted target labeled
      case-processing.mmd           # Editable diagram source
    codebase/
      cases-module.md               # Public interfaces, invariants, test seams
    data-model/
      case-model.md                 # Identity, relationships, constraints, lifecycle
      case-model.mmd                # ERD source; links to authoritative schema
    adr/
      0042-case-ownership.md         # Decision, rationale, supersession links
    operations/
      local-verification.md         # Maintained execution/recovery procedure
    agents/
      housekeeping.md               # Conditional policy, not repeated in AGENTS
      housekeeping-services.md
      housekeeping-recovery.md
  work/
    queue.md                        # Active efforts only
    case-redesign/
      README.md                     # Outcome, state, authority, current pointers
      discovery.md                  # Findings and unresolved questions
      design.md                     # Proposal and evaluated alternatives
      spec.md                       # Approved implementation requirements
      tickets/
        01-case-boundary.md
      research/
        ownership-options.md        # Sources and reasoning worth retaining
      evidence/
        prototype-findings.md       # Answer, limitations, source commit/link
        validation.md               # Necessary acceptance evidence
      history/
        spec-r1.md                  # Only if an actual revision was superseded
  tests/
    fixtures/
      sample-case.json              # Maintained synthetic fixture
    test_case_lifecycle.py           # Maintained regression coverage
  .scratch/
    agent-tmp/                      # Narrowly ignored disposable subtree
      case-redesign-run-42/
        planning-notes.md            # Disposable working notes, not approved plan
        prototype.html              # Isolated runnable experiment, when suitable
        validate-once.py             # One-off validator
        raw-result.json             # Disposable output
        recovery.md                 # Only if work/resources may survive interruption
```

The chosen filenames do not change domain authority: retain the repository's existing glossary, schema definitions and migration locations. A framework-dependent prototype may instead live beside its real module in an owned throwaway worktree under the existing prototype rules. Do not force runnable code into scratch when that prevents a representative experiment.

**Example 2: the same repository after the effort finishes**

```text
project/
  docs/                             # Updated current knowledge and decisions remain
  work/
    queue.md                        # Completed effort removed from this list
    case-redesign/                  # Same path; completed state and evidence remain
      README.md
      discovery.md
      design.md
      spec.md
      tickets/
      research/
      evidence/
      history/                      # Present only when history was needed
  tests/                            # Maintained tests and fixtures remain
  .scratch/
    agent-tmp/                      # Root may remain empty or be absent
                                    # case-redesign-run-42 has been removed
```

The temporary script, raw output and resolved recovery note are gone. Useful findings and the required prototype source reference survive in durable evidence. Owned temporary services and disposable worktrees are also retired. A retained diagnostic or review environment is an explicit exception with an owner, purpose and revisit condition, not a claim of complete cleanup.

**Example 3: possible future Applications4Life adoption, outside this delivery**

```text
applications4life/
  app/                              # Existing current application checkout
    docs/
      README.md
      architecture/                 # Keep existing architecture records
      codebase/                     # Add only when a maintained module doc is needed
      data-model/                   # Add only when a maintained model doc is needed
      adr/                          # Keep existing decision identities
      operations/
      agents/
    wayfinder/                      # Preserve the existing authoritative tracker
      repository-structure-cleanup/ # Existing effort stays at its established path
    backend/                        # Existing code, schema, migrations and tests
    frontend/                       # Existing code and tests
  .local/
    agent-tmp/                      # Illustrative dedicated subtree within .local
      task-id/                      # Disposable notes, probes and conditional recovery
  worktrees/
    active-task/                    # Only while needed; retire through Git lifecycle
  archive/                          # Existing retained material; outside temp cleanup
```

This is a role mapping, not a declaration that these are the only permitted existing folders or that all current folders should be deleted. Reuse a suitable temporary subtree already present instead of adding a duplicate. Review existing workspace ownership and preservation obligations before any later cleanup. No new parallel work tracker is added to Applications4Life. Articles likewise keeps its established content and source-ledger locations; these engineering examples do not prescribe a coaching folder structure.

This existing-repository example is a future adoption illustration. Revision 3 validates representative isolated fixtures; it does not move or modify this live workspace.

### Authority and handoff

The user explicitly requested revision around the three recommended objectives: a clear home for durable knowledge, explicit survival rules at task completion, and proof without routine burden. Revision 3 materially narrows revision 2, retaining the previously confirmed testing seam and folder examples. Periodic review, broader check tooling and elaborate metadata are deferred rather than optional implementation work inside this effort.

No implementation Issues were published at revision time, so no child bases required reconciliation. Prior revisions remain historical evidence. Publication marks this specification ready-for-agent; implementation breakdown approval and implementation authorization remain separate.

## Revision note

User-approved reduction to three objectives: give durable knowledge a clear home, define what survives completion, and demonstrate outcomes without routine burden. Replace five regression groups with three acceptance cases; defer periodic review, broader documentation-check tooling and elaborate metadata. Preserve existing housekeeping dependency, safety rules, folder examples and user-only acceptance of mandatory exceptions.
