---
schema: 1
kind: spec
id: work/agent-workflow-reliability/spec.md
effort: work/agent-workflow-reliability
revision: 1
state: current
readiness: ready-for-agent
---

# Reliable agent workflows and durable project knowledge

## Problem Statement

Across the October 20-27 retrospective, authorized work stopped at intermediate milestones, planning drifted into unrelated prerequisites, and users had to rediscover where work was saved. Repeated validation encountered environment and fixture failures late, while status sometimes described a running test without observing its current execution. Multiple checkouts, installed skill variants, and stale references obscured authority.

Architecture and design knowledge is valuable beyond an individual effort, but its location, adoption status, and relationship to implementation are inconsistent. Disposable planning drafts, prototypes, generated output, and service resources accumulate beside durable records. A blanket Markdown ignore rule can hide new permanent documents. Adding more persistent instructions, trackers, reports, agents, or cleanup infrastructure would increase the burden instead of reliably resolving these problems.

The user wants dependable outcomes with minimal routine context and execution overhead. A specification cannot guarantee arbitrary model behavior, tool availability, or unattended cleanup while no agent runs. It can define verifiable delivery conditions, deterministic protections where available, bounded behavioral evidence, and explicit unresolved outcomes. Neither reassuring prose nor a passing demonstration alone constitutes a universal guarantee.

## Solution

Extend the existing setup, planning, design, implementation, review, and housekeeping workflows around three artifact lifetimes: maintained project knowledge, durable effort history, and disposable execution work. Reuse the current tracker, native resource lifecycle mechanisms, installation authority, CI runners, and repository checks.

Give each repository one discoverable mapping of these roles to its existing locations. Keep persistent instructions short. Load detailed guidance only for the relevant action. Maintain a visible requested outcome and resume point without creating another tracker. Verify final results against the current integrated revision; report blocked, unknown, and unavailable observations accurately.

Deliver the reusable behavior in skillsrepo and validate targeted adoption in Applications4Life and the Articles planning workflow. Use a lightweight non-code scenario to establish that engineering scaffolding does not spill into coaching or ordinary advice. Adoption into a live repository requires its approved implementation scope; publication of this specification performs no adoption or implementation.

## User Stories

