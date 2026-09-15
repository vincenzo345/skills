# ADR 0001: Route profiles over fixed workflow routes

**Status:** Accepted  
**Date:** 2026-09-14

## Context

Workbench v0.1 selects one of five fixed routes. Those route names conflate several different facts: whether the business basis is a hypothesis or an operating process, whether software is greenfield or brownfield, whether the user wants exploration or implementation, where the run may stop, and whether a fast lane is safe. This makes ordinary requests hard to classify and encourages an oversized route when only one uncertainty needs investigation.

Workbench must also preserve v0.1 event replay and support staged migration. The current lifecycle cannot yet compile every greenfield or mixed-process profile into stages.

## Decision

Workbench will persist an immutable routing receipt, bound to the exact intake record, with five independent axes:

- Business basis: `hypothesis`, `operating-process`, `supplied-requirements`, or `technical-only`.
- Solution context: `greenfield`, `brownfield`, `process-only`, or `undetermined`.
- Engagement intent: `explore`, `plan`, `implement`, or `release`.
- Destination: one of the lifecycle's planning or delivery destinations.
- Execution lane: `fast` or `full`.

The receipt also records rationale, evidence, explicit facts, assumptions, unresolved material questions, stage-applicability recommendations, and granted versus withheld actions. Proposal is modeled as a destination, fast as a lane, and greenfield or brownfield as solution context.

During migration, a complete supported profile may name a v0.1 `runtime_route`. Existing route IDs and event semantics remain valid for replay. Profiles with no honest legacy mapping, including initial greenfield delivery profiles, are persisted but cannot start until stage compilation supports them.

Discovery will escalate only as required:

1. Targeted inspection of named evidence and the relevant repository surface.
2. Focused investigation of one material blocking question.
3. Deep uncertainty mapping only for dependent unknowns, conflicting evidence, high-risk or hard-to-reverse decisions, multi-session coordination, or explicit user request.

Workbench remains the sole coordinator. Specialist skills perform research, analysis, prototyping, grilling, and domain modeling for named questions; they do not own lifecycle state or silently choose material business and technical tradeoffs.

## Considered options

### Keep fixed routes

This preserves a smaller implementation but cannot accurately represent combinations such as an unproven greenfield interface, a supplied-requirements brownfield feature, or a technical-only greenfield build. It also hides why stages apply.

### Create a route for every combination

This makes combinations explicit but causes a combinatorial route catalog, duplicated definitions, and brittle changes whenever an axis or stage is added.

### Embed Wayfinder or a new discovery coordinator

This could preserve thorough discovery behavior but would create competing state owners and restore the opacity and over-expansion Workbench is meant to reduce.

## Consequences

- Routing becomes explainable and correctable without changing the user's original intake.
- Stage applicability can later be compiled from facts instead of being encoded in proliferating route names.
- v0.1 remains replay-compatible while v0.2 capabilities are added incrementally.
- Some valid profiles will initially stop at `routing-blocked`; this is deliberate and more honest than a false route.
- The receipt adds one record and validation boundary before lifecycle start.
- Corrections after finalization require a future append-only routing-correction event; v0.2's first slice does not mutate a receipt in place.
