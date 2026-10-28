---
schema: 1
kind: spec
id: work/agent-workflow-reliability/spec.md
effort: work/agent-workflow-reliability
revision: 2
state: current
readiness: ready-for-agent
---

# Durable project knowledge and disposable agent work

## Problem Statement

Agents leave useful design knowledge scattered across effort records and temporary files, while approved plans, prototype findings, generated output, and disposable scripts lack clear lifetimes. A folder convention alone does not prevent duplicate current documents, accidental loss of decisions, hidden new Markdown files, or unnecessary cleanup ceremony.

Revision 1 combined this problem with broader continuation, CI execution, installation, and cross-repository rollout changes. Those are worthwhile but independently substantial. This revision confines delivery to the documentation and artifact-lifecycle contract, implemented in skillsrepo and demonstrated in isolated repository fixtures.

The user wants dependable, observable outcomes without burdening routine work. No instruction set guarantees arbitrary model behavior. Delivery therefore requires explicit acceptance observations, existing deterministic checks where appropriate, and honest handling of unresolved results.

## Solution

Extend existing setup, design, prototype, and housekeeping workflows to distinguish maintained project knowledge, durable effort history, and disposable execution work. Discover and reuse repository conventions; expose one compact navigation entry point; preserve decisions and maintained verification; retire owned temporary work when its purpose ends.

Implement and integrate this behavior within skillsrepo's existing Git/tracker authority. Use representative fresh and existing repository fixtures to demonstrate the resulting folder structures and behavior. Live adoption into Applications4Life, Articles, or other repositories is separate work, not a condition this implementation can silently claim to have satisfied.

## User Stories

1. As a maintainer, I want setup to reuse suitable documentation and temporary locations, so that it does not create competing folder structures.
2. As a contributor, I want a short current documentation index, so that I can find the relevant knowledge without loading everything.
3. As an architect, I want system boundaries, responsibilities, and runtime constraints recorded, so that later changes respect the design.
4. As a developer, I want module interfaces, dependencies, and invariants documented, so that implementation choices are understandable.
5. As a data designer, I want identity, relationships, constraints, and lifecycle decisions recorded, so that schema changes preserve their meaning.
6. As a developer, I want schemas and migrations to remain authoritative for physical implementation, so that diagrams do not become competing schemas.
7. As a reviewer, I want decision approval distinguished from implementation progress, so that accepted designs are not mistaken for delivered behavior.
8. As a maintainer, I want consequential decisions and supersession links preserved, so that later contributors can understand the rationale.
9. As a user, I want approved effort records to keep stable identities and paths, so that I can resume work and follow historical references.
10. As a planner, I want disposable working notes distinguished from approved plans and unique reasoning, so that cleanup does not erase needed context.
11. As a designer, I want prototype findings captured before retiring the environment, so that the experiment's answer survives.
12. As a developer, I want maintained regression tests and reusable synthetic fixtures retained, so that verification remains useful.
13. As a maintainer, I want output classified independently from its checker, so that a permanent test does not justify permanent raw output.
14. As a collaborator, I want cleanup to respect ownership, active use, and retention, so that shared resources and other agents remain safe.
15. As a returning contributor, I want existing housekeeping recovery to preserve interrupted work, so that this change does not weaken established safeguards.
16. As a maintainer, I want an explicitly invoked periodic review of bounded temporary locations, so that forgotten exceptions can be reconciled safely.
17. As a contributor, I want new permanent documents visible to Git and linked from current navigation, so that they do not silently disappear.
18. As a reviewer, I want invalid navigation and ignored intended documents caught by existing checks, so that agents do not rely on prose alone.
19. As a user, I want ordinary edits to add no new workflow actions, so that organization does not become another task.
20. As a user, I want context, reads, commands, and bookkeeping measured separately, so that efficiency claims reflect actual work.
21. As a maintainer, I want one authority for each current fact and state, so that duplicated policy does not drift.
22. As a non-code user, I want engineering folder conventions applied only when relevant, so that advice and editorial work remain lightweight.
23. As a user, I want deviations from mandatory acceptance brought to me, so that an agent cannot approve its own incomplete delivery.
24. As a maintainer, I want changes to compose from existing skills and checks, so that the solution does not introduce another framework.

