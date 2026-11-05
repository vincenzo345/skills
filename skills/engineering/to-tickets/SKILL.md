---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
disable-model-invocation: true
---

# To Tickets

Map a plan, spec, or conversation into **outcomes**, then refine the next eligible work into **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it. Read [ticket sizing](../setup-repo/TICKET-SIZING.md) before sizing or revising the breakdown.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-repo`.

Before drafting or publishing, read the configured tracker and [shared work-record contract](../setup-repo/WORK-RECORDS.md). Repository locations override defaults. For local tracking, publish approved issues through the shared producer into the identified effort, with explicit basis, order, blockers and durable approval evidence. Each body must carry enough scope, observable acceptance criteria, spec/design references and delivery requirements for a fresh implementation session.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Prefer the existing implementation path. Prefactor when it removes a concrete obstacle to the feature and reduces total work, including verification and integration.

### 3. Map coverage and refine the next slices

Map each requirement to an outcome and its likely dependencies. Fully refine only the next eligible outcomes using the shared sizing rubric; keep later outcomes explicitly provisional with their refinement condition. On an existing breakdown, review integrated evidence first, preserve completed work and stable IDs, and reconcile affected remaining coverage rather than recreating the plan.

Before presenting the breakdown, review the combined approach against the required outcomes. Trace prerequisites to the mechanism that created them, reconsider that mechanism when a simpler accepted path suffices, and combine slices when they form one coherent outcome within the sizing gate. Preserve coverage and surface consequential approach changes for the user's decision.

When a refined plan is linked from the spec or effort, compare the whole proposed breakdown against it: map its agreed outcomes to issues or provisional coverage, check that the slices and blockers preserve its approach and constraints, and identify omissions or added mechanisms. Correct routine discrepancies before presenting the breakdown; present consequential changes for the user's decision. If no plan exists, use the spec or conversation as the basis.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through the layers needed for its outcome, including verification
- A completed slice is demoable or verifiable on its own
- Each dispatched slice meets the shared sizing and readiness gate
- Keep necessary prefactoring with the outcome it enables; a separate ticket needs its own useful compatibility result

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. No blockers means dependency eligibility, not readiness or dispatch authority.

**Wide refactors use expand–contract.** Add the compatible new form, migrate bounded caller groups, then remove the old form after all callers migrate. Each slice must satisfy the shared sizing and verification gate, including an observable compatibility outcome. If a batch cannot be verified independently, refine the compatibility boundary before dispatch.

### 4. Confirm the authorization boundary

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work
- **Coverage and readiness**: requirement references; refined or provisional; for refined work, the sizing note required by the shared reference

For the initial breakdown or a consequential change proposal, ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Obtain approval of the initial breakdown, distinguishing ready slices from provisional coverage. For routine revisions during authorized implementation, record existing authority and proceed without another quiz; use the shared reference's authorization boundary for consequential changes.

### 5. Publish the tickets to the configured tracker

Publish approved refined tickets. Retain provisional outcomes and requirement coverage in the existing breakdown by default; publication alone never makes them ready. **How** depends on the tracker `/setup-repo` configured:

- **Local files** → publish one file per ticket under `work/<effort>/tickets/<NN>-<slug>.md`, in dependency order (blockers first), preserving existing numbering. Use the shared contract and body template below. Follow its publication capability guidance if provisional outcomes need individual records; the CLI's ready default is only suitable for refined work.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so blocking edges can reference real identifiers. Use native blocking relationships where available, otherwise body references. If the source was an existing issue, make each ticket its sub-issue (tracker doc's operation). Apply `ready-for-agent` only after approval and the shared readiness gate; publish provisional issues as `needs-info` with the missing refinement named. Current basis, completed blockers and exclusive ownership still gate implementation. Follow the [remote adapter contract](../setup-repo/REMOTE-WORK.md).

Hand off the refined **frontier**, provisional coverage and next refinement conditions. Refresh both after integration evidence; an empty ready frontier does not mean provisional requirements are complete.

Preserve parent acceptance criteria and lifecycle. Update the existing breakdown/coverage section when revising work, with links to retained evidence and replacement outcomes.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None".

**Sizing and coverage:** requirement references and the shared reference's readiness evidence, estimate and confidence rationale; or provisional status and missing refinement.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Sizing and coverage

Requirement references and the shared reference's readiness evidence, estimate and confidence rationale; or provisional status and missing refinement.

## Blocked by

- A reference to each blocking ticket, or "None". Omit this section when blockers were set as native edges.

</issue-template>

In either form, link the spec and design basis so a fresh session can resolve them. Avoid specific implementation file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