1. As a maintainer, I want setup to discover existing conventions, so that it preserves valid locations instead of creating competing folders.
2. As a contributor, I want one short documentation index, so that I can find relevant current knowledge without loading every document.
3. As an architect, I want system responsibilities and runtime boundaries maintained together, so that later work respects the agreed structure.
4. As a developer, I want module interfaces and invariants documented separately from deployment topology, so that implementation decisions are understandable.
5. As a data designer, I want identity, relationships, constraints, and lifecycle decisions recorded, so that schema changes preserve their meaning.
6. As a developer, I want implemented schema definitions and migrations to remain authoritative, so that diagrams do not become competing schemas.
7. As a reviewer, I want proposed, accepted-target, implemented, and superseded designs distinguished, so that acceptance is not mistaken for delivery.
8. As a maintainer, I want consequential decisions linked to their rationale and replacements, so that supersession preserves history.
9. As a user, I want approved effort records to retain stable paths, so that later sessions can resume them.
10. As a user, I want disposable planning drafts distinguished from approved plans, so that cleanup preserves decisions and commitments.
11. As a designer, I want prototype findings preserved before execution files are retired, so that cleanup does not erase the answer.
12. As a developer, I want maintained regression tests and repeatable checks retained, so that verification improves over time.
13. As a maintainer, I want generated output classified independently from its checker, so that a permanent test does not justify permanent clutter.
14. As a collaborator, I want ownership verified before cleanup, so that shared resources and other agents remain protected.
15. As a returning user, I want interrupted work to locate its recovery state, so that lost conversation context does not prevent safe reconciliation.
16. As a maintainer, I want periodic review bounded to configured temporary locations and registered worktrees, so that housekeeping avoids machine-wide scanning.
17. As a user, I want my authorized outcome carried through eligible steps, so that intermediate milestones do not require repeated continue prompts.
18. As a user, I want genuine missing decisions surfaced precisely, so that autonomy does not invent approval or bypass dependencies.
19. As a user, I want existing answers reused and scope preserved, so that an application-planning request does not become an unrelated writing exercise.
20. As an implementation owner, I want claims and integration receipts respected across sessions, so that parallel work does not overwrite live authority.
21. As a reviewer, I want completion tied to the accepted scope and actual evidence, so that a partial result is not labeled complete.
22. As a developer, I want missing test prerequisites detected before expensive checks, so that invalid setup fails quickly and usefully.
23. As a developer, I want focused diagnosis before full acceptance reruns, so that repeated failures do not cause unnecessary full-suite churn.
24. As a user, I want test status backed by an observed run identity and result, so that idle orchestration is not confused with completed execution.
25. As a reviewer, I want validation tied to the exact revision and environment, so that stale passes cannot certify new changes.
26. As a maintainer, I want new durable documentation visible to Git, so that useful knowledge is not silently excluded.
27. As a contributor, I want stale skill references and broken navigation caught mechanically where possible, so that sessions do not guess replacement entry points.
28. As a maintainer, I want one declared source for globally installed skills, so that an unreviewed worktree does not silently become active.
29. As a user, I want ordinary edits to add no housekeeping ceremony, so that reliability does not burden every task.
30. As a user, I want context and tool costs measured against equivalent tasks, so that efficiency claims are evidence-backed.
31. As a reviewer, I want mechanical checks separated from judgment-based standards, so that implementation context is not filled with lint rules.
32. As a maintainer, I want existing safety and compliance controls preserved, so that reducing instruction duplication does not weaken enforcement.
33. As a non-code user, I want only the organization my work needs, so that coaching or advice does not acquire an engineering workflow.
34. As a maintainer, I want each adoption to have its own repository and revision evidence, so that a fixture demonstration is not represented as deployment.
35. As a user, I want unavailable validation and cleanup failures reported explicitly, so that uncertainty is not presented as success.
36. As a maintainer, I want no new helper, hook, skill, or registry without an observed gap, so that the solution remains smaller than the problem.

## Implementation Decisions

### 1. Scope, ownership, and reuse

- This is a follow-on effort, not a reopening or replacement of completed Wayfinder reliability or agent-housekeeping records. Preserve their identities, decisions, completed evidence, and outstanding delivery restrictions.
- Reuse agent-housekeeping's baseline, conditional file/service/recovery references, and native teardown rules. Its draft PR must be reviewed and incorporated through the repository's authorized delivery workflow before dependent adoption can be claimed. This specification does not authorize merging that PR or activating its draft globally.
- Required implementation surfaces are the existing setup and design flows; the planning-to-implementation handoff and continuation behavior; relevant prototype and review guidance; existing package/documentation checks; and narrowly scoped adoption checks and CI-runner improvements in Applications4Life.
- Articles is the documentation/planning adoption case: preserve its source ledger, editorial records, and existing publication boundary. Do not build the writing application or introduce software infrastructure merely to demonstrate the workflow.
- Repository-specific conventions remain repository-owned. Reusable skills describe roles and triggers rather than hardcoding Applications4Life's architecture, compliance rules, or tracker location.
- Preserve configured remote tracker authority, established local coordinator ownership, existing global installation policy, and current security controls. Shared-source deployment or migration requires the applicable repository's delivery requirements.
- Each later implementation Issue must state which repository it changes and which outcome it delivers. Cross-repository evidence names each accepted revision; a skillsrepo merge alone does not certify adoption elsewhere.

### 2. Three artifact lifetimes

| Lifetime | Authority and contents | End-of-work treatment |
| --- | --- | --- |
| Maintained project knowledge | Current architecture, codebase and data-model descriptions, decision records, operations guidance, maintained verification | Update affected knowledge with implementation; preserve version history |
| Durable effort history | Outcome, discovery, accepted designs and plans, specification revisions, approvals, implementation Issues, conclusions, necessary acceptance evidence | Keep stable identities and paths; remove completed efforts from the active queue rather than relocating them |
| Disposable execution work | Working scratch notes, alternate drafts, prototype execution files, one-off validators, raw output, temporary processes and disposable service data | Remove once no longer needed, subject to ownership and retention requirements |

