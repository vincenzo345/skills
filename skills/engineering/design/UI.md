# UI design

Take the established work as input and design the experience with the human. Shared understanding of the business workflow does not settle the interface. For a small change, use only the rounds needed; for a blank canvas, build the structure incrementally.

## Ground the design

Inspect the existing UI, workflow documents, realistic content, and prior findings. Identify the actor, entry trigger, work objects, handoffs, repeat cycles, and success state from that evidence. Treat confirmed rules as constraints. If an unresolved rule changes what work belongs where or what an action means, resolve that specific question before designing the dependent screen.

Show the human the relevant current screens and what could be retained. With no existing UI, start from a rough map of the work and candidate screens. A new visual direction still inherits the product's established behavior.

## Design in rounds

Work through choices whose prerequisites are settled, adjusting the order to the task:

- **Entry and screen map:** where work begins, which screens it needs, and how the user returns or resumes.
- **Information hierarchy:** what must be visible immediately, what establishes context, and which detail appears on demand.
- **Navigation and actions:** how the user selects work, enters an activity, moves between related information, and recognizes what an action affects.
- **Interaction states:** empty, pending, error, completed, repeat, and recovery states relevant to the task. Consider keyboard operation, focus, and accessible feedback as the interaction is shaped.
- **Visual direction:** density, typography, spacing, color, and component treatment in the real shell and with representative content.

For the current decision, show an annotated sketch or a small set of meaningful alternatives, explain the tradeoff, and recommend a direction. Ask the human to choose, combine, or correct it. Wait before building downstream choices on an unanswered decision. Record the choice and rationale. Use existing components and tokens where they fit; let the human judge consequential experience choices rather than every styling detail.

Walk representative tasks on the emerging wireframe: what the user sees, clicks, needs to remember, and can recover or repeat. Retain accepted choices between rounds. Reopen a choice explicitly when new evidence or human feedback warrants it, rather than replacing the whole design after each comment.

## Prototype and conclude

When an interaction or visual choice needs to be experienced, send that question to `prototype` with the selected structure, fixed constraints, representative tasks, and any alternatives still open. Rough runnable sketches are appropriate earlier when the human requests them or the question needs interaction; label unchosen assumptions. Keep comparison tasks and data constant, and vary the disputed choice.

Return for human evaluation. Separate observed navigation problems from preferences and from simulated backend behavior. When using multiple judges, record each person's task observations and keep the winner undecided until the agreed evaluation is complete.

The handoff includes the screen map or wireframes, accepted choices and reasons, task walkthrough findings, relevant states, and proposed reads, writes, permissions, validations, and backend gaps. The outcome is a workable design for the selected scope; production readiness and user validation claims require corresponding evidence.