## Implementation Decisions

### Scope and delivery authority

- Implement only reusable documentation placement, design promotion, artifact lifetime, task-end cleanup integration, explicitly invoked periodic review guidance, and focused documentation checks.
- skillsrepo remains the sole implementation and integration authority for this effort. Its existing coordinator, claim protocol, review flow, and integration receipts apply unchanged. Cross-repository receipt mechanisms are not introduced.
- Use isolated fixtures representative of a fresh repository, an existing custom documentation/tracker layout, and a non-code workflow. Applications4Life's and Articles' existing conventions inform these cases; their live repositories are not modified.
- Build on the completed agent-housekeeping effort's baseline, native lifecycle guidance, and conditional service/recovery references. Reuse its implementation through the authorized integration workflow rather than recreate it. The existing draft PR restriction remains in force: this specification does not authorize its merge or global activation.
- If the required housekeeping basis is not available on the selected integration branch, expose that dependency before implementation. Do not report delivery of dependent behavior from an unintegrated draft.
- Preserve existing domain, tracker, installation, invocation, security, and compliance authority. Resynchronize affected skill docs, catalogs and router entries as part of each delivered behavior.

### Three artifact lifetimes

| Lifetime | Contents and authority | Completion behavior |
| --- | --- | --- |
| Maintained project knowledge | Current architecture, module and data-model descriptions, decisions, operations guidance, maintained tests and reusable fixtures | Update affected knowledge and retain version history |
| Durable effort history | Outcome, discovery, accepted designs/plans, specification revisions, approvals, Issues, conclusions and necessary evidence | Preserve stable paths; completed efforts leave the active queue |
| Disposable execution work | Scratch planning notes, alternate drafts with no unique remaining value, prototype execution files, one-off scripts, raw outputs and temporary resources | Remove when no longer needed, after ownership and retention checks |

Classify purpose before creation using existing task planning, not a new form. An approved plan is durable. An unaccepted draft with unique reasoning may also need retention. File age, extension, ignored status, or the word plan never independently establishes disposability.

Create only artifacts actually needed. Do not scaffold empty collections, require a separate report for every task, or maintain a second inventory of all documents.

### Setup and navigation

- Extend existing setup discovery and reviewed configuration. Find the authoritative instruction surface, documentation index, tracker, domain/decision records, temporary convention and relevant existing checks.
- Map document and execution roles to existing suitable locations. For fresh repositories, use conventional architecture, codebase, data-model, decision and operations collections only as needed. Keep established glossary, schema, migration and tracker locations.
- Keep one short index and conditional navigation pointers. Detailed placement and promotion guidance loads only for documentation, design, prototype or cleanup work. An ordinary edit need not inspect the documentation tree.
- Ensure the chosen instruction surface is actually loaded and generated references resolve, including custom paths. Prefer repository configuration to a package fallback.
- Repeated setup preserves user edits, legacy content, authority and existing valid choices, with no duplicate policy blocks or conflicting mappings.
- Establish temporary storage through the existing housekeeping flow only when absent. Reuse the established fallback for unconfigured work. Setup remains a soft dependency for ordinary tasks.
- During setup or a relevant documentation change, verify that representative intended permanent documents are visible to Git. A blanket Markdown exclusion is a diagnostic, not permission to reveal all ignored content.
- Before proposing ignore-rule narrowing, inspect relevant path classifications without reading protected content. Include a targeted correction in the existing reviewed configuration change. Preserve secret and generated-output protection. Live historical unignore/migration work remains outside this effort.

### Design knowledge and promotion

| Collection | Responsibility |
| --- | --- |
| Architecture | System responsibilities, runtime/deployment boundaries, interactions, ownership, constraints and failure behavior |
| Codebase | Module interfaces, dependencies, invariants, representative usage and testing seams |
| Data model | Logical identity, relationships, integrity, lifecycle/history and mapping to physical schema authority |
| Decision records | Consequential choices, rationale, alternatives and supersession |
| Operations | Maintained procedures for running, observing and recovering the implemented system |

