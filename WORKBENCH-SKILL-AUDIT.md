# Workbench Skill Portfolio Audit

**Status:** Design input, not an implementation standard  
**Reviewed:** 2026-09-14  
**Companion plan:** [WORKBENCH-BUILD-PLAN.md](WORKBENCH-BUILD-PLAN.md)

## Verdict

The source skills are better than their current workflow.

They contain unusually strong ideas about evidence, decision authority, transcript fidelity, expert fatigue, traceability, and truthful completion. The failure is systemic: too many skills independently own routing, state, tracker behavior, readiness gates, proof rules, and handoffs. Each can be locally sensible while the overall journey remains repetitive, opaque, and difficult for the human to direct.

| Dimension | Assessment |
|---|---:|
| Specialist reasoning | 8/10 |
| Evidence and decision integrity | 8/10 |
| End-to-end coherence | 4/10 |
| Human orchestrability | 4/10 |
| Operational validation | 3/10 |
| Ready to migrate unchanged | No |

The right move is not to concatenate the skills or make a larger router. Build one small control plane, extract the best specialist behaviors behind contracts, and test the routes as a system.

## Scope and method

This review covered the skills that can participate in business intake, uncertainty reduction, design, software delivery, verification, or continuity:

- External business skills: `to-record`, `to-scope`.
- Current workflow and continuity: `ask-matt`, `grill-me`, `grill-with-docs`, `wayfinder`, `setup-matt-pocock-skills`, `handoff`.
- Evidence and decisions: `grilling`, `domain-modeling`, `research`, `prototype`, `delivery-proof`.
- Architecture and brownfield work: `codebase-design`, `improve-codebase-architecture`, `diagnosing-bugs`, `resolving-merge-conflicts`.
- Delivery: `to-spec`, `to-tickets`, `implement`, `tdd`, `code-review`, `triage`.
- External design intelligence: [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).

`teach` was excluded because it is a learning workflow rather than part of delivery. `writing-great-skills` was used as authoring guidance but is not a runtime Workbench specialist.

The review inspected the skill instructions, their directly required references, tracker adapters, validators, and executable tests. The local packaging validator passed all 42 skills. The `to-record` preservation suite passed all 27 tests. No end-to-end route scenarios or behavioral skill evaluations exist in this repository, so neither result establishes workflow quality.

## Portfolio-level findings

### High — The control plane is duplicated across specialists

`ask-matt` chooses the route; `wayfinder` maintains a tracker-native frontier; `to-scope` infers its next phase from a document tree; tracker setup defines workflow states; `to-spec`, `to-tickets`, `triage`, and `implement` each apply readiness rules; `handoff` carries conversation state through temporary files.

This is the central defect. There is no single answer to “where are we, why are we here, and what is next?” Workbench must be the only owner of route selection, lifecycle state, uncertainty nodes, transition history, and the current frontier.

### High — Artifacts have no shared identity or lineage

The current system can place evidence in `.scratch`, process models in `scope/`, domain terms in `CONTEXT.md`, decisions in ADRs, design rules in `design-system/`, specs and tickets in a tracker, proof in comments, and handoffs in the OS temporary directory. These are useful artifacts but not one work item.

Every artifact needs a stable work ID, artifact type, source references, producing stage, status, owner, and downstream consumers. A registry should point to artifacts rather than copy their contents.

### High — Strong rules are repeatedly copied instead of referenced

Decision authority and delivery-proof language is repeated through Wayfinder, `to-spec`, `to-tickets`, `implement`, `tdd`, `code-review`, triage templates, setup adapters, and the repository validator. Repetition currently acts as a safety measure, but it also guarantees drift and makes every skill heavy.

Decision policy, evidence status, proof contracts, obligation semantics, and lifecycle states need one versioned source each. Specialists should return references and stage-specific views of those records.

### High — Several important disciplines are absent

There is no complete specialist for:

