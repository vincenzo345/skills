## What it does

`design` owns a design conversation from an outcome to a workable direction. It combines investigation and concrete alternatives with human decisions about intent, priorities, and tradeoffs. The amount of collaboration follows the decision: a UI can need frequent sketch reviews, while an internal module can rely mostly on established conventions.

## When to reach for it

Type `/design`, or the agent reaches for it automatically when the task fits. Use it when structure or experience is unsettled. An existing design ready to build belongs to implementation; a request to assess a repo belongs to a review workflow until a concrete design problem is identified.

| Question | Branch |
|---|---|
| What should people see and do? | UI: sketches, hierarchy, navigation, and task walkthroughs |
| How should the system divide responsibilities and operate? | Architecture: constraints, alternatives, ownership, failures, and migration |
| How should data be represented and preserved? | [Data model design](datamodel-design.md): identity, relationships, integrity, history, and evolution |
| What should a module expose and hide? | Codebase design: the existing module discipline and vocabulary |

## Decisions accumulate

The agent brings evidence and a recommendation. You choose where the answer depends on your priorities or judgment. Accepted decisions carry forward, and feedback changes the affected part. When a question needs runnable evidence, [prototype](prototype.md) builds an experiment and returns the findings to the design conversation.

Proposals, evidence and useful reasoning stay in the existing effort. Accepted current architecture, module and data-model knowledge belongs in the configured maintained documents, linked back to that evidence and discoverable through the short knowledge index. The handoff distinguishes proposed intent, accepted choices and implemented behavior; it links glossary and schema authority rather than copying them.

## Common questions

**Where does grill-with-docs end and design begin?**

[Grill-with-docs](grill-with-docs.md) is a general interview that records domain understanding. It can establish the work before design starts. Design then owns the specialist method, including any focused clarification it needs. You can enter design directly when the task and its constraints are already clear.

**Is module design different from codebase-design?**

They are the same branch. Design loads the existing [codebase-design](codebase-design.md) guidance, so its vocabulary and principles have one source. Existing callers can still use that skill directly.

**Will every design require a long interview?**

No. Confirmed decisions and routine conventions are reused. Your input is needed for consequential choices the evidence cannot settle, and you can delegate those choices explicitly.

## It's working if

- You can see what decision is being made and why it matters before being asked to choose.
- Each iteration retains accepted choices and explains the specific change.
- A sketch, diagram, or usage example makes the tradeoff concrete.
- The result records chosen tradeoffs, evidence, and remaining uncertainty clearly enough for the next activity.
- Accepted current knowledge is findable from the existing index, while plans, proposals and prior reasoning remain at stable effort paths.

## Where it fits

Design is a standalone workflow with four specialized branches. [Prototype](prototype.md) supplies runnable experiments; [codebase-design](codebase-design.md) supplies module principles, and [datamodel-design](datamodel-design.md) supplies data representation and integrity principles. [Guide-me](guide-me.md) routes you here when a design task needs this process.
