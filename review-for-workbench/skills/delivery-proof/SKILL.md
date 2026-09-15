---
name: delivery-proof
description: Define and evaluate truthful completion evidence for specs, tickets, implementations, and reviews. Use when deciding what "done" means, tracing requirements to proof, or checking whether evidence is sufficient, independent, non-vacuous, and from the required environment.
---

# Delivery Proof

Completion is a claim backed by evidence, not a synonym for code written, tests run, or a ticket closed. Apply this contract whenever another skill defines acceptance criteria or reports progress.

## Preserve the artifact chain

Trace every desired outcome through the artifacts that are meant to deliver it:

`outcome -> decision/spec criterion -> implementation ticket -> change -> proof receipt`

Record delivery obligations as stable `OBL-*` identifiers. Every obligation needs an owner or next artifact and a discharge condition. An artifact may finish its own job while carrying obligations forward; an effort is complete only when every effort-level obligation is discharged.

## Name the required proof level

For each criterion, report the highest level the evidence actually establishes—never a higher one. The overall state is bounded by every unmet required criterion, not by the best result in the set:

1. **implemented** — the intended change exists in the reviewed change set.
2. **locally-verified** — independent checks pass in a representative local or test environment.
3. **deployed-verified** — the deployed target environment passes the required checks.
4. **outcome-verified** — the real user/business outcome is observed over the required population or journey.

A lower level never implies a higher one. A commit proves only that a checkpoint exists. A unit test cannot prove deployment, and a successful deployment cannot by itself prove the outcome.

Choose the required level from the claim being made, not from the access or environment currently available. Every desired outcome must have at least one criterion that observes it where its users or consuming systems experience it.

## Write proof contracts before implementation

For each criterion, record:

- **Criterion** — stable source ID and exact statement.
- **Required proof level** — one of the four levels above.
- **Environment** — where the behavior must be observed.
- **Journey or seam** — the public boundary exercised.
- **Independent oracle or fixture** — where expected results come from.
- **Expected population** — named cases, identities, or a nonzero minimum.
- **Procedure** — reproducible commands or human steps.
- **Artifact** — where logs, screenshots, reports, or observations will live.

Do not invent missing business expectations during implementation. Mark the criterion blocked and route the unresolved decision upstream.

## Require non-vacuous, independent evidence

- Establish the expected population before applying a pass-rate or completeness threshold.
- An empty or unexpectedly reduced population cannot pass.
- The implementation under test cannot generate its own golden values or oracle.
- An intermediate, candidate, quarantined, staged, dead-letter, or rejected artifact cannot satisfy a criterion for accepted, published, or consumable output. Exercise and assert the named terminal state and destination.
- Zero output can pass only against a named nonzero input population whose accepted expectation explicitly requires zero output.
- Skipped or disabled checks, mock-only evidence, harness failures, and commands that never exercise the named seam are not proof.
- Mocks may prove a local contract, not a real integration or end-to-end journey.
- Missing access, data, deployment, or human validation produces `blocked`, not `passed`.

## Produce a proof receipt

For every criterion, preserve the contract and append:

- **Actual population**
- **Achieved proof level**
- **Result** — what was observed
- **Artifact or log** — durable pointer when available
- **Status** — `passed`, `failed`, or `blocked`

A receipt is `passed` only when its achieved level meets the criterion's required level in the named environment. Lower-level success may be recorded, but the criterion stays `blocked` until the required evidence can be obtained. Use `failed` when a check ran and observed behavior that does not meet the criterion; use `blocked` when the required evidence could not be obtained. Never convert "not run," "cannot access," or "awaiting deployment" into success.

## Control acceptance changes

Implementation and review may clarify a criterion but must not silently weaken, waive, or replace it. Keep the original text and ID, document the proposed change and consequence, and route outcome-reducing choices through an informed decision. Evidence may establish facts and support a recommendation; it cannot authorize a user-owned product, trust, security, privacy, legal, or business trade-off. If the source artifact is not updated by an authorized owner, the original criterion remains binding.

## Close at the correct scope

- A planning artifact may finish when all downstream obligations are traced to an owner or next artifact with a discharge condition.
- An implementation ticket closes only when its own criteria and ticket-owned obligations have sufficient proof.
- The overall effort closes only when every outcome and effort-level obligation is discharged at its required proof level.

Report partial success precisely: for example, "implemented and locally verified; deployed and outcome verification blocked on production access."