- testing whether an unproven process should exist;
- combining interviews, observation, documents, system behavior, and operational data into a current-state process model;
- a proposal/business case and preliminary workflow or logical diagram;
- UX research, service design, task flows, information architecture, and usability validation;
- solution and infrastructure architecture across security, data, integration, reliability, operations, cost, and deployment concerns;
- brownfield feature reconnaissance and change-impact analysis;
- resolving which coding and DevOps standards apply;
- release, adoption, operational verification, and long-running outcome measurement.

These cannot be filled merely by expanding Wayfinder, `codebase-design`, or UI/UX Pro Max. They need focused specialists with explicit applicability.

### High — Some skills turn one useful lens into a universal law

Examples include a process always being an epic/feature/story tree, architecture being reducible to deep modules, every implementation using the same TDD sequence, and every completion claim fitting one four-level ladder. These are useful defaults in the situations they fit. They become harmful when the system cannot explain why the lens applies or let the user choose another representation.

Workbench should select methods by problem shape and risk, record applicability, and preserve alternatives. No architectural paradigm becomes the agency architecture by default.

### High — The current `to-record` proof does not prove its motivating risk

`to-record` correctly treats normalization as preservation and its 27 executable tests pass. Its verifier compares a case-folded word multiset, so it can detect added or missing words while permitting reorder. It cannot prove sentence order, punctuation, turn boundaries, or speaker attribution—the exact area the skill says raw exports corrupt.

Keep the current verifier as one control, but add source-span or token-alignment lineage and an attribution review. The process also needs an owner and next action for unresolved record defects; carrying a flag forward is not enough.

### Medium — Passing validation currently proves packaging, not behavior

`skills/scripts/validate-skills.py` usefully checks names, metadata, invocation policy, links, docs, catalogs, portability markers, and the presence of selected phrases. It does not run a skill, validate handoff artifacts against schemas, simulate route transitions, or measure user understanding. Some phrase checks also cement duplicated policy into multiple files.

Keep packaging validation. Add schema tests, state-transition tests, golden scenario fixtures, mutation-scope tests, and human-control evaluations.

### Medium — Tracker integration arrives too early

Wayfinder and the delivery skills treat GitHub, GitLab, or local Markdown as stores for planning state. That makes external collaboration convenient, but it couples cognition, state, and publication. It also encourages a large issue graph before the plan is stable.

Workbench state should be file-backed and tracker-neutral. A tracker adapter publishes or synchronizes only artifacts that have reached the appropriate gate.

### Medium — Human-control safeguards can become ceremony

The grilling consequence receipt and `to-scope` anti-exhaustion rules are worth preserving. Applied to every choice, however, one-question-at-a-time interviews, repeated confirmations, and full proof tables can exhaust the same user they are intended to protect.

Add a materiality test. Group non-consequential defaults, ask only the highest-value unresolved question, record a settled decision once, and let downstream stages consume it without asking again.

## Skill dispositions

The disposition is about each skill's role in Workbench, not whether its source is “good” or “bad.”

