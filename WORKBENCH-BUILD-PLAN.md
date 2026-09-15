# Workbench Build Plan

**Status:** In development — v0.5 first-class data-model design source-validated
**Recorded:** 2026-09-14

## Implementation progress

The first contract-and-runtime slice now exists:

- Four foundation documents define purpose, workflow, artifacts, and informed-decision policy.
- A machine-readable lifecycle registry owns eight operational phases, 18 reusable domain activities, five legacy replay routes, planning destinations, gate handler IDs, and honest work statuses.
- Twelve bundled schemas define lifecycle/common vocabulary plus pre-route intake, intake-bound routing, state, events, maps, artifacts, decisions, proof, authorizations, and specialist handoffs.
- Five executable route scenarios cover existing process, unproven process, brownfield feature, proposal-only, and the small-change fast lane.
- Comparison fixtures preserve evidence attribution, process modeling, uncertainty mapping, informed decisions, ticket coverage, and proof-level behavior.
- A coherent proposal checkpoint forward-tests all eight record types. Focused negative cases reject missing consequence receipts, delegation bounds, replay changes, idempotency keys, and canonical stage IDs.
- `scripts/validate-workbench.py` checks the schemas, closed references, lifecycle registry, scenarios, record instances, comparison oracles, and selected cross-record invariants. Runtime proof is intentionally reported by a separate black-box suite.
- `scripts/show-workbench-status.py` reads a persisted checkpoint, rejects unsafe dangling references, and renders the five human-control answers plus agent, user, and external frontiers without mutating state. Deterministic JSON output supports later UI work.
- `skills/workbench/` is a self-contained skill package. Its stdlib-only CLI now includes profile compilation, atomic `route-and-start`, append-only pre-start `revise-routing`, `accept-handoff`, derived checkpoint receipts, multidimensional verification status, replay, and revision-bound mutations.
- Free-form intake preserves the user's exact request and references before interpretation. Preferred `route-and-start` persists the synthesized profile and starts its compiled lifecycle atomically; `finalize-intake` remains the deliberate pause point. Unlisted capabilities are persisted as withheld by default.
- `status` and `resume` return the complete actionable projection; `next` remains an optional focused view. A bound start cites and hashes both `intake.json` and the latest valid routing receipt. Greenfield and brownfield profiles compile directly without inventing a fixed route for each combination.
- Event replay reconstructs state and map from an empty projection, validates every event/state/map/proof/authorization against the bundled schemas, checks canonical transition metadata and exact target IDs, and blocks snapshot divergence.
- Mutations use idempotency fingerprints, expected revisions, an OS-released exclusive lock, a transaction journal, content hashes, and bounded roll-forward recovery. Gate enforcement includes registered exit-gate identity, receipt freshness, destination proof kind, exact proof semantics, and scoped implementation, deployment, and closure authorization.
- The black-box runtime suite covers normal commands, durable free-form intake, routing finalization and blockers, append-only routing revision, legacy receipt upgrade, exact revision provenance, phase compilation, explicit data-model classification, accepted handoffs, record and content tamper detection, proof-target fidelity, separated verification scopes, corruption rejection, stale revisions, illegal before-values, record identity conflicts, malformed proof/authorization records, capability scope/expiry, destination completion, crash recovery, and atomic rejection. The v0.5 source run passes 85 tests; the previously installed v0.4 package passed 83.
- The v0.4 package is installed at `C:\Users\vince\.agents\skills\workbench` and exposed to Codex at `C:\Users\vince\.codex\skills\workbench`. The source and installed junction each pass all 83 runtime/status tests; an isolated copied package passes validation plus 24 focused routing and v0.3 compatibility tests. Its 25 maintained source files match the installed hashes. Prior v0.2, v0.3, and pre-v0.4 copies remain recoverable under `C:\Users\vince\.agents\skill-backups`, outside the discoverable skill directory.
- The v0.3.1 skill correction narrows new-item invocation to an explicit human signal, treats specialist activities as methods rather than automatic subagents, reuses one evidence inventory and canonical phase artifact, makes review and verification risk-targeted, and moves legacy manual-receipt instructions off the normal path.
- The v0.5 correction makes `data-model-design` a first-class Design and Decide activity. Every greenfield or brownfield software profile must explicitly record its applicability; database-impacting work cannot silently proceed to specification or implementation, while an evidenced no-impact disposition keeps bounded work lean.

Independent reviews first blocked mutation until lifecycle, decision, delegation, replay, handoff, scenario, map, and proof-vocabulary drift was resolved. Runtime review then found and drove fixes for shallow embedded-record checks, duplicate identities, record-target tampering, crash-stale locks, schema-invalid replay, mismatched proof semantics, and contradictory audit metadata.