A file's age, extension, ignored status, or informal use of the word plan does not determine its lifetime. An approved plan is durable. An unaccepted proposal containing unique reasoning may also need preservation. Classify based on purpose and needed evidence before creation, then promote or retire material when its purpose changes.

Do not create every possible folder or record in advance. Reuse suitable existing locations and create only the collections and artifacts actually needed.

### 3. Setup and navigation

- Extend the existing setup discovery and reviewed write flow. Identify the authoritative instruction surface, tracker, temporary root, documentation index, domain vocabulary, decision records, verification commands, and installation source from available repository evidence.
- Record a compact mapping of artifact roles to locations through the existing configuration surface and documentation index. Reuse current mappings rather than maintain a parallel manifest of every document.
- Existing documentation and tracker paths take precedence. Fresh repositories receive conventional documentation collections for architecture, codebase, data model, decisions, and operations as needed. Repository-specific glossary and domain locations remain unchanged.
- Reuse the established dedicated temporary subtree. When none exists, establish one through the housekeeping setup flow with narrow ignore rules and unique task children. Unconfigured ordinary work retains the established OS-temporary fallback.
- Repeated setup must preserve user edits, legacy content, tracker authority, and one copy of each policy. Custom documentation paths must remain usable by every consumer.
- Setup verifies that the instruction surface is actually loaded, that published conditional references resolve, and that representative durable documents are visible to Git. It does not scan all documents on every task.
- A configured reference is preferred to a package fallback. A retired skill name must produce a specific diagnostic or verified current replacement, never an invented invocation.
- Keep global installation sourced from the declared reviewed branch or committed snapshot. Validate changed mappings through the existing installer/package checks without activating development worktrees.

### 4. Durable design information

| Collection | Information it owns |
| --- | --- |
| Architecture | System responsibilities, runtime and deployment boundaries, cross-component interactions, data ownership, operational constraints and failure behavior |
| Codebase | Module boundaries, public interfaces, dependencies, invariants, representative usage and verification seams |
| Data model | Logical identity and relationships, integrity constraints, lifecycle, history, retention and mapping to the implemented schema |
| Decision records | Consequential choices, rationale, rejected alternatives and explicit supersession |
| Operations | Maintained procedures for executing, observing, recovering and operating the implemented system |

- Existing glossary or domain records own business meaning. Schema definitions and migrations own implemented physical structure. Design documents explain intent and constraints and link to those sources; do not duplicate full schemas or generate another ontology store.
- Substantive design records identify scope, status, and evidence or implementation linkage. Distinguish proposed, accepted target, implemented, and superseded. For mixed-status documents, mark the affected sections rather than applying an inaccurate single status.
- Accepted target documents may legitimately precede implementation. Mark a design implemented only when the relevant accepted revision and validation support that claim. Preserve open differences from current behavior.
- During an effort, keep proposals and evaluation in its durable record. On adoption, update the affected current project document and link to the effort evidence. Keep one current authority for each fact; historical designs remain labeled history.
- Keep editable diagram sources with their owning document. Generated renders may be retained when useful to the reader, with their source identified. Use small, non-sensitive illustrative examples. Reusable synthetic test data belongs with existing maintained fixtures; operational dumps and temporary databases do not become documentation.
- Use a short index with links and scope cues, not a mandatory catalog of all implementation details. Avoid automatic folder movement, filename churn, or mass rewriting for stylistic uniformity.

### 5. Planning, continuation, and truthful completion

