# Workbench Workflow

**Status:** v0.6 collaborative delivery and ticket frontier

This document explains lifecycle meaning and route behavior. Workbench's purpose and authority boundaries are defined in the [charter](CHARTER.md). The versioned identifiers, route order, applicability handler IDs, gate handler IDs, planning destinations, and work statuses are owned by [`workbench-lifecycle.schema.json`](../../schemas/workbench-lifecycle.schema.json). Artifact field shapes, decision rules, and state-transition schemas belong in their named contracts; this document does not create a second vocabulary.

A free-form request is first preserved as a pre-route `intake-draft` under [`workbench-intake.schema.json`](../../schemas/workbench-intake.schema.json). It keeps the original request available while the agent inspects evidence, synthesizes the execution contract, and resolves only material unknowns. When routing is ready, `route-and-start` atomically persists the immutable routing receipt and starts lifecycle state.

When a material answer is still needed, `finalize-intake` persists the unresolved question without starting. `revise-routing` then records the answer and complete updated synthesis as an immutable successor receipt under the same work ID. Revision one remains `routing.json`; later receipts live under `routing-revisions/`, bind the exact prior receipt, and become current only as a valid contiguous chain. `start --from-routing` binds the latest ready revision. A finalized-but-incomplete route therefore never requires a replacement work item.

The routing receipt keeps six axes separate: business basis, solution context, engagement intent, planning destination, execution lane, and planning posture. Proposal is a destination, fast is a lane, collaborative is a posture, and greenfield or brownfield is solution context. Workbench compiles domain activities into one operational checkpoint per applicable phase and ends the plan at the selected destination. Fixed route IDs survive only for old journals and direct legacy starts.

## Lifecycle rules

- The lifecycle has eight stable phases. The 17 stage identifiers are domain activities grouped inside those phases.
- A compiled phase has at most one operational checkpoint: its last applicable activity. In design-and-decide, proposal is the consolidating activity after applicable experience, architecture, and data-model lenses. Other activities remain visible in the routing receipt and specialist handoff without forcing transitions.
- An activity marked not applicable can never become the phase checkpoint. Unresolved material applicability blocks the affected frontier.
- A phase can call multiple specialists. Specialist invocation does not itself advance the lifecycle; one accepted handoff may cover several activities in the same phase.
- Persisted state and recorded transitions determine position. A narrative document, tracker issue, or conversation does not.
- New evidence can invalidate an earlier result. Workbench returns to the earliest affected stage and preserves the prior result and correction history.
- Reaching the current planning destination is distinct from achieving the desired business outcome.

## Operational phases

| Phase | Activities selected as needed |
|---|---|
| Frame | Intake and outcome framing |
| Discover | Brownfield reconnaissance, evidence intake, process modeling, and process validation |
| Design and decide | Experience design, solution architecture, data-model design, and a consolidating proposal |
| Plan | Standards resolution, specification, and delivery planning |
| Implement | Implementation |
| Verify | Local verification |
| Release | Release and deployed verification |
| Measure | Outcome verification |

The last applicable activity in a phase supplies that phase's checkpoint and exit-gate identity. This preserves the specialized vocabulary while avoiding a transition for every lens. A large work item grows through map nodes, specialist tasks, evidence, and artifacts rather than ceremonial lifecycle steps.

The v0.6 source runtime adds collaborative posture, phase decision/evidence nodes, shared-understanding confirmation, artifact readiness, multiple artifacts per handoff, semantic specification and delivery gates, implementation-ticket dependency nodes, dependency-derived readiness, atomic ticket claims, and ticket-scoped proof handoffs. It keeps v0.5 records readable and replayable without rewriting them. Post-start route correction remains deferred; evidence that invalidates an earlier started phase blocks dependent work without rewriting canonical history.

## Canonical activity registry

Stage IDs are stable, kebab-case contract values.