The v0.3 source kernel compiles applicable activities into at most one operational checkpoint per phase and stops the plan at the selected destination. It accepts one structured specialist handoff with locally verified artifact integrity, registers artifact/decision/proof/authorization outputs atomically, rejects proof whose achieved environment, seam, or journey differs from its requirement, and reports verification concerns independently. Legacy routes remain replay-compatible, but new routed work uses `profile-compiled` state. v0.4 adds pre-start routing correction; map-node creation, dependency-derived readiness, post-start route correction, validation loops, remote-artifact retrieval, and map rendering remain explicit later slices.

## Proposed v0.3: proportional orchestration

Workbench may grow as large as genuine uncertainty and delivery risk require. Its control overhead must grow only when work creates knowledge, establishes a control, authorizes an action, transfers ownership, or proves a claim.

The v0.3 adjustments are:

- Treat `intake`, reconnaissance, process modeling, experience design, architecture, standards, specification, and related labels as reusable activities grouped under eight phases: frame, discover, design-decide, plan, implement, verify, release, and measure.
- Compile at most one operational checkpoint per applicable phase. A phase handoff records every activity applied or skipped; the labels remain available without forcing separate transitions.
- Compile from the five-axis routing profile and explicit applicability evidence. Fixed route IDs are compatibility data, not the source of new execution state.
- End the active plan at its selected destination. Release and outcome work are future extensions until requested, not pending work on a local-implementation item.
- Preserve the exact raw intake, then permit routing and lifecycle start as one atomic `route-and-start` operation after inspection. `start --from-routing` remains compatible and derives repeated values from the receipt.
- Let mutations return the updated projection. `status` already includes the frontier and next action; agents do not routinely call both `status` and `next` after the same change.
- Replace invisible internal ceremony with three human-facing visibility moments: a compact execution card after routing, consequence receipts only for material decisions or blockers, and a multidimensional verification report at the selected destination. Do not require stage-by-stage approval when the user already authorized the bounded work.
- Accept one handoff bundle containing the specialist handoff and its produced artifact, decision, proof, and authorization records. Workbench verifies local artifact existence and digest and registers the bundle atomically.
- Permit `advance-stage --accepted-handoff` to derive the mechanical gate envelope from a registered handoff instead of requiring a manually authored receipt file.
- Use explicit authorization grants with default deny. A derived withheld list may be persisted for compatibility, but the agent does not have to enumerate it.
- Use one proof record as the canonical requirement-to-proof matrix. Generated delivery summaries and ticket views must not become parallel proof stores.
- Report feature implementation, focused verification, integration journey, repository health, user acceptance, deployment readiness, deployed behavior, and business outcome separately.
- Require v0.3 proof to name its environment, seam, and journey. Achieved proof passes only when that target exactly matches the required target; unavailable prerequisites remain blocked.
- Keep event sourcing, replay, revision checks, idempotency, transaction recovery, stable identities, content integrity, authority boundaries, and distinct proof levels.

The manual-table extraction audit is the first v0.3 regression: process modeling and proposal remain non-applicable, six phase checkpoints replace thirteen stage transitions, artifacts are registered rather than referenced through shadow Wayfinder state, and an isolated browser harness cannot pass an authenticated-journey requirement.

## v0.3.1: execution economy

Workbench must optimize useful work, not minimize the apparent size of the process. Necessary research, design, implementation, and proof may be extensive. Waste is work that repeats context, state, reasoning, artifacts, or verification without changing a decision or confidence in a claim.

The execution-economy correction therefore:

- starts new Workbench state only after an explicit user signal; active persisted work may still resume when the user asks to continue or names its ID;
- keeps the Workbench entrypoint narrow and discloses intake, routing, discovery, gate, state, and legacy compatibility instructions only on their relevant branches;
- treats a specialist as a method and handoff contract, not automatically as another skill invocation, agent, document, or lifecycle transition;
- uses the current agent and shared evidence inventory for related work, reserving subagents for independent evidence or independence-sensitive review with material expected value;
- accepts one canonical artifact and consolidated handoff for a phase when they satisfy all included activities, instead of producing parallel Wayfinder, Workbench, specification, and proof state;
- derives a fixed review and test set from the actual change, risk, applicable policy, and destination; focused checks run first, pre-existing repository health remains separate, and corrected findings receive targeted re-review;
- stops at the selected destination and does not perform release, outcome measurement, full-suite validation, or repeated review simply because those capabilities exist; and
- enforces an entrypoint-size budget in packaging validation so future safety additions do not silently recreate a giant coordinator.