- Reuse the effort overview for desired outcome, scope, authority, current pointers, and next action. Reuse individual Issue state and claim receipts for dependencies and execution ownership. Do not duplicate that state in a session ledger.
- An authorized implementation flow continues to the next eligible step after intermediate success. A status question is answered briefly and does not cancel the requested work.
- Human choices, missing authorization, unavailable required evidence, unresolved dependencies, policy rejection, and external failures are explicit blockers. Preserve the ownership rules and continue independent work already within scope; do not seize another worker's claim or redefine acceptance to make progress appear complete.
- Planning retains its human decision boundaries. Do not automatically resolve unanswered questions, treat silence as agreement, or turn specification readiness into implementation approval.
- At resumption, use current pointers and authoritative state rather than replaying the entire conversation or reading every historical revision. Verify a claimed prior completion through its receipt and relevant evidence.
- A completion statement names the delivered outcome and material qualifications. An unavailable observation is unknown, a running check is not a pass, and a historical pass does not certify a changed revision.
- Runtime interruptions cannot be eliminated by instructions. Retain a concrete next action and sufficient scoped recovery information when work cannot continue; do not introduce a background orchestrator to simulate uninterrupted autonomy.

### 6. Validation execution and observation

- Reuse existing CI and release entry points. First inspect their actual prerequisite and progress facilities; extend missing behavior rather than build a separate runner.
- Before expensive execution, verify required configuration presence, fixture availability, dependency/import readiness, relevant database role capabilities and intended disposable namespace, and runner support for the requested check. Inspect only what that run needs; never print secrets or claim privilege checks passed from a role name alone.
- Preflight failure identifies the missing condition and prevents expensive downstream execution. Preflight success is not a substitute for test collection, behavioral tests, security checks, or release acceptance.
- Diagnose a failure with the smallest relevant existing check. Rerun full required acceptance after the candidate is integrated at a fixed revision. A materially changed revision invalidates acceptance evidence for affected requirements; reuse unaffected evidence only with an explicit, supportable rationale.
- Reuse existing run output or evidence to expose run identity, source revision, environment/fixture identity, progress location, and final exit state. Store this once per run, not once per command. Lightweight status reads must not require unrestricted process scans.
- If performance checks need quiet conditions, isolate or explicitly coordinate those conditions while retaining a safe observation path. Do not assert that execution is active merely because its owner previously said it was.
- Use existing runner time limits or diagnostics for stalled checks. Report an interrupted or timed-out run as incomplete, preserve useful failure information, and release disposable resources through native teardown. Never hide failures through skips, weaker assertions, widened baselines, or prematurely closed Issues.
- Routine deterministic command execution uses the existing executor. Independent agents are reserved for independent review, behavioral replay, or justified isolation, not introduced for every shell operation.

### 7. Cleanup and periodic review

- Reuse the established housekeeping ownership, exact identity, partial-acquisition, anonymous-volume, path-boundary, retention, and recovery rules. Do not duplicate their detailed policy in this specification's consumer skills.
- At task completion or failure, release no-longer-needed owned resources. Keep useful diagnostics only with a purpose and revisit condition; remove the recovery note after reconciliation. Preserve maintained checks and requested deliverables.
- At prototype conclusion, save the question, result, limitations, and necessary reproducibility evidence before retiring its environment. Preserve an intentional branch or immutable source reference when required by the existing prototype lifecycle. Remove a disposable worktree only after accounting for unique commits and relevant tracked, untracked, and ignored work.
- Weekly housekeeping is a recommended review cadence, not an installed schedule. An explicit periodic review examines only the configured temporary locations and registered worktrees. It classifies candidates using provenance, owner inactivity, current use, and retention purpose.
- Age can prioritize inspection but cannot authorize deletion. Active, shared, ambiguous, inaccessible, or deliberately retained resources survive and are reported briefly. Historical effort records are outside disposable cleanup.
- Do not install a hook, timer, reaper, cleanup skill, acquisition helper, or general registry. If evaluation demonstrates a gap that existing native mechanisms and focused guidance cannot address, record the failing case and propose the smallest separately reviewed expansion.

### 8. Existing checks and instruction economy

