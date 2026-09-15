---
name: to-spec
description: Synthesize the current conversation and repository evidence into a traceable, implementation-ready spec, without starting a fresh interview.
disable-model-invocation: true
---

# To Spec

Turn the current conversation and codebase understanding into a spec. Do not start a new interview. If a consequential question is unresolved, publish a truthful `draft` or `blocked` spec and name the decision or evidence needed; do not invent an answer merely to make the spec look ready.

Verify the model-invoked `/delivery-proof` companion is installed. If it is missing, say so and apply the complete embedded proof contract rather than omitting the gate.

Use the project's configured issue tracker, domain glossary, and ADRs. Run `/setup-matt-pocock-skills` if the tracker conventions are missing.

## Process

1. Read the relevant code, prior decisions, prototypes, research, and tracker history.
2. Separate the desired outcome from the proposed implementation. Preserve decision provenance: user-owned choices are confirmed, explicitly delegated, provisional, or blocked; facts may be evidence-backed. Evidence can inform a choice but cannot authorize it.
3. Prefer existing public test seams. If a consequential new seam was not settled earlier, record it as an unresolved decision instead of soliciting a fresh answer here.
4. Apply `/delivery-proof` to every acceptance criterion. If that companion skill is not installed, the required/achieved level, environment, independent-oracle, non-vacuity, and truthful-blocking rules embedded below still apply.
5. Run the readiness audit below, then publish to the configured tracker.

## Spec template

### Status

`draft | blocked | ready`

State why and record `Artifact type: spec`. A ready spec gets `Next skill: to-tickets` and the tracker-specific `ready-for-tickets` workflow state or label. Never apply `ready-for-agent` to a spec; that state is reserved for executable implementation tickets.

### Problem statement

Describe the user's problem and current evidence.

### Desired outcomes

Number stable outcomes as `OUT-1`, `OUT-2`, and so on. State an observable success condition for each.

### Solution

Describe the user-visible and operational solution without brittle file paths or implementation snippets.

### User stories

Use `US-*` identifiers. Make the set complete and non-duplicative. Each story has an actor, capability, and benefit.

### Invariants

Use `INV-*` identifiers for behavior or safety properties that must remain true.

### Acceptance and proof

Use `AC-*` identifiers. For each criterion include:

- source outcome, story, and invariant IDs;
- exact observable behavior;
- required proof level;
- target environment and public journey or seam;
- independent oracle or fixture;
- named expected cases or nonzero minimum population;
- accepted terminal state and destination, including any intentionally rejected/quarantined state;
- reproducible procedure and evidence artifact location.

An empty population cannot satisfy a criterion. The implementation cannot create its own oracle.
Each `OUT-*` must map to at least one criterion whose required level and environment directly observe that outcome where users or consuming systems experience it. Choose the proof level from the claim, not from currently available access.

### Implementation decisions

Use `DEC-*` identifiers. Record the interfaces, contracts, schemas, module boundaries, and technical trade-offs that were actually settled. Include state and provenance. Do not include transient file paths or code unless a small prototype-derived shape expresses the decision more precisely than prose.

### Delivery dependencies and obligations

Use `DEP-*` for external dependencies and `OBL-*` for work that must survive this spec. Give each an owner or next artifact, blocker state, and discharge condition. Include data, access, deployment, migration, human validation, operational, and documentation needs.

### Rollout and recovery

Define deployment order, compatibility/parity checks, cutover trigger, monitoring, rollback trigger and method, and any migration or cleanup. Mark sections not applicable with a reason.

### Out of scope

Exclude an item only when every desired outcome remains true without it. State the consequence of exclusion and any follow-up owner.

### Unresolved decisions

List provisional and evidence-blocked items, what would resolve them, and who owns the next step.

### Traceability

Map every `OUT-*`, `US-*`, `INV-*`, `AC-*`, `DEP-*`, `DEC-*`, and `OBL-*` forward and backward. No desired outcome or obligation may disappear between sections.

### Further notes

Include remaining context that does not belong above.

## Readiness audit

A spec is `ready` only when:

- every desired outcome has non-vacuous acceptance proof at the level and environment where the outcome is consumed;
- every criterion has a complete proof contract;
- every consequential user-owned choice is confirmed or explicitly delegated after its consequence is understood; evidence-backed facts do not substitute for decision authority;
- every dependency and obligation has an owner, state, and discharge condition;
- rollout, target-environment verification, and rollback are defined where relevant;
- traceability has no orphaned or contradicted items;
- the work can be ticketed without inventing product behavior.

Otherwise publish as `draft` or `blocked` and do not apply `ready-for-tickets`.