This is a proportionality policy, not a shortcut policy. Evidence failure, conflicting findings, broad blast radius, regulation, or difficult proof expands the work. A clear bounded task stays bounded.

## v0.4: same-item routing revision

The finalized-intake pilot exposed a control-plane defect: Workbench could persist material questions, but once the user answered them the runtime offered no supported way to update the route. Asking to create a successor work item preserved immutability at the cost of continuity, comprehension, and unnecessary ceremony.

The v0.4 correction:

- keeps the original `routing.json` immutable and appends later receipts under `routing-revisions/`;
- retains one work ID and selects the highest valid contiguous routing revision as current;
- records a revision reason and the answer plus source for every unresolved question removed by the revision;
- binds each revision to the exact reference and digest of its predecessor;
- requires an expected routing revision and idempotency key so stale or repeated updates are safe;
- makes `status` and `resume` show routing lineage and resolved answers;
- binds lifecycle start to the exact latest ready revision and rejects every later pre-start routing mutation; and
- preserves backward compatibility by treating older receipts without an explicit revision field as revision one.

This solves the pre-start clarification path only. Evidence that invalidates routing after lifecycle start still requires a separate event-sourced route-correction slice; agents must preserve the same item and report that limitation rather than editing state or creating a duplicate.

## v0.5: first-class data-model design

Database design must not disappear inside a generic architecture or implementation step. The v0.5 correction:

- adds `data-model-design` to Design and Decide and `data-model` to the artifact vocabulary;
- requires every greenfield or brownfield software routing receipt to classify the activity explicitly;
- makes the activity the phase checkpoint when persistent concepts, invariants, ownership, lifecycle, access patterns, security, or migration behavior may change;
- permits a concise evidence-backed no-impact disposition when persistence is genuinely unaffected;
- requires the applicable disposition before specification or implementation; and
- routes detailed conceptual, logical, physical, migration, operational, and proof guidance through one conditional reference rather than bloating the Workbench entrypoint.

## Purpose

Build a coherent Workbench that helps a human remain the informed orchestrator of business-process discovery, validation, solution design, software delivery, and verification.

Workbench coordinates focused specialist skills. It preserves state, explains routing, records decisions, and verifies handoffs. It is not an all-knowing advisor and does not replace human ownership of material decisions.

The detailed source-skill review and migration dispositions are recorded in [WORKBENCH-SKILL-AUDIT.md](WORKBENCH-SKILL-AUDIT.md). This plan contains only the binding conclusions from that review.

## Honest assessment

The concept is strong because it addresses the important problem: not merely getting agents to produce work, but ensuring the human understands what was learned, what was decided, why a recommendation was made, and what should happen next.

The primary risk is ambition. Workbench could recreate the weaknesses of Wayfinder or the unexercised DevOps standard in a larger form: sophisticated reasoning, extensive documentation, and recommendations that are difficult for the user to interrogate. A large, untested system would repeat the problem Workbench is intended to solve.

Development must therefore proceed as thin, exercised vertical slices. The team should not migrate every skill, rewrite every standard, or integrate every UI/UX resource before one end-to-end route works transparently.

## Routing profile retained from v0.2

Workbench will not treat one route label as the complete description of a request. Routing records five independent axes:

| Axis | Initial values | Question answered |
|---|---|---|
| Business basis | `hypothesis`, `operating-process`, `supplied-requirements`, `technical-only` | What justifies the work? |
| Solution context | `greenfield`, `brownfield`, `process-only`, `undetermined` | What environment is being changed? |
| Engagement intent | `explore`, `plan`, `implement`, `release` | What is the user asking Workbench to do now? |
| Destination | proposal, proof of concept, specification, implementation plan, locally verified implementation, released software, or business outcome | Where may this run stop? |
| Execution lane | `fast`, `full` | How much ceremony is justified by uncertainty and risk? |

The axes are persisted in an immutable routing receipt derived from the exact intake record. Facts, assumptions, unresolved material questions, evidence, stage recommendations, route rationale, and the user's authorization boundary remain visible. Proposal is a destination, fast is a lane, and greenfield or brownfield describes solution context; none is a competing entrance.

The v0.3 lifecycle compiles applicable activities from this profile into one checkpoint per active phase and stops at the selected destination. The five v0.1 route IDs remain replay-compatible metadata; new routed state uses the compiled profile. Material unresolved questions or undetermined applicability still block starting rather than being forced into a convenient route.

Discovery is a bounded protocol, not a second coordinator:

1. Inspect the named sources and repository surface needed to classify the request.
2. Investigate one focused question when a material uncertainty blocks routing or a decision.
3. Build a deeper uncertainty map only when multiple dependent unknowns, conflicting evidence, a hard-to-reverse or high-risk decision, multi-session coordination, or an explicit user request justifies it.