- In Applications4Life, inventory currently ignored Markdown before narrowing blanket exclusions. Preserve secret/generated-output protection and existing tracked history. Verify that new representative permanent documents are not ignored.
- Extend the existing structure, documentation-link, package and installation checks where their scope fits. Detect broken configured navigation, missing published references, and references to retired installed skill entry points. Avoid fragile matching of arbitrary prose or historical quotations.
- Mechanical rules belong in deterministic checks wired to the actual CI entry points. Judgment about scope, rationale, architectural consistency, and appropriate documentation remains a review responsibility.
- skillsrepo CI must cover the actual main-target contribution path. Reuse the housekeeping PR's correction when incorporated; do not implement a duplicate fix.
- Reduce persistent instructions by removing duplicated policy and moving detailed methods to conditional references. Do not remove a security invariant or review obligation merely to meet a token target. Existing legal, privacy and compliance requirements retain their authority.
- Resynchronize affected human docs, discovery metadata, catalogs and router guidance in each delivered behavior. Preserve invocation boundaries and the existing writing-for-agents conventions.

### 9. Context and execution budgets

These budgets govern added workflow machinery, not the user's substantive task inputs, source code, or documents needed to perform the work.

| Dimension | Acceptance rule |
| --- | --- |
| Ordinary edit with no disposable work | Zero additional housekeeping/documentation inventory calls, specialized-reference reads, recovery notes or mandatory report artifacts |
| Persistent guidance | Reuse the housekeeping baseline. Aim for 150-250 combined tokens; this remains a target, not a previously approved hard limit. Measure net change and justify any increase |
| Incremental persistent text | Engineering target of at most 75 additional tokens beyond the incorporated housekeeping baseline; exceeding it requires an explicit overhead finding and reviewed disposition before acceptance |
| Newly added conditional procedure | Aim for at most 800 tokens per reference; split only along real task branches. Report larger justified requirements rather than silently omitting safety or correctness |
| Navigation | Current task authority and relevant reference discoverable from the configured entry point within two navigation steps in the evaluation fixtures |
| Ordinary task bookkeeping | Use existing effort/Issue state; no second tracker and no per-command log or status file |
| Recovery bookkeeping | At most the existing one small task recovery note when resources/evidence may survive interruption |
| Resource-producing tasks | Scoped acquisition/ownership/cleanup observations only; combine observations with existing verification where useful |
| Long-running checks | Reuse one existing run status/evidence surface and bounded progress reads; no new agent or whole-machine inventory per poll |
| Re-reading and retries | Do not reload unchanged guidance or repeat an unchanged failing command without new evidence or a changed input |

Use a named tokenizer and report characters as well as tokens. Measure the generated configuration, loaded reference chain, tool invocations, executable commands, and created bookkeeping artifacts separately. Label estimates and unavailable measures. Compare equivalent tasks under the same recorded harness/model settings; do not infer savings from a task that failed early or produced a different result.

The 75-token and 800-token figures are engineering targets introduced by this specification, not historical user commitments. If a target cannot be met, report the concrete reason and alternatives in the existing review evidence. Numerical targets never waive required controls. The zero-extra-work ordinary-edit criterion is mandatory.

## Testing Decisions

### Confirmed end-to-end seam

The user explicitly confirmed one seam: repository setup, followed by an agent planning/designing and performing or resuming authorized work, followed by observation of durable documents, history, cleanup, truthful completion and overhead. Extend the previously confirmed housekeeping seam. Deterministic checks and native resource inspection support this seam; they are not separate competing workflow platforms.

Test externally visible behavior and artifacts, not whether an instruction contains a preferred sentence. Use existing temporary-repository replay patterns, work-record tests, package/installer tests, repository structure/link checks, native fixtures and the current CI runner. Reuse valid prior evidence for unchanged behavior.

### Required scenarios and observations