| Stage ID | Applies when | Entry | Exit |
|---|---|---|---|
| `intake` | Every work item | A request, problem, opportunity, or hypothesis is present | Work ID, preliminary desired outcome, planning destination, candidate route, known constraints, and current authorization are recorded |
| `evidence-intake` | Existing sources must be registered or new evidence is needed | The questions or claims the evidence may inform are known | Sources have provenance, freshness, authority, confidentiality, defects, and links; unresolved defects have owners or blockers |
| `process-model` | Current or proposed work behavior must be understood | Sufficient sources exist to begin, with conflicts still allowed | Applicable actors, triggers, states, steps, branches, exceptions, handoffs, waits, controls, data, systems, measures, and variants are represented; uncertainty remains visible |
| `process-validation` | A process, demand, behavior, or value claim is unproven | A scoped hypothesis, population or context, falsifier, and evidence threshold are defined | The claim is recorded as supported, rejected, revised, deferred, or blocked for the tested conditions; follow-up work is owned |
| `outcome-framing` | Every route that may proceed beyond intake | Preliminary outcome, evidence, and constraints are available | Desired outcome, baseline or proxy, success and failure signals, exclusions, constraints, and planning destination are explicit |
| `proposal` | A sales, funding, prioritization, or proceed/stop decision needs an integrated recommendation | Outcome and current evidence are sufficient to compare credible options | Business case, target workflow, preliminary logical/deployment view, options, recommendation, assumptions, risks, phases, and limits are packaged; the decision or external decision owner is recorded |
| `experience-design` | Human tasks, interactions, information, service touchpoints, or accessibility are affected | Outcome and relevant process behavior are understood | Applicable journeys, task flows, information structure, interaction states, accessibility intent, and usability unknowns are settled or linked to owned evidence work |
| `solution-architecture` | Technical boundaries or operational tradeoffs are material | Outcome and relevant process/experience constraints are available | Selected option and rejected alternatives, logical and deployment views, interfaces, data and integration constraints, operational concerns, reversibility, and unresolved decisions are recorded at the destination's required depth |
| `data-model-design` | A database or durable store is introduced, or persisted semantics may change | Solution boundaries and an explicit persistence-impact determination are available | An evidence-backed no-impact disposition or sufficient conceptual, logical, and physical model is recorded, including invariants, ownership and tenancy, lifecycle, access patterns, security, migration and recovery, decisions, and obligations |
| `brownfield-reconnaissance` | Existing code, data, integrations, or deployment behavior will change | Repository or system scope and intended behavior are bounded enough to inspect | Current behavior, ownership, seams, dependencies, tests, data effects, compatibility and migration constraints, deployment constraints, and blast radius are evidenced |
| `standards-resolution` | Prototype, implementation, review, or release guidance must be selected | Technology and risk surface are known enough to evaluate applicability | Versioned applicable profiles, skipped modules, unknowns, executable mechanisms, and any waiver needs are recorded; re-evaluation triggers are set |
| `specification` | Delivery needs a durable behavioral contract | Required product, process, UX, architecture, data-model disposition, standards, and brownfield decisions are settled or explicitly blocked | The specification truthfully reports ready, draft, or blocked status and traces outcomes, behavior, constraints, acceptance, rollout, recovery, and open map nodes |
| `delivery-planning` | Work needs slicing, dependencies, coordination, or tracker publication | A ready-enough specification and publication authorization, when applicable, exist | Delivery slices, dependency types, coverage, proof obligations, release work, and final outcome-verification ownership are defined |
| `implementation` | An authorized change is ready to build | Required inputs, data-model disposition when persistence is present, standards profile, starting-state inventory, scope, and implementation authorization are present | The scoped change is implemented without claiming release; changed artifacts, deviations, and verification needs are registered |
| `local-verification` | An implementation or executable artifact must be checked before release | A fixed review set and required proof profile exist | Applicable tests, static checks, reviews, contract checks, and failure paths have run; results are passed, failed, or honestly blocked with evidence |
| `release` | An artifact must be promoted, published, migrated, or enabled outside the local worktree | Release authorization, acceptable local proof, target identity, rollout and recovery plan, and artifact identity exist | Promotion or rollout is recorded against the exact artifact, or the no-release disposition is explicit; incidents and rollback actions remain visible |
| `deployed-verification` | The released behavior must be proven in its target environment | A release record and safe verification method exist | Deployment identity, critical journey, integration, migration, and operational checks required by the proof profile are evidenced or blocked |
| `outcome-verification` | The desired result must be measured or transferred to an operating owner | A process change or deployment can affect the defined outcome | Result is measured against the baseline or proxy, or a time-bound measurement obligation has an accountable owner; planning acceptance and outcome achievement remain distinct |

Evidence intake, standards resolution, and outcome framing may be revisited when their inputs change. A completed phase remains historical evidence; correction creates a transition and superseding result rather than rewriting history.

## Legacy route templates

These five templates remain v0.1 compatibility route IDs for event replay and direct legacy starts. New routed work does not traverse them. Brackets mark historically conditional stages.

### Existing process to software

```text
intake
  -> evidence-intake
  -> process-model
  -> outcome-framing
  -> [process-validation]
  -> [proposal]
  -> [experience-design]
  -> solution-architecture
  -> standards-resolution
  -> specification
  -> [delivery-planning]
  -> implementation
  -> local-verification
  -> [release]
  -> [deployed-verification]
  -> outcome-verification
```

`process-validation` applies when the current process, proposed change, demand, or value premise is not supported strongly enough for the next consequential decision. `proposal` applies when approval or investment has not already been granted. Experience design applies whenever human behavior or interaction changes, including non-screen service touchpoints.

### Unproven process

```text
intake
  -> outcome-framing
  -> evidence-intake
  -> process-model
  -> process-validation
       |-> revise -> evidence-intake and/or process-model
       |-> stop, defer, or remain blocked
       `-> supported -> next applicable stage of the existing-process route