Workbench owns the map, routing, state, and gates. Research, data analysis, repository inspection, prototypes, grilling, and domain modeling are specialist methods selected for a named question. Grilling follows evidence when a consequential choice remains; it is not the default discovery engine. A standalone discovery skill will be considered only after two real pilots show a repeated method that these specialists cannot cover.

## Target workflow

The first route will take an existing, understood business process into software:

```text
Existing process
    -> understand current state
    -> define problem and desired outcome
    -> create proposal
    -> design UX and solution architecture
    -> select applicable standards
    -> write specification
    -> create tickets
    -> implement and verify locally
    -> release and verify deployment
    -> measure or transfer ownership of the outcome
```

The proposal is a valid stopping point. A preliminary business case, target workflow, logical architecture, assumptions, risks, and phased plan can support a sales decision before a POC or implementation is authorized. Workbench must distinguish this planning destination from delivery of the business outcome.

The following v0.1 routes remain executable compatibility envelopes for direct legacy starts and replay. They are not the v0.3 classification or execution model.

### Unproven-process entrance

```text
Hypothesis
    -> experiment
    -> collect evidence
    -> revise, stop, or prove
    -> enter the existing-process software route when justified
```

### Brownfield-feature entrance

```text
Codebase reconnaissance
    -> impact analysis
    -> architecture delta
    -> enter the shared software route
```

### Small-change fast lane

```text
Bounded request
    -> confirm behavior, blast radius, applicable standards, and proof
    -> implement and verify
    -> release as applicable
```

The fast lane applies only when no consequential choice or missing evidence is being hidden, the affected area is understood, and the change fits one execution context. It still creates a minimal work item and evidence record. A failed preflight expands the route instead of guessing.

These are legacy paths and stopping points in one system. The routing profile determines which stages should apply; a route ID must not erase or replace the profile.

## Uncertainty mapping

Workbench maintains two related structures:

- The **lifecycle route** identifies the broad kind of work underway and the stages that apply.
- The **uncertainty map** identifies what must be learned, tested, decided, or produced to reach the desired outcome.

The uncertainty map is the capability inherited from Wayfinder. It is central whenever the destination is understood but the route is not. It is not merely a status visualization.

### Preserve from Wayfinder

- A desired outcome distinct from the planning artifact or handoff.
- **Fog of war** that remains visible until it can be expressed as a precise question.
- Breadth-first discovery of the questions blocking progress.
- Research, data analysis, repository inspection, and other agent-executable evidence tasks.
- Prototypes and experiments that answer behavioral or visual questions without becoming production implementation by accident.
- Blocking relationships between evidence, decisions, obligations, and deliverables.
- Human ownership of consequential business, product, architecture, risk, and scope decisions.
- Explicit delegation when the user authorizes an agent to decide within stated bounds.
- Evidence-blocked work remaining open with an owner and next action.
- Assumptions, falsifiers, corrections, and reversals when new evidence invalidates the map's premise.
- Delivery obligations that keep necessary downstream work from disappearing when they leave the current map.
- Exercising important artifacts instead of treating reasoned design as operational proof.
- Durable state that survives fresh agent sessions.

### Replace from the existing map format

- Replace a large narrative map with a structured node-and-edge graph.
- Replace duplicated ticket summaries with short linked gists.
- Replace chronological ordering as the primary view with dependencies and a derived ready frontier.
- Replace inline amendment layers with current state plus an append-only event history.
- Replace one broad `resolved` status with states that distinguish evidence, human decisions, exclusions, supersession, and completed tasks.
- Replace narrative ownership and blockers with required structured fields.
- Replace an ever-growing map with an admission test that ties every new node to an outcome or planning-destination requirement.
- Replace forensic rereading with a one-screen current-state view.

### Map node contract

Every node records at least:

```yaml
id: E-01
kind: evidence-task
question: Where does the current process lose time?
why_it_matters: The proposed process should target the measured constraint.
owner: agent
status: ready
depends_on: []
supports:
  - D-01
done_when:
  - data quality limitations are recorded
  - cycle time is calculated for every measurable step
  - suspected bottlenecks include supporting evidence
evidence: []
```

Permitted node kinds initially are `outcome`, `question`, `evidence-task`, `experiment`, `decision`, `obligation`, and `deliverable`. Add another kind only after two scenarios cannot be represented correctly without it.

The map's generated current-state view shows:

- Desired outcome and planning destination.
- Current lifecycle stage.
- Ready agent tasks.
- Decisions waiting on the user.
- External and evidence blockers.
- Recently changed assumptions or conclusions.
- The recommended next node and why it has priority.