| ID | Scenario | Required observable outcome |
| --- | --- | --- |
| A1 | Fresh setup | One usable role/location mapping and temporary convention; conditional references reachable; representative durable documents visible; no empty collection scaffolding |
| A2 | Existing/custom setup repeated | User choices, authority, content and stable identities preserved; zero duplicate instruction blocks, conflicting mappings or broadened ignore rules |
| A3 | Ordinary edit | Requested edit and existing relevant checks only; zero added inventories, specialized reads, recovery notes or reports |
| A4 | Architecture/codebase/data-model design | Correct responsibility and status recorded; source schema/domain authority preserved; unresolved assumptions remain provisional; no competing current copy |
| A5 | Design adoption and supersession | Current document updated with implementation/evidence linkage; accepted target remains distinguishable from implementation; historical rationale and links survive |
| A6 | Planning handoff and authorized continuation | Agent reaches the next eligible step without an unnecessary continue prompt; no unrelated prerequisite; a genuine human decision or blocker remains explicitly open |
| A7 | Fresh resumption | Agent finds current effort and ownership without lost conversation identifiers; completed, blocked, stale and active work are handled through existing authoritative gates |
| A8 | Prototype and maintained verification | Prototype conclusion and needed reproducibility evidence survive; disposable execution files disappear; maintained checks and requested outputs remain runnable/usable |
| A9 | Failure and cleanup | Actual owned file/process/Docker outcomes satisfy incorporated housekeeping criteria, including partial startup and anonymous volumes; unavailable cleanup is explicitly unresolved |
| A10 | Periodic review with concurrency | Only bounded configured candidates inspected; zero changes to active/shared/unknown resources, escaped-link targets, stable effort records or retained evidence |
| A11 | Documentation visibility/navigation | A representative previously ignored new design document becomes visible after reviewed rule narrowing; broken current links and retired active skill references fail existing checks; history and unrelated prose are not falsely rejected |
| A12 | Fast validation preflight | Missing fixture/configuration or wrong required capability fails before the expensive stage; correcting the prerequisite admits the real run; no secret values appear in output |
| A13 | Running, failed, interrupted and stale CI | Observed status corresponds to the identified actual run; no running/unknown state becomes pass; changed-revision evidence cannot satisfy final acceptance; stalled execution yields a bounded diagnostic |
| A14 | Installed source and package | Declared installation source resolves to reviewed content; draft worktrees are not silently activated; relevant package, installer and main-target CI checks pass |
| A15 | Non-code applicability | Articles retains its existing source/publication conventions; a lightweight coaching/advice task adds no engineering folders, tracker, services or routine reporting |
| A16 | Overhead | Per-scenario instruction, read, command and artifact measurements supplied; A3 is zero increment; target deviations are explained and dispositioned |
| A17 | Repository adoption | Each required live adoption has its own accepted revision, observed output and check results; fixture-only or unavailable adoption is reported as incomplete |

### Evaluation method and completion gate

- Record exact source revisions, generated setup, supplied user turns, runtime/platform, available model identity, relevant loaded guidance, expected outcomes, independently observed results, and scoped cleanup evidence in one bounded effort summary. Do not persist whole conversation dumps or another telemetry system.
- Capture before/after cases for the actual observed gaps: premature stopping or scope drift, hidden permanent documentation, stale invocation, late preflight failure, and unobserved CI status. Reuse existing red evidence only when the comparison remains applicable.
- Use fresh actor context for resumption and discovery tests; do not provide lost resource IDs, note locations, or the expected answer in the task prompt. Separate actor behavior from evaluator fixture preparation and assisted cleanup.
- Repeat the three highest-risk behavioral scenarios, ordinary edit, authorized continuation/resumption, and ownership-safe recovery, in three independent fresh contexts for the affected candidate. All must satisfy their explicit criteria. Reuse valid unchanged housekeeping ownership evidence where possible; do not rerun the entire matrix for editorial changes.
- Use one matched baseline/candidate comparison for each materially changed task class. Disclose differences in authorization, tool policy, context state, completion result, or environment. Bounded passes do not establish a statistical guarantee of future compliance.
- Deterministic negative fixtures must demonstrate that wrong authority, broken references, hidden intended documentation, missing prerequisites, and stale completion evidence are rejected where the corresponding checks apply. Checks must also admit valid cases, including custom locations and legitimate retention.
- Claims about processes and Docker require actual native observations; simulated fixtures alone do not pass those claims. Production services, sensitive datasets, cloud infrastructure and unrelated resources are not needed.
- Implementation completion requires all applicable A1-A17 observations, required repository checks, reviewed target deviations, valid integration receipts, and explicit adoption evidence. A missing required observation is a gap, not a passing limitation. A blocked cleanup may be reported honestly, but the affected cleanup observation remains unresolved until safely reconciled or explicitly accepted as a delivery exception.
- New findings are fixed within the agreed scope or recorded as blockers. Do not quietly reduce acceptance, add broad infrastructure, or mark the effort complete because the testing budget or context is exhausted.

