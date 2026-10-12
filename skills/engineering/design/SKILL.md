---
name: design
description: Design a UI, system architecture, codebase module, or data model with the human. Use for blank-canvas design, redesign, or unresolved structural choices; reuse established decisions and involve the human in consequential tradeoffs. Use prototype for a bounded runnable experiment and review skills for assessing existing work.
---

# Design

Own the design conversation from the desired outcome to a workable, evidence-backed direction. The agent investigates and recommends; the human supplies intent, priorities, and judgments that evidence cannot settle. Scale collaboration to the decision rather than requiring approval for routine details.

## Choose the branch

Read only the branch needed for the current question:

| Design question | Branch |
|---|---|
| What should a person see and do to accomplish their work? | [UI.md](UI.md) |
| How should the system divide responsibilities and meet operational constraints? | [ARCHITECTURE.md](ARCHITECTURE.md) |
| How should data identity, relationships, integrity, and history be represented? | [DATAMODEL.md](DATAMODEL.md), using `datamodel-design` |
| What should a module expose, hide, and make testable? | [CODEBASE.md](CODEBASE.md), using the existing `codebase-design` skill |

Module design and codebase design are the same branch. A task may cross branches: resolve the specific dependency in the relevant branch, carry the answer back, and preserve the other settled decisions. A broad repo review belongs to a review or audit workflow; use design once there is a concrete problem or decision to address.

## Work with the human

1. **Establish the decision.** Read the request, existing application or code, relevant workflow documents, and previous decisions. Name the outcome and scope. Distinguish facts, accepted constraints, assumptions, and open decisions. Reuse confirmed answers; ask only for missing intent or a choice that affects the next activity. A prior `grill-with-docs` session can supply this input, but is not a prerequisite.
2. **Make choices concrete.** Follow the branch's method to expose the next consequential choice using sketches, examples, diagrams, or alternative interfaces. Explain the tradeoffs and give a recommendation. Ask the human about preferences, priorities, behavior, or costs the evidence cannot settle. Wait for that answer before proceeding with dependent decisions; continue independent investigation while waiting. Honor explicit delegation of routine or broader decisions.
3. **Evaluate and revise.** Walk representative tasks or failure scenarios through the design. Use a focused prototype only when runnable evidence can resolve a stated uncertainty. Load `prototype` through the available skill mechanism, or read its installed SKILL.md when there is no invocation tool. Give it the question, accepted decisions, fixtures, and observations needed. Bring the findings back into this design conversation; successful execution alone is not human acceptance.
4. **Hand off the result.** Keep a compact record using the project's existing decision-document convention: outcome, evidence, chosen design and rationale, rejected alternatives, open questions, and how the design was evaluated. Update only affected decisions after feedback and say what changed. Finish when the selected scope has a coherent direction supported by the required human decisions, and remaining implementation assumptions or blockers are explicit. Use an ADR only when the decision warrants one.

`grill-with-docs` remains a standalone general interview with domain documentation. Design owns this task's specialist method and uses focused clarification within it. A consequential domain change should be reflected in the existing domain record; it does not restart the entire design session. If the human is unavailable for a required decision, report the concrete choice and leave dependent work open instead of treating silence as agreement.

Design does not automatically authorize production implementation or publication. Hand over the result and the next activity within the user's requested scope.