Detailed evidence remains behind links. The generated view is not a second source of truth.

### Map completion criteria

A map can hand off or close only when:

- Every desired outcome traces to settled decisions and downstream obligations.
- No unresolved fog is silently omitted.
- Every open node has an owner and next action or is explicitly evidence-blocked.
- Every exclusion explains why the desired outcome remains achievable without it.
- Every necessary item outside the current planning destination is represented by an owned obligation.
- The difference between completed planning and achieved business outcome is explicit.

## Process evidence and validation

Workbench treats a transcript as evidence, not the entire truth. Evidence intake can register interviews, observations, policies, regulations, existing forms, screenshots, system behavior, logs, datasets, and prior decisions. Each source records provenance, freshness, confidentiality, known defects, and what kind of authority it carries. Conflicts remain visible until resolved; neither the cleanest document nor the most confident speaker wins automatically.

The process model records the applicable actors, triggers, goals, states, steps, branches, exceptions, handoffs, waits, controls, data, systems, measures, and observed variants. A tree, swimlane, state model, service blueprint, or other view may be generated from that model when it fits; no single view is the canonical representation for every process.

Recognition-based expert review, coverage and conflict passes, visible manual work, provisional versus confirmed statements, and protection against acceptance by exhaustion are preserved from `to-scope`. Workbench owns resumption and state so the process specialist does not encode another workflow engine in its documents.

An unproven process reaches the software route only when the agreed validation claim is supported at its required evidence level. The decision may instead be revise, run another experiment, defer, or stop. “Proven” is scoped to the tested population, conditions, and time period; it is not a permanent universal label.

## Architectural boundaries

Workbench owns:

- Work-item creation and resumption.
- File-backed state and append-only transition history.
- Route selection and an explanation of that selection.
- Stage applicability and exit criteria.
- Decision, override, and uncertainty records.
- Artifact and specialist handoff validation.
- A clear account of the next available action.

Specialist skills own:

- Evidence intake and source preservation.
- Business-process discovery, modeling, and build scoping.
- Process validation and experiment design.
- Solution proposals.
- Experience design, UI/UX intelligence, and usability validation.
- Solution and infrastructure architecture.
- Brownfield codebase reconnaissance.
- Engineering-standards applicability.
- Specifications, tickets, implementation, release, and outcome verification.

Workbench coordinates those specialists through contracts. It does not reproduce their domain instructions.

## Skill portfolio migration strategy

The source skills will not be copied into one larger skill. Their disposition is:

| Treatment | Skills and capabilities |
|---|---|
| Extract into the control plane | Wayfinder's uncertainty engine; `ask-matt` routing; specialist resume logic; temporary handoff state |
| Rebuild or split | `to-record`; `to-scope`; setup; process modeling; process validation; proposal; experience design; solution architecture; brownfield reconnaissance; standards resolution; release/outcome verification |
| Adapt to shared contracts | `grilling`; `domain-modeling`; `research`; `prototype`; `to-spec`; `to-tickets`; `implement`; `code-review`; `delivery-proof` |
| Retain as conditional specialist methods | `codebase-design`; `tdd`; `triage`; `diagnosing-bugs`; `resolving-merge-conflicts`; the narrowed module-deepening portion of `improve-codebase-architecture` |
| Vendor as an advisory engine | UI/UX Pro Max, pinned and attributed, behind the experience-design boundary |
| Supersede after parity is proven | `ask-matt`; `grill-me`; `grill-with-docs` as a separate wrapper; `setup-matt-pocock-skills`; OS-temporary `handoff` as state storage |

Migration is governed by these requirements:

- Preserve behavior with comparison fixtures before retiring a source skill.
- Put route, stage, map, decision, artifact, and transition state in one control plane.
- Give every artifact a work ID, artifact ID, type, source lineage, status, owner, and named consumer.
- Keep decision policy, proof policy, lifecycle states, and tracker behavior in one versioned source each; specialists reference them instead of embedding copies.
- Select process, architecture, UX, testing, and standards methods by applicability and risk rather than treating one lens as universal.
- Make tracker publication an adapter action after a gate, not the canonical reasoning store.
- Keep prototype evidence, recommendations, implementation, deployment, and measured outcomes as distinct claims.
- Require separate authorization for repository mutation, tracker publication, implementation, commits, deployment, and closure.
- Test human comprehension as a workflow outcome, not merely file validity.

## Milestone 1: Workbench kernel

Create the following foundation before rewriting specialist skills:

```text
docs/workbench/
|-- CHARTER.md
|-- WORKFLOW.md
|-- ARTIFACT-CONTRACTS.md
`-- DECISION-POLICY.md