```

The process model is a hypothesis until validation supports it for the recorded population, conditions, and time period. Experiments, prototypes, research, and data analysis are uncertainty-map nodes executed while `process-validation` is active; they are not extra lifecycle stages. A supported claim enters the existing-process route at its first incomplete applicable stage, usually `proposal` or `experience-design`, rather than restarting completed work.

### Brownfield feature

```text
intake
  -> outcome-framing
  -> brownfield-reconnaissance
  -> [evidence-intake]
  -> [process-model]
  -> [proposal]
  -> [experience-design]
  -> solution-architecture
  -> standards-resolution
  -> specification
  -> [delivery-planning]
  -> implementation
  -> local-verification
  -> [release]
  -> [deployed-verification]
  -> outcome-verification
```

Reconnaissance precedes solution selection. Its output establishes current behavior and blast radius; `solution-architecture` records the intended architecture delta, and `data-model-design` makes persistence impact explicit. Business-process and experience stages remain applicable when the feature changes work outside the codebase or changes what a person must understand or do.

### Proposal only

```text
intake
  -> evidence-intake
  -> [process-model]
  -> outcome-framing
  -> [process-validation]
  -> proposal
  -> completed-for-destination
```

The proposal includes preliminary workflow and logical/deployment views appropriate to the sales or proceed/stop decision. It does not imply delivery architecture, a POC, a specification, implementation authorization, or outcome achievement. An external decision can leave the work `paused` with a named owner instead of falsely completing it.

### Small-change fast lane

```text
intake
  -> outcome-framing
  -> brownfield-reconnaissance
  -> standards-resolution
  -> implementation
  -> local-verification
  -> [release]
  -> [deployed-verification]
  -> [outcome-verification]
```

The abbreviated route is valid only when behavior and blast radius are bounded, no material decision or evidence gap is hidden, applicable standards and proof are known, and the change fits one execution context. The intake and reconnaissance records form the minimal durable behavior contract. A failed preflight expands the same work item to the earliest applicable full-route stage.

## Valid stops, pauses, and loop-backs

### Stops and pauses

- `completed-for-destination` means the authorized planning destination was reached; it never upgrades the claim to implementation, deployment, or business outcome. `completed-for-outcome` is reserved for supported outcome claims.
- `awaiting-acceptance` means the final destination gate passed but closure was not authorized. The result is ready for human review; `close` records acceptance without rerunning the completed phase.
- `stopped` is valid when the human rejects the premise, validation falsifies it, risk is unacceptable, or proceeding no longer has sufficient value. The reason and surviving obligations are recorded.
- `paused` is valid when an otherwise coherent work item is waiting for a user decision, external event, evidence source, or authorization. `blocked` means an applicable stage cannot satisfy its exit criteria. Both require an owner and next action; they are not synonyms.
- A proposal handoff, a rejected or deferred process hypothesis, and transfer of long-running outcome measurement are valid endpoints when their narrower claims are explicit.
- Closure is valid only for the claimed destination and requires its specific authorization.

### Loop-backs

- Failed or ambiguous validation returns to `evidence-intake`, `process-model`, or `outcome-framing` according to what changed.
- Experience, architecture, and data-model design may iterate when a technical constraint changes a human interaction, a user need changes a technical boundary, or persistent invariants disprove an earlier design.
- A changed stack or risk surface re-enters `standards-resolution` before affected work continues.
- Failed local verification returns to `implementation` or the earliest stage whose assumption was disproved.
- Failed deployed verification can return to `release`, `implementation`, or design; rollback remains an explicit release action.
- A missed outcome returns to `outcome-framing`, `process-validation`, or proposal/design as a new measured iteration rather than being relabeled success.
- Any downstream discovery returns to the earliest invalidated stage. The transition records cause, affected outputs, and what remains valid.

Loop-backs preserve the work ID, prior evidence, and event history. They supersede invalid conclusions and recompute the ready frontier; they do not silently edit completed artifacts.

## Lifecycle route and uncertainty map

The two structures answer different questions:

| Structure | Question | Shape | Changes when |
|---|---|---|---|
| Compiled lifecycle | What broad phase applies, and what gate controls movement? | At most one checkpoint per applicable phase through the selected destination | Applicability, destination, authorization, or a proved correction changes |
| Uncertainty map | What must be learned, tested, decided, or produced to reach the destination? | Dependency graph of outcomes, questions, evidence tasks, experiments, decisions, obligations, and deliverables | Fog becomes a question, evidence arrives, a decision settles, a dependency changes, or an obligation is created |

The active phase checkpoint supplies context for map nodes, but map-node completion does not automatically advance the phase. Its exit evaluates the registered artifacts, decisions, evidence, and human-control condition. Conversely, a map node may span phases or force a loop-back when it invalidates an earlier premise.

Workbench derives one current-state view from both structures: current route and stage, ready agent tasks, decisions waiting on the human, external blockers, changed assumptions, and the recommended next action with its reason. Neither structure duplicates the other's records.