The existing glossary/domain records own business meaning; schemas and migrations own implemented physical structure. Explain intent and constraints and link to those authorities rather than copy entire schemas or introduce another ontology store.

Decision status and implementation status answer different questions:

- Decision status: proposed, accepted or superseded.
- Implementation status, when relevant: not implemented, partially implemented or implemented, with evidence or a source revision.

Use these distinctions where ambiguity would matter, including individual sections of mixed-status documents. A brief status line or prose is sufficient; a new mandatory metadata schema for every document is not required. Acceptance does not imply implementation, and implementation progress does not rewrite decision history.

Keep effort proposals and evaluations in their durable effort record. On adoption, update the affected current project document and link back to rationale and evidence. Preserve historical designs as history without maintaining a second competing current description. A new request can reopen a decision, but routine editing must not silently reverse one.

Keep editable diagram sources beside the owning document. Retain generated renders when they serve a reader and identify their source. Reusable synthetic data stays with maintained test fixtures; sensitive or operational dumps remain outside design documentation.

A framework-dependent prototype may need an owned throwaway worktree and application-native placement. Capture its question, findings, limitations and required reproducibility/source reference before retiring its environment. Do not move prototypes into scratch when that makes the experiment unrepresentative.

### Task-end cleanup and explicitly invoked review

- Reuse existing housekeeping ownership, native teardown, partial-acquisition, path-boundary, retention and recovery behavior. Do not copy detailed file/process/Docker rules into every skill.
- At task completion or failure, remove owned disposable work that is no longer needed. Preserve maintained tests, approved plans, unique decision evidence, requested deliverables, active tasks and shared resources.
- Retained diagnostics or review environments have an owner, purpose and revisit condition in existing context or the single recovery note where needed. Reconcile them when the condition is met. Do not create a per-command ledger.
- Worktree retirement follows existing Git ownership/integration requirements and accounts for unique commits, tracked changes, untracked work and relevant ignored assets. A clean status alone is insufficient evidence of complete resource cleanup.
- Version one provides task-end cleanup and an explicitly requested periodic review through existing workflows and conditional guidance. Weekly review is a suggested cadence, not a guarantee that review occurs.
- The periodic review examines only configured temporary locations and registered worktrees. Age prioritizes inspection; ownership, inactivity, current use and retention determine disposition.
- Preserve and report active, ambiguous, inaccessible or intentionally retained resources. Historical effort records and maintained documentation are outside disposable cleanup.
- Do not add a scheduled task, daemon, cleanup skill, hook, acquisition helper or registry. A gap requiring new infrastructure must have a failing case and a separately approved targeted proposal.

### Focused deterministic checks

- Inspect existing package, structure, link and Git-visibility checks first. Extend the smallest suitable existing check rather than create another governance system.
- Validate changed/current navigation and published references at the configured documentation boundary, including custom locations. Report broken links with the owning document and unresolved target.
- Detect when a representative intended permanent document is ignored. Verify targeted corrections preserve unrelated generated/secret exclusions and existing tracked history.
- Scope checks to current configured navigation and changed documentation; avoid scanning every historical file or treating arbitrary skill names in quoted prose as invocations.
- Wire the relevant checks into the existing repository validation entry point and CI contribution path. Reuse any applicable housekeeping PR wiring instead of duplicating it.
- Mechanical failures are deterministic diagnostics. Judgment about design quality, rationale, scope and appropriate retention remains review work. No test should merely confirm that policy contains preferred wording.

### Context and execution constraints

Mandatory outcomes:

1. An ordinary edit with no relevant documentation or disposable work adds zero inventory calls, specialized-reference reads, recovery notes, mandatory reports or other workflow actions.
2. Load only the guidance triggered by the actual task. This specification, the retrospective and historical research are not routine context.
3. Keep one authority for each current fact or state. Reuse tracker records and housekeeping recovery instead of creating competing documents.
4. Do not rediscover unchanged configuration, reload unchanged guidance, or rerun unchanged validation without a changed input, failure, unresolved question or explicit task need.
5. Every retained artifact has an identified reader, reusable purpose, approval/history obligation or necessary evidentiary role.
6. Required correctness, ownership and security controls cannot be removed to reduce tokens.