schemas/
|-- workbench-lifecycle.schema.json
|-- workbench-intake.schema.json
|-- workbench-routing-receipt.schema.json
|-- workbench-state.schema.json
|-- workbench-event.schema.json
|-- workbench-map.schema.json
|-- workbench-artifact.schema.json
|-- workbench-decision.schema.json
|-- workbench-proof.schema.json
|-- workbench-authorization.schema.json
`-- workbench-handoff.schema.json

tests/scenarios/
|-- existing-process-to-software/
|-- unproven-process/
|-- brownfield-feature/
|-- proposal-only/
`-- small-change-fast-lane/

skills/workbench/
|-- SKILL.md
|-- references/
|   |-- routing.md
|   |-- stage-gates.md
|   `-- state-management.md
`-- scripts/
    |-- start-work.py
    |-- show-status.py
    |-- advance-stage.py
    |-- select-next-node.py
    `-- render-map.py
```

The kernel initially performs only five responsibilities:

1. Start or resume a work item.
2. Persist the lifecycle route, uncertainty graph, and the history that produced their current state.
3. Show the current state, derive the ready frontier, and explain the recommended next stage or node.
4. Record material decisions and user overrides.
5. Validate an output contract before handing work to another skill.

The kernel does not initially provide business, architecture, engineering, or UX advice.

### Kernel completion criteria

Milestone 1 is complete only when:

- `start`, `status`, `next`, and `resume` work after a fresh context or agent session.
- The persisted state, not conversation history, determines the current stage.
- Map nodes, edges, owners, dependencies, and evidence references survive a fresh session.
- Ready agent tasks and user-owned decisions are derived from node state rather than inferred from prose.
- Each transition records its cause, inputs, outputs, actor, and timestamp.
- Every artifact and decision has stable identity and input/output lineage across specialist handoffs.
- Route selection and skipped stages are visible and explained.
- A user can override a recommendation without corrupting the route history.
- Repeating a completed operation is safe or produces a clear conflict.
- Invalid state and incomplete handoffs are rejected with actionable errors.
- A generated current-state view fits on one screen and links to details rather than duplicating them.
- The five scenario fixtures can assert expected routes and valid stopping points without relying on hidden context.
- Packaging checks, schema/transition tests, route scenarios, and human-control evaluations are reported separately; one passing layer cannot stand in for another.

## Specialist handoff contract

The canonical serialized envelope is [`workbench-handoff.schema.json`](schemas/workbench-handoff.schema.json); its meaning and validation order are defined in [`ARTIFACT-CONTRACTS.md`](docs/workbench/ARTIFACT-CONTRACTS.md). This plan intentionally does not duplicate the field list.

Every specialist handoff identifies its work, node, canonical stage, specialist, owner, operation key, and exact input fingerprint. It separates consumed record references, applicability, findings, bounded options, recommendations, decisions or blockers, produced artifacts, proposed node updates, authorization references, and routing advice. The specialist proposes changes; Workbench validates and records acceptance atomically.

The schema-valid proposal checkpoint under `tests/records/proposal-only-checkpoint/` is the executable example. This contract prevents reasoning from disappearing inside a polished artifact while keeping specialists out of lifecycle and authority ownership.

## Human-control test

After every stage, the user must be able to answer:

1. Where are we?
2. What did we learn?
3. What did we decide, and which alternatives were rejected?
4. Why is the proposed stage next?
5. What remains uncertain?

If Workbench cannot make these answers apparent, the stage has failed even if its artifact is technically strong.

## Anti-overcomplication constraints

- Every artifact has a named downstream consumer.
- Every stage has explicit applicability conditions and exit criteria.
- Workbench explains why a stage applies, why it applies now, and the consequence of skipping it.
- A specialist presents no more than three meaningful options by default.
- A recommendation states assumptions, tradeoffs, confidence, and what it makes harder later.
- The user owns material business, product, architecture, risk, and scope decisions.
- User overrides are recorded and respected without repeated argument.
- A new abstraction or specialist is introduced only after at least two scenarios require it.
- A documented control is not called operational without execution evidence.
- Project state must be understandable without rereading the conversation.
- Workbench remains one coordinator with focused specialists, not one giant skill.

## Architecture integration

Architecture runs at the depth justified by the planning destination:

- A proposal uses preliminary context, workflow, logical-component, integration, and deployment views. Assumptions and unvalidated choices remain visible; the diagram communicates a plausible route, not a proven design.
- A POC architecture isolates the questions being tested and records what the POC cannot prove.
- A delivery architecture settles the boundaries and operational decisions needed for specification, implementation, release, and recovery.
- A brownfield change adds a current-state view, blast-radius analysis, compatibility and migration constraints, and an explicit architecture delta.

