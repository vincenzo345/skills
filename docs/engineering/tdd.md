## What it does

`tdd` builds behavior test-first: one failing test, then the smallest implementation that passes. It tests public behavior against independently established expectations, so useful tests survive internal refactoring.

It reuses agreed test boundaries and existing coverage. A new test belongs at the cheapest stable public boundary that detects the relevant failure, with real interaction coverage where correctness depends on it.

## When to reach for it

Type `/tdd`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it when building features or fixing bugs test-first.

| Situation | Where to go |
| --- | --- |
| A defined behavior with observable inputs and outputs | `tdd` |
| The required behavior is unsettled | [to-spec](to-spec.md) records settled decisions; [design](design.md) resolves design choices |
| A hard or intermittent defect needs diagnosis | [diagnosing-bugs](diagnosing-bugs.md) |
| A ready ticket needs implementation and review | [implement](implement.md), which uses `tdd` |

## Seams and focused feedback

A **seam** is a public boundary at which a caller can observe behavior. Routine selection within the accepted approach does not need another approval. If a new boundary changes the agreed proof or behavior, the agent explains what it catches and misses before asking you to decide.

| Behavior under test | Useful coverage |
| --- | --- |
| Parsing or validation rules | Focused public-module examples |
| Persistence and tenant isolation | Real database interactions |
| Delivery and restart behavior | Relevant worker and persistence interactions |
| Complete recovery | Representative application-flow checks |

Extend a relevant existing test before adding another test of the same behavior. A cheap test is insufficient if it removes the interaction that causes the defect.

**Red-green** proceeds one behavior at a time. Expected values come from the spec, known examples or an independent oracle, not from recomputing the implementation. Refactoring remains part of review under the current skill; this update does not change that division.

Execution follows the [shared verification guidance](../../skills/engineering/setup-repo/TICKET-SIZING.md#verification-evidence): focused checks during development, affected interactions at handoff and required broader checks at their boundaries. Applicable passing evidence is reused.

## Common questions

**Do I have to choose the test boundary again for every ticket?**

No. Previously agreed boundaries carry forward. Ordinary implementation choices remain with the agent; changes to the agreed proof or behavior come back to you with concrete tradeoffs.

**Should it always start with a browser or end-to-end test?**

No. Start at the cheapest stable boundary that detects the relevant failure. Keep application-flow coverage when it proves interactions that narrower tests cannot.

**Does a refactor require rewriting the tests?**

Public behavior should remain stable. Tests coupled to private helpers or internal call order need scrutiny; external effects such as preventing duplicate paid sends can be meaningful observable behavior.

**When should testing stop?**

After relevant checks pass and required verification for the boundary is satisfied. Repeat when changes invalidate evidence, a failure needs investigation or a required check remains outstanding.

## It's working if

- Existing agreed boundaries are reused without another approval request.
- A test fails for the intended reason before the behavior is implemented.
- Assertions use independently established expected values.
- Real interaction tests remain where isolation or persistence depends on them.
- Passing checks lead to the next delivery step instead of redundant reruns.

## Where it fits

[tdd](tdd.md) is the testing reference used by [implement](implement.md) and [implement-spec](implement-spec.md). [to-spec](to-spec.md) records the accepted proof, [code-review](code-review.md) independently examines the resulting change, and [codebase-design](codebase-design.md) supplies interface vocabulary when needed. [guide-me](guide-me.md) maps the full workflow.