## Out of Scope

Production feature development, building the proposed writing application, repairing every inherited application test or architecture violation, weakening security/compliance gates, and deployment to production.

Automatic migration or renaming of existing durable records; repository-wide deletion; wholesale Markdown unignore without inventory; cleanup of personal data, global caches or third-party resources; age-only deletion; cleanup while no agent or native lifecycle mechanism is running.

New cleanup skills, global registries, general evaluation platforms, background orchestrators, hooks, scheduled jobs or acquisition helpers without a demonstrated gap and separately reviewed expansion. Weekly review is not authorization to schedule automation.

Replacing the current tracker, schema authority, domain model, source ledger or installation system. Generating complete documentation mirrors of code. Loading this specification, the retrospective or historical research into ordinary task context.

Implementation Issues, code changes, installations, cross-repository adoption, PR merges or scheduling during specification publication. Specification readiness is not implementation authorization.

## Further Notes

### Evidence and existing decisions

The retrospective screened 564 locally available Codex session files with activity in the October 20-27 window across Applications4Life, skillsrepo, Articles and coaching. Worker/replay logs and inherited history are not independent conversations or independent failures. No Claude project transcripts showed activity in that window. Findings are evidence-backed candidates, not a claim of exhaustive machine or service coverage.

Sources available to implementers:

- [Existing housekeeping effort](../agent-housekeeping/README.md), [specification revision 1](../agent-housekeeping/spec.md), and [behavioral measurements](../agent-housekeeping/validation.md). Draft [PR #7](https://github.com/vincenzo345/skills/pull/7) remains a delivery dependency, not an authorized merge.
- [Wayfinder reliability retrospective](../wayfinder-reliability/retrospective.md) and [validation](../wayfinder-reliability/validation.md).
- [Stable effort workspace decision](../../docs/adr/0001-stable-effort-workspaces.md), [setup dependency decision](../../.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md), and [installation authority](../../.agents/install-block.md).
- [Earlier hygiene handoff](../../docs/plans/hygene-recommendations.md). Its preventive recommendations were explicitly separate from the original Applications4Life cleanup scope; this new effort does not silently add conditions to that existing cleanup.
- [Applications4Life documentation entry point](<C:/Users/vince/AI agency business/applications4life/app/docs/README.md>) and [existing structure/check authority](<C:/Users/vince/AI agency business/applications4life/app/docs/maintenance/repository-structure-manifest.md>).
- [Articles workflow](C:/Users/vince/projects/Articles/WORKFLOW.md).

At specification time, Applications4Life's blanket Markdown exclusion still hides hypothetical new architecture/data-model documents; its domain guidance still names a retired local skill entry point. Existing CI and structure checks already exist and should be extended. These observations must be refreshed before implementation because concurrent work may resolve them.

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

**Example 3: adapting Applications4Life without moving its tracker**

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

### Authority and handoff

The user approved the retrospective direction and requested detailed specification synthesis, with low context overhead. The extended end-to-end seam was explicitly confirmed through the question tool. No further interview is required.

This is specification revision 1 for a new follow-on effort. Keep the completed prior efforts intact. Publication marks this specification ready-for-agent; a proposed implementation breakdown and its approval are separate subsequent activities. Any later scope or acceptance change follows the existing revision and Issue reconciliation workflow.

## Revision note

Editorial clarification requested by the user: add concrete active/completed repository trees and an Applications4Life mapping illustrating already specified artifact lifetimes and location-preservation rules. No scope, acceptance criterion or approved dependency changed.