| Skill | Preserve | Change | Disposition |
|---|---|---|---|
| `to-record` | Verbatim source, explicit provenance, visible defects, executable preservation check, confidentiality | Support multiple evidence types; add order/span/attribution lineage; make unresolved-defect ownership explicit; remove fixed `.scratch` location | Rebuild as evidence-ingest specialist |
| `to-scope` | Recognition over generation, expert/builder authority, coverage and conflict passes, manual steps, provisional/confirmed distinction, anti-exhaustion rule | Split discovery, process modeling, validation, and build scoping; replace mandatory tree with selectable process views; admit documents, observation, logs, and data by authority; remove its private resume engine and direct ticket handoff | Split into process-model and scope specialists |
| `wayfinder` | Outcome vs planning destination, fog, breadth-first questions, evidence tasks, decision provenance, blockers, obligations, falsifiers | Use the Workbench node graph and event log; stop owning trackers, routing, and narrative map state | Extract uncertainty engine into Workbench |
| `ask-matt` | One memorable entry point and route explanations | Static route list, conversation-dependent “smart zone,” missing business/UX/architecture stages | Supersede with `workbench start/status/next` |
| `grill-me` | A no-codebase entrance to informed questioning | Separate entry point is unnecessary once Workbench supports net-new work | Absorb into Workbench intake |
| `grill-with-docs` | Decisions and unresolved items leave a durable record | It is only a two-skill wrapper and has no stage contract | Reduce to a decision-session adapter or absorb |
| `grilling` | User-owned vs delegable vs evidence-blocked choices, recommendation last, confusion is not consent, consequence receipt | Add materiality, decision grouping, prior-decision reuse, fatigue budget, and Workbench decision IDs | Retain and adapt |
| `domain-modeling` | Canonical vocabulary, scenario testing, sparse ADR criteria, decision provenance | A domain model needs concepts, relationships, events, invariants, actors, and context boundaries—not only a glossary; separate domain facts from architecture decisions | Expand domain model; centralize decisions |
| `research` | Primary-source preference, facts vs inference, honest blockers, mutation-scope discipline | Add question/falsifier, freshness, search scope, claim-to-source ledger, confidence, and Workbench evidence-node output; allow first-party operational evidence | Expand into one evidence-task executor |
| `prototype` | One question, production exclusion, synthetic data, variants, decision capture, no accidental promotion | Add hypothesis, falsifier, success measure, expiry/cleanup owner; keep broader experiments outside this code-prototype skill | Retain as experiment subtype |
| UI/UX Pro Max | Local searchable catalog, progressive lookup, stack detection, accessibility-first checklist, explicit zero-result fallback | It starts from style/product keywords, conflates UX/design/implementation, and persists a second state tree; its reasoning catalog is prescriptive and lacks source fields; remove its “then implement” handoff | Vendor as advisory engine behind an experience-design specialist |
| `codebase-design` | Deep-module vocabulary, interface-as-test-surface, locality and leverage, design alternatives | Stop banning legitimate architecture terms; treat deep modules as one lens; add failure, data, concurrency, distributed-system, security, and operational perspectives elsewhere | Retain as optional module-design reference |
| `improve-codebase-architecture` | Hotspot-based inspection, concrete candidates, visual before/after, ADR awareness | Do not equate architecture health with module depth; make HTML optional; remove “spare moment” refactoring implication; separate survey from design decision | Narrow to module-deepening review; add broader architecture review |
| `to-spec` | Ready/draft/blocked truthfulness, stable IDs, outcomes/invariants, traceability, rollout and recovery | Consume UX, architecture, data, standards, and brownfield artifacts explicitly; make sections applicability-aware; route gaps back to map nodes; avoid forcing user stories on non-user work | Adapt to shared artifact contract |
| `to-tickets` | Requirement ledger, vertical slices, start blockers vs verification dependencies, coverage denominator, final outcome-verification work | Derive from the Workbench graph; avoid copying full criteria everywhere; allow enabling, migration, risk-reduction, operations, and verification ticket types; include standards profile | Adapt as delivery-plan publisher |
| `implement` | Starting-state inventory, user-change protection, blocker checks, progressive verification, review of the actual delta, truthful receipts | Use the resolved standards profile; calibrate method to change type/risk; register even the fast lane; add explicit deploy/release handoff | Adapt as execution coordinator |
| `tdd` | Red caused by missing behavior, public seams, independent expectations, non-vacuous tests, refactor after green | Make it a selected method rather than a universal gate; support characterization tests, IaC/config/doc changes, and justified exceptions; make examples language-specific references | Retain as conditional implementation method |
| `code-review` | Separate standards/spec axes, fixed review set, untracked files, criterion-to-proof analysis, no implicit fix authority | Consume an exact standards profile; expose any delegated review axes; add applicability for UX, security, architecture, data, and operations without duplicating their standards | Adapt as verification aggregator |
| `delivery-proof` | Claim-to-evidence chain, independent oracles, non-vacuity, required vs achieved proof, failed vs blocked, owned obligations | Make proof fields applicability-aware; avoid treating proof kinds as a strict total order; transition long-running outcome measurement to an owned operating stage; remove copies from other skills | Retain as one shared proof policy |
| `setup-matt-pocock-skills` | Explore first, preserve working configuration, preview before write, verify after write | Replace product-specific naming and tracker-first setup with Workbench initialization, schema/version checks, adapter configuration, standards profiles, and safe re-run behavior | Supersede with `workbench init` |
| `handoff` | Reference existing artifacts, redact sensitive content, state the next focus | OS-temp conversation summaries are lossy and can disappear; they should not be the state mechanism | Keep only as optional export; Workbench state replaces it |
| `triage` | Explicit incoming-work states, verified claim, durable agent brief, distinction between missing info and agent readiness | Separate prioritization, claim verification, and implementation planning; map to Workbench IDs; do not treat a PR as merely an issue with code; route hard bugs to diagnosis | Retain as external-intake adapter |
| `diagnosing-bugs` | Tight feedback loop, minimization, ranked falsifiable hypotheses, instrumentation cleanup, regression evidence | Diagnosis must not imply authorization to fix; permit hypothesis-led observability when a local reproducer is impossible; return findings to the map | Split diagnose from fix; retain specialist route |
| `resolving-merge-conflicts` | Inspect both intents and run integration checks | “Never abort” and unconditional stage/commit behavior exceed safe authority; add dirty-work protection and explicit completion authorization | Retain only after safety rewrite |