The architecture specialist checks applicable concerns across domain boundaries, data, integration, interfaces, security/privacy, reliability, concurrency, performance, observability, deployment, infrastructure, cost, testability, maintainability, migration, and rollback. It returns the concerns applied and skipped, with reasons.

Clean Architecture, hexagonal or ports-and-adapters design, domain-driven design, deep modules, event-driven design, functional or object-oriented techniques, and similar paradigms are selectable lenses. None is a default agency architecture. A lens is used only when its tradeoffs fit the problem, and the selection is recorded as a decision when it materially constrains later work.

## Engineering-standards integration

Standards enter gradually. The first vertical slice includes only a small common, Python, testing, and CI profile rather than the complete standards corpus.

At runtime, the standards specialist will:

1. Detect applicable language, framework, data, deployment, exposure, and change-surface dimensions.
2. Produce an applicability receipt showing what it loaded, skipped, and could not determine.
3. Let the user correct ambiguous or consequential applicability decisions.
4. Save the resolved profile with the work item.
5. Re-evaluate the profile when implementation changes the relevant technology or risk surface.
6. Record verification evidence separately from the policy and its implementation mechanism.

Prototype work can use a lighter profile, but irreversible data, credential, privacy, and safety constraints remain applicable.

## UI/UX integration

UI/UX participates at two different depths:

- During an unproven process, it helps create inexpensive experiments and interfaces that test behavior before software is justified.
- During solution design, it defines production interaction flows, information architecture, states, accessibility, and design-system decisions.

UI/UX Pro Max will be vendored into this repository with provenance and license information. Its guidance will be adapted behind Workbench's contracts rather than made responsible for routing or product decisions.

The vendored engine is a candidate generator and heuristic/reference lookup, not evidence of user need or authority to select a design. Experience design owns service blueprints, task flows, information architecture, interaction states, accessibility intent, and usability questions. Uncertain visual or behavioral choices route through prototypes or user evidence before becoming confirmed decisions.

Vendor an exact upstream commit, retain the upstream license and attribution, record local modifications, add regression fixtures for representative searches, and require review before upstream updates. Resolve the upstream CLI license-metadata inconsistency identified in the skill audit before copying CLI-specific assets.

## Development sequence

1. Freeze synthetic or safely anonymized comparison fixtures for transcript preservation, process reconstruction, uncertainty mapping, informed decisions, ticket coverage, and delivery proof. **Complete for v0.1.**
2. Define the machine-readable lifecycle registry and the state, event, map, artifact, decision, proof, authorization, and handoff contracts. **Complete for v0.1.**
3. Turn the five legacy routes and stopping points into executable acceptance scenarios. **Complete for v0.1.**
4. Build free-form `capture-intake`, then `start`, `status`, `next`, and `resume`, with replay and transition safety. **Complete and globally installed for v0.1.**
5. Add `finalize-intake` and an immutable routing receipt that separates business basis, solution context, engagement intent, destination, and lane; project it through `status`, `next`, `resume`, bound starts, and replay. **Complete, forward-tested, and globally installed for v0.2.**
6. Add proportional phase compilation, destination truncation, atomic route-and-start, accepted handoffs, local artifact integrity, proof-target fidelity, and multidimensional verification. **Implemented, source-validated, copied-package forward-tested, and globally installed in v0.3: 79 black-box runtime/status tests, 10 comparison cases, 10 negative contract cases, 14 record instances, five scenarios, 12 schemas, and skill-package validation pass.**
7. Add same-item, append-only pre-start routing revision with explicit question resolutions, lineage validation, exact start binding, and legacy-receipt compatibility. **Complete, forward-tested, and globally installed for v0.4: 83 source tests, 24 copied-package compatibility tests, 83 installed-package tests, and skill-package validation pass.**
8. Make data-model design a first-class conditional activity with an explicit routing disposition for every software profile. **Complete and source-validated for v0.5: 85 runtime/status tests, schema/fixture validation, skill-package validation, and plugin-manifest validation pass.**
9. Exercise the manual-table feedback case plus existing-process, greenfield, and brownfield requests through the v0.3 kernel using real contracts and specialist stubs where needed.
10. Rebuild `to-record` as evidence intake, retaining its tested word-preservation check while adding source-span and attribution lineage.
11. Split `to-scope` into process modeling and build scoping; preserve recognition-based review, authority, coverage, conflicts, manual work, and anti-exhaustion behavior without requiring every process to be a tree.
12. Add process validation and proposal generation, including a proposal-only stop before POC or implementation.
13. Add experience design and solution/infrastructure architecture as collaborating specialists.
14. Add brownfield reconnaissance and architecture-delta handling.
15. Add the standards resolver with a small vertical profile.
16. Centralize the delivery-proof contract, then adapt `to-spec`, `to-tickets`, `implement`, and `code-review` to consume it.
17. Add release, deployed verification, and transfer of long-running outcome measurement.
18. Vendor and adapt UI/UX Pro Max after its advisory boundary and update tests are exercised.
19. Adapt triage, diagnosis, module-deepening, TDD, and merge resolution as conditional specialist entrances and methods.
20. Retire the superseded router, setup, and handoff behaviors only after comparison fixtures and real scenarios pass.
21. Exercise the complete system on real work before declaring version 1 stable.

