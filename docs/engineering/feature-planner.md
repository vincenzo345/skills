## What it does

`feature-planner` develops an implementation-ready plan grounded in the available repository and the user's goals. It evaluates and revises the plan before presenting it, while keeping discovery non-mutating.

## When to reach for it

Type `/feature-planner`, or the agent can invoke it when implementation planning or plan review is needed. Use it when you need a concrete approach and verification plan before coding. For a collaborative interview that retains domain decisions, use [grill-with-docs](grill-with-docs.md), which also calls it.

## Plan evaluation

The planner inspects existing patterns, resolves consequential uncertainty, and checks the proposed approach against the outcome, interfaces, risks and verification. A material issue found in review sends the plan back for revision. Assumptions remain visible in the final proposal.

## Common questions

**Does it implement the feature?**

No. It produces a plan; use [implement](implement.md) for authorized implementation after the appropriate readiness check.

**Does it replace design?**

No. Use [design](design.md) when a consequential UI, architecture, module or data-model choice needs specialist collaboration.

## It's working if

- The plan identifies the outcome, affected behavior, verification and relevant risks.
- Consequential assumptions and unresolved input are visible rather than silently treated as decisions.
- The proposed approach fits the existing code and avoids unnecessary work.

## Where it fits

`feature-planner` is available as a standalone planning skill and is called at the start of [grill-with-docs](grill-with-docs.md). [guide-me](guide-me.md) maps the broader workflow.