## UI/UX Pro Max: specific conclusion

The repository is valuable raw material, but it should not be copied unchanged as the Workbench UX function.

Its current skill has good operational mechanics: small targeted searches, explicit stack detection, a retry-and-fallback rule, a persistent master/override model, and an accessibility-first checklist. The current metadata identifies version `2.13.0`, and the root repository carries an MIT license. Preserve the upstream license and attribution when vendoring.

The weakness is epistemic. The design-system generator maps product labels and style keywords to recommendations. In the current `ui-reasoning.csv`, entries such as healthcare → social-proof/neumorphism and financial dashboard → OLED dark mode/red-green alerts are catalog opinions, not validated facts about this project's users. The CSV exposes `Reasoning` and `Confidence` columns but the inspected entries leave them empty, and the UX guideline CSV has no source URL or source-version column. That makes the engine useful for generating candidates and checklists, not for selecting the product experience.

The source skill also ends by synthesizing its results and implementing. Workbench must break that shortcut:

```text
user/process evidence
    -> experience model and task flows
    -> candidate interaction/visual directions
    -> prototype or usability evidence when uncertain
    -> confirmed design decisions
    -> specification
    -> implementation
```

Vendor a pinned upstream commit into a clearly named directory. Add `UPSTREAM.md`, the original `LICENSE`, the pinned commit and version, a modification log, search regression fixtures, and an update-review procedure. An [open upstream issue](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/481) reports inconsistent license metadata in a CLI subdirectory, so decide exactly which upstream paths are copied and resolve that ambiguity before vendoring CLI assets. This is a provenance warning, not a legal conclusion.

Primary sources inspected:

- [Current skill instructions](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/ui-ux-pro-max/SKILL.md?plain=1)
- [Current package metadata](https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/skill.json)
- [UX guideline data](https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/src/ui-ux-pro-max/data/ux-guidelines.csv)
- [UI reasoning data](https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/src/ui-ux-pro-max/data/ui-reasoning.csv)
- [Root license](https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/LICENSE)

## Capabilities to add

These are internal specialist roles. They should not all become commands the user must remember.