Measure generated persistent guidance, triggered reference content, reads, executable/tool calls and bookkeeping artifacts separately. Use a named tokenizer and character counts, with a matched ordinary-task baseline. Report cumulative loaded guidance for the tested path rather than only the size of the entry pointer.

The earlier 150-250 combined-token aspiration and the revision-1 figures of 75 additional persistent tokens and 800 tokens per conditional reference are provisional comparison points, not acceptance thresholds. Establish measurements before treating any number as a budget. Do not introduce a hard two-navigation-step limit.

A material measured increase requires a concrete explanation and a simplification pass during review. Token savings must not be claimed from incomplete, differently authorized or otherwise incomparable tasks. The zero-added-action ordinary-task condition remains mandatory.

## Testing Decisions

### Existing confirmed seam

Retain the user's already confirmed end-to-end seam: setup produces repository guidance, an agent uses it during planning/design and task completion or resumption, and the evaluator observes artifacts, history, cleanup and overhead. This revision narrows the behaviors exercised at that same seam; it adds no new seam or confirmation requirement.

Use existing temporary-repository behavioral replay, work-record, package/installer and housekeeping prior art. Deterministic check fixtures support this seam. Assertions inspect resulting behavior and resource state rather than implementation text.

### Compact mandatory regression set

| Case | Required observations |
| --- | --- |
| R1: Setup and preservation | Fresh setup supplies a usable role mapping and temporary convention. Repeated setup of an existing custom layout preserves content, authority, ignore boundaries and one policy source; intended durable documents are visible and references resolve |
| R2: Design to durable knowledge | A bounded design/prototype task puts architecture, module and data-model information under their correct authorities, distinguishes approval from implementation, captures findings, and promotes current knowledge without erasing effort history or leaving competing current copies |
| R3: Task completion and retention | A maintained check/fixture and requested deliverable survive; owned one-off script/output and resolved bookkeeping are removed. Unresolved useful diagnostics remain with purpose/revisit condition and disappear after reconciliation |
| R4: Explicit periodic review | A requested review remains within configured temporary locations/worktrees, preserves active/shared/ambiguous state and durable plans, and removes only proven eligible owned work. An unrelated task performs no periodic review |
| R5: Ordinary-task overhead | A matched ordinary edit adds zero workflow actions, specialized reads or bookkeeping. A lightweight non-code case creates no engineering folders or processes. Record context and execution costs for the changed paths |

Supporting negative/positive fixtures demonstrate that the existing checks reject a broken configured reference and an ignored intended document, then admit the corrected custom-path configuration while preserving unrelated exclusions.

Run one observed candidate case per changed behavior, using a fresh session where discoverability or resumption is under examination. Do not supply the expected answer or lost resource identities in the actor prompt. R1 requires both fresh and custom/repeated variants; these can reuse one bounded fixture sequence.

There is no blanket requirement for three repeated actor runs or a new baseline for every scenario. Reuse prior evidence only when its source revision, conditions and behavior remain applicable. Repeat a case when it fails, materially changes, or leaves relevant uncertainty; rerun the full set only when a cross-cutting change invalidates it.

Unchanged process/Docker lifecycle behavior may reuse the incorporated housekeeping evidence. If an integration change alters service acquisition, cleanup, ownership or recovery, rerun the affected existing scenario with actual native resource observations. Do not create services merely to validate documentation placement.

### Evidence and completion

Keep one bounded effort validation summary with source revision, platform/harness and available model identity, supplied prompts, generated configuration, loaded guidance, observed outcomes, overhead measurements and fixture disposition. Separate agent behavior from evaluator assistance and deterministic results. Raw transcripts and per-command evidence files are not required.

Delivery requires R1-R5, the focused negative/positive check fixtures, relevant existing repository checks, review findings resolved, integrated work on the designated skillsrepo branch, and scoped fixture cleanup. Report fixture demonstrations as demonstrations, not live adoption.

