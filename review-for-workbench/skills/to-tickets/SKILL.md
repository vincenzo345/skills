---
name: to-tickets
description: Convert a ready spec into traceable tracer-bullet implementation tickets with explicit blockers, proof contracts, and complete source-to-ticket coverage.
disable-model-invocation: true
---

# To Tickets

Break a ready spec into vertical slices that can be implemented in fresh sessions without losing requirements. Use the tracker configured by `/setup-matt-pocock-skills`; its documentation controls physical paths, issue relationships, labels, and where the coverage artifact lives.

Verify `/delivery-proof` and `/grilling` are installed before starting. If a companion is missing, name it; embedded proof rules remain binding and consequential unresolved choices must not be guessed.

## 1. Load and validate the source

Read the complete spec or plan, its comments, linked decisions, prototypes, and research. Do not ticket a `draft` or `blocked` spec as if it were ready. If a legacy artifact has no status, audit it against `/to-spec` and `/delivery-proof`; preserve history and record missing readiness work. If either companion skill is not installed, apply the readiness and proof rules embedded here rather than skipping the gate.

Do not change, reinterpret, or weaken source criteria while slicing. Proposed changes go back to the source artifact and its authorized owner.

## 2. Build the requirement ledger

Before choosing slices, inventory every source ID:

- outcomes, stories, invariants, and acceptance criteria;
- decisions and their provenance;
- dependencies and `OBL-*` delivery obligations;
- rollout, compatibility, cutover, rollback, and outcome-verification needs.

Record the original wording. This ledger is the denominator for coverage; an omitted requirement cannot disappear because no ticket mentions it.

## 3. Draft vertical slices

Each ticket should cut a narrow but complete path through the necessary layers and fit one fresh context window. It must be independently demoable or verifiable at the proof level it owns. Use expand-migrate-contract tickets for wide mechanical refactors that cannot safely land as vertical slices.

For each ticket specify:

- **What it delivers** — user-visible or operational behavior;
- **Covers** — exact source IDs and unchanged criterion text;
- **Discharges** — ticket-owned `OBL-*` items and their discharge conditions;
- **Start blockers** — prerequisites needed to implement safely, including required decisions, data, access, or earlier tickets;
- **Verification dependencies** — deployment, target access, real data, or human validation needed only for later proof, with a downstream proof owner;
- **Acceptance proof** — required level, environment, public journey/seam, independent oracle, expected population, accepted terminal state/destination, procedure, and artifact;
- **Status** — ready only when the ticket can start without inventing behavior.

If no implementation slice proves the complete real journey or desired outcome, add a final outcome-verification ticket. A later verification dependency does not block safe lower-level implementation, but it must be its own ticket or owned obligation when appropriate. Deployment and human checks are work with owners, not footnotes.

## 4. Build and audit the coverage matrix

Persist a source-to-ticket-to-proof coverage matrix at the location defined by the configured tracker:

`source ID -> ticket(s) -> proof owner -> required level -> evidence location -> status`

Require:

- every source ID maps to at least one ticket or a justified exclusion;
- every ticket maps back to source IDs;
- shared obligations have exactly one accountable proof owner;
- no criterion is "covered" only by setup, mocks, skipped checks, or an empty population;
- blockers and dependency edges form an executable frontier;
- the final ticket set can prove every desired outcome at its required level.

## 5. Confirm consequential slicing choices

Present the ticket titles, blockers, delivered behavior, covered source IDs, and proof level. Ask only about choices that materially change scope, sequencing, ownership, or evidence. Use `/grilling` when the consequences are not already understood. Do not ask the user to approve mechanical details the source already settled.

## 6. Publish

Publish one issue or file per approved ticket in dependency order using the configured tracker. Use native blocking relationships where available and text edges otherwise. Do not hardcode a local directory here and do not close or modify a parent issue unless explicitly authorized.

Apply `ready-for-agent` only to tickets whose blockers, criteria, proof contract, and source references are complete. Work the frontier: open, unblocked, ready tickets can start.

## Ticket template

```md
# <Ticket title>

**Status:** ready-for-agent | blocked
**What it delivers:** <complete vertical behavior>
**Covers:** <source IDs and unchanged criteria>
**Discharges:** <OBL-* IDs and discharge conditions, or none>
**Start blockers:** <implementation prerequisites, or none>
**Verification dependencies:** <later proof dependency and owner, or none>

## Acceptance proof

| Criterion | Required level | Environment / seam | Independent oracle | Expected population | Terminal destination | Procedure | Artifact |
|---|---|---|---|---|---|---|---|
| AC-* | ... | ... | ... | ... | ... | ... | ... |

## Proof receipts

<Filled during implementation as passed, failed, or blocked; include achieved proof level and do not pre-mark passed.>
```