1. **Evidence intake** — ingest transcripts, documents, observations, screenshots, system traces, datasets, and prior decisions with provenance and defects.
2. **Process model** — describe current actors, triggers, states, branches, exceptions, handoffs, controls, data, systems, measures, and observed variants in a representation that fits the process.
3. **Process validation** — turn an unproven process into hypotheses, experiments, success/failure thresholds, evidence, and a stop/revise/prove decision.
4. **Proposal** — produce the preliminary business case, recommended operating model, assumptions, options, phased plan, risks, and sales-pitch diagrams without pretending implementation has been proven.
5. **Experience design** — own service blueprint, task flows, information architecture, interaction states, accessibility intent, usability questions, and design decisions. It may call the vendored UI intelligence engine.
6. **Solution architecture** — compare options across domain boundaries, data, integration, security/privacy, reliability, performance, observability, deployment, infrastructure, cost, and reversibility; create logical and deployment views appropriate to the decision stage.
7. **Brownfield reconnaissance** — map current behavior, ownership, seams, dependencies, data migrations, tests, deployment constraints, and blast radius before proposing an architecture delta.
8. **Standards resolver** — load only applicable, versioned policy modules and executable configurations; produce an applicability receipt and waivers.
9. **Release and outcome verification** — promote the same artifact, execute rollout/recovery plans, verify the deployed journey, and transfer long-running measures to an accountable operating owner.

Data analysis does not need its own top-level stage. It is an agent-executable evidence-task kind on the uncertainty map, with a question, dataset provenance, quality checks, method, result, limitations, and the decision it supports.

## Binding migration rules

The build should preserve these rules even if skill names and artifact formats change:

1. One control plane owns route, lifecycle stage, uncertainty graph, state transitions, and next-action selection.
2. Every artifact and decision belongs to a stable work item and has lineage to its inputs and consumers.
3. Evidence may establish facts and inform recommendations; it does not authorize user-owned consequences.
4. Confusion cannot count as consent, and acceptance cannot be won through question or document volume.
5. Current-state views are derived from structured state; narrative artifacts are not hidden state machines.
6. Specialist instructions contain domain method, not copies of global routing, proof, decision, or tracker policy.
7. Every stage declares applicability, entry criteria, exit criteria, artifacts, and what happens when it is skipped or blocked.
8. Framework, language, architecture, UX, test, and operational guidance is loaded only when applicable and records the selected version.
9. Prototype, recommendation, implementation, deployment, and observed outcome remain distinct claims.
10. Tracker publication, repository mutation, implementation, deployment, closure, and commits each respect their own authorization boundary.
11. Vendored content is pinned, attributed, licensed, regression-tested, and updated through review rather than silently floated.
12. A route is not considered proven until a fresh agent can resume it from files and the human can explain the current state without rereading the conversation.

## Recommended migration order

1. Freeze representative source artifacts and expected behaviors from `to-record`, `to-scope`, Wayfinder, grilling, ticket coverage, and delivery proof as fixtures.
2. Build the Workbench state, event, map, decision, artifact, and handoff contracts.
3. Add behavioral route tests before migrating specialists.
4. Migrate evidence intake and process modeling first; preserve the source skills unchanged until the replacement passes comparison fixtures.
5. Add process validation and proposal generation, including a proposal-only stop point before POC or implementation.
6. Add experience design and solution architecture as separate collaborators.
7. Add brownfield reconnaissance and standards resolution.
8. Centralize delivery-proof policy, then adapt specification, ticketing, implementation, and review to consume it.
9. Add release and outcome verification.
10. Vendor UI/UX Pro Max only after its advisory boundary and provenance tests exist.
11. Adapt triage, diagnosis, and merge resolution as specialist entrances after the main three routes work.
12. Retire `ask-matt`, temporary handoff state, and specialist-owned routing only after the Workbench replacements pass real scenarios.

## Honest recommendation

Do not begin by rewriting the skill prose. Begin by writing the shared contracts and evaluations that will tell us whether a rewrite is better.

The source material is strong enough to preserve, but not coherent enough to serve as the architecture. The Workbench should be deliberately boring: small schemas, explicit state transitions, short current-state views, and narrow specialists. The intelligence should remain in the specialists; authority, state, and movement between them should not.