An unavailable required observation or failed mandatory outcome remains unresolved. Only the user can accept a deviation from mandatory acceptance, with the exact criterion, consequence and disposition recorded. An implementing or reviewing agent may disclose an exception but cannot approve it. A material change to scope or acceptance requires specification revision and applicable Issue reconciliation.

Bounded successful runs establish evidence for the delivered version, not a universal guarantee of model behavior. Do not close the effort because work is lengthy or context is low, and do not claim cleanup succeeded when it was blocked.

## Out of Scope

- Broader autonomous continuation/orchestration fixes, new claim/receipt mechanisms, background execution systems and cross-repository completion protocols.
- CI preflight, long-running runner observability, performance isolation and comprehensive release-test repair. Existing validation wiring needed for the focused documentation checks remains in scope.
- Global installation redesign, general retired-skill discovery, or live rollout into Applications4Life, Articles, coaching or other repositories.
- Production feature work, building a writing application, repairing inherited application architecture or weakening security/compliance controls.
- Automatic migration/renaming of durable records, bulk historical cleanup, blanket unignore without inventory, age-only deletion, or deletion of shared/personal/global resources.
- Scheduled cleanup, new helpers/hooks/skills/registries/evaluation platforms without a separately approved demonstrated need.
- Implementation Issues, code changes, installations, repository adoption, merges or scheduling during specification publication.

## Further Notes

### Deferred work and rationale

| Separate future effort | Why deferred |
| --- | --- |
| Continuation and orchestration reliability | Requires its own outcome, interruption/ownership scenarios and authority boundaries; it is independent of document placement |
| CI preflight and execution observability | Changes application runners and environment contracts, with different tests and operational risks |
| Live repository adoption | Requires approved scope and revision-specific receipts in each repository's own authority; a skillsrepo integration receipt cannot certify another Git repository |
| Installation/reference cleanup beyond this boundary | Has its own discovery and compatibility concerns; it should not expand the focused documentation checks |

These are recorded future directions, not published or approved implementation Issues. The original Applications4Life cleanup effort receives no new conditions from this specification.

### Existing evidence and decisions

The October 20-27 retrospective screened 564 local Codex session files across four project areas; workers, replays and inherited histories are not independent conversations. Its observations motivate this effort but must not become mandatory routine context.

- [Housekeeping effort](../agent-housekeeping/README.md), [specification](../agent-housekeeping/spec.md), [behavioral evidence](../agent-housekeeping/validation.md), and [draft PR #7](https://github.com/vincenzo345/skills/pull/7).
- [Wayfinder reliability retrospective](../wayfinder-reliability/retrospective.md) and [validation](../wayfinder-reliability/validation.md).
- [Stable effort workspace decision](../../docs/adr/0001-stable-effort-workspaces.md), [setup dependency decision](../../.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md), and [installation authority](../../.agents/install-block.md).
- [Earlier hygiene handoff](../../docs/plans/hygene-recommendations.md).

The folder examples below are retained at the user's explicit request. They illustrate outcomes rather than prescribe implementation source paths or authorize live migration.

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

This existing-repository example is a future adoption illustration. Revision 2 validates representative isolated fixtures; it does not move or modify this live workspace.

### Authority and handoff

The user requested the revisions proposed in the honest assessment: narrow this effort to durable knowledge and disposable work, separate other improvements, reduce evaluation overhead, treat numerical targets as provisional, and reserve mandatory exceptions for user acceptance. This is a material scope and acceptance change, published as revision 2 with revision 1 retained verbatim in history.

The previously confirmed end-to-end seam is unchanged; this revision narrows its scenario set. No additional seam or interview is required. There were no published implementation Issues at revision time, so no child bases require reconciliation. Publication marks the revised specification ready-for-agent; breakdown approval and implementation authorization remain separate.

## Revision note

User-authorized material revision: narrow delivery to durable documentation and disposable work in skillsrepo; defer orchestration, CI-runner changes, installation redesign and live multi-repository adoption; retain folder examples; replace broad evaluation with five scenario groups and focused supporting checks; make numerical targets provisional, distinguish decision/implementation status, and require user acceptance of mandatory deviations.