## First pilot

Use one bounded, real, existing business process whose desired outcome is understood but whose constraint or improvement path is not. The pilot should require at least one agent-executable evidence task, such as analyzing operational data to locate a bottleneck. A synthetic intake-to-approval process with timestamp data is the fallback when no real pilot is available.

The pilot is intended to test orchestration mechanics rather than demonstrate every specialist capability. Stubs are acceptable for specialists that have not yet been built, provided their input and output contracts are real.

### Pilot completion criteria

The pilot is complete only when:

- It travels from intake through a verified implementation plan or deliberately recorded stop decision.
- Every stage consumes named upstream artifacts and produces named downstream artifacts.
- Evidence tasks appear on the map, execute only when ready, and attach their results to the decisions they support.
- Every material recommendation exposes its reasoning and alternatives.
- User decisions and overrides survive a fresh agent session.
- The selected route can be explained entirely from persisted state.
- The current frontier distinguishes agent-ready work, user decisions, and external blockers.
- Irrelevant specialist and standards references are not loaded.
- At least one route correction is exercised and leaves an intelligible history.
- The user can pass the human-control test at every stage.
- A proposal-only run can stop with an honest preliminary diagram and unresolved assumptions without creating a POC, spec, or implementation tickets.
- The transcript fixture detects a speaker-attribution defect even when the word multiset is unchanged.
- Proof of packaging, artifact validity, local implementation, deployment, and business outcome is reported as distinct evidence.

## Deferred until the kernel is proven

- Migrating every existing skill.
- Rewriting the complete coding and DevOps standards.
- Supporting every language, framework, cloud, and database.
- Building a polished Workbench UI.
- Making every path fully automatic.
- Treating generated documentation volume as evidence of completeness.

The existing `PROTOTYPE-workflow-state.html` remains a visualization experiment. File-backed state and event contracts are the source of truth. The UI can become data-driven after those contracts stabilize.

## Immediate next action

Complete and promote the v0.3 correction slice:

1. ~~Run the entire schema, comparison, status, and black-box runtime suite against the source package.~~ **Passed.**
2. ~~Forward-test the manual-table feedback route from fresh repositories, including atomic route/start, six compiled checkpoints, accepted artifact handoff, derived checkpoint advance, blocked authenticated-journey proof, and separated failed repository-health status.~~ **Passed as black-box tests.**
3. ~~Verify old v0.1/v0.2 event journals still replay and direct legacy starts remain compatible.~~ **Passed in the full regression suite.**
4. ~~Review the package instructions for command economy: two-command intake/start, one projection per checkpoint, and no mechanical `status` plus `next` repetition.~~ **Updated and package-validated.**
5. ~~Forward-test the copied package from a non-source location, then install v0.3 globally and rerun the installed-package suite before treating it as the default coordinator.~~ **Passed: 20 focused copied-package tests and 79 tests through the global junction.**
6. ~~Apply the v0.3.1 execution-economy correction, remove blanket specialist dependencies, relocate discoverable backups, and reinstall globally.~~ **Passed: 43-skill packaging validation, 79 source runtime/status tests, installed package validation, exact 25-file source/install hash parity, one discoverable Workbench folder, and 20 focused installed-package tests.**

7. ~~Validate and globally promote v0.4, including the exact finalized-question/answered-question failure case, legacy receipt compatibility, stale-update rejection, predecessor tamper detection, and fresh-repository installation proof.~~ **Passed: 83 source tests, 24 isolated-package focused tests, 83 installed-package tests, schema/fixture validation, package validation, and exact 25-file source/install hash parity.**

After v0.5 is promoted, add map-node mutation and dependency-derived readiness as one bounded slice, then post-start route correction and validation loops. Add a new discovery abstraction only if two real pilots expose the same unmet method.

Workbench v0.4 remains the globally installed coordinator; v0.5 is the source-validated candidate. The next runtime slice after promotion is map-node mutation and dependency-derived readiness, followed by post-start route correction and validation loops. Those deferred capabilities must not be simulated by hand-editing canonical state.
