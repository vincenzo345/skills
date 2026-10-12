## What it does

`datamodel-design` designs how information is represented and preserved through changes. Its organizing idea is data integrity: the model must explain which states are valid and how real operations maintain them. It uses the established business meanings and can remain a logical model until storage decisions are justified.

## When to reach for it

Type `/datamodel-design`, or the agent reaches for it when a task fits. It is also the data-model branch of [design](design.md).

| Situation | What it helps decide |
|---|---|
| New or confusing schema | Identity, relationships, constraints, and physical representation |
| Results must remain understandable after corrections | Required history and input provenance |
| A populated model needs to change | Conversion, compatibility, verification, and recovery implications |

Use [domain-modeling](domain-modeling.md) to settle what business concepts mean. Use architecture design for system ownership, and [codebase-design](codebase-design.md) for module interfaces.

## The model must survive operations

A diagram is a starting point. The agent walks concrete records through normal operations and relevant invalid states, including concurrency where an invariant can race. The result explains enforcement and remaining uncertainty, rather than presenting field declarations as a complete design.

## Common questions

**How is this different from domain modeling?**

Domain modeling establishes the meaning of a Case, Scenario, or recommendation. Data model design establishes their identities, references, constraints, and how recorded results survive later changes. Missing business meaning returns to the human; a convenient schema does not decide it.

**Does every model need immutable revisions?**

No. A simple current-state application can use mutable records. History is selected for a concrete requirement, such as retaining the exact analysis a presentation used. The skill distinguishes a new business object from a revision of an existing object.

**Does it run migrations?**

It designs the transition and can propose schema or mapping examples. Production conversion is implementation work with its own authorization and verification.

## It's working if

- You can trace representative records through changes and explain why the relationships remain valid.
- Every important rule names how it is enforced, or clearly identifies an unresolved gap.
- History choices answer a real future query and include the inputs that query needs.
- Existing-data ambiguity and compatibility costs are visible before implementation.

## Where it fits

This is a specialist subskill of [design](design.md), packaged independently so other workflows can reuse its discipline. [Prototype](prototype.md) can test a bounded uncertainty. [Guide-me](guide-me.md) routes broader requests to the appropriate workflow.
