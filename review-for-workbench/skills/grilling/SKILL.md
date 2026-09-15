---
name: grilling
description: Stress-test a plan, decision, or idea through an informed, one-question-at-a-time interview. Use when the user asks to be grilled or when another skill must resolve consequential choices without turning recommendations into accidental consent.
---

# Grilling

Interview the user until the consequential choices, trade-offs, and completion conditions are understood. Ask one question at a time and wait for the answer before continuing.

## Investigate before asking

Explore the environment for facts instead of making the user guess. Separate each open item into one of three states:

- **Delegable** — the user may explicitly authorize the agent to choose within stated bounds.
- **User-owned** — only the user can accept a business, product, legal, financial, security, privacy/data, publication/trust, material operational-cost, destructive-migration, or otherwise hard-to-reverse consequence.
- **Evidence-blocked** — neither party should choose until a fact, experiment, or outside decision is obtained.

Route evidence-blocked items to research, a prototype, a task, or a clearly named blocker. Do not disguise missing evidence as a preference question.

## Make each choice understandable

For a consequential question, present in this order:

1. the decision in plain language;
2. why it matters now;
3. one concrete example;
4. viable options and the consequence of each;
5. important unknowns and how reversible each option is;
6. a conditional recommendation last, with confidence and the assumptions it depends on.

Offer legitimate ways to continue: choose, explicitly delegate within bounds, defer, request more evidence, or ask for a simpler explanation. Do not use a recommendation-first question or treat a one-word agreement as informed merely because it matched the recommendation.

## Confusion overrides apparent consent

If the user says they do not understand, asks to "just go with the recommendation," or otherwise signals confusion, that same response cannot confirm the choice or delegate it. Explain it more simply, use a different example, or gather the missing evidence. Confirmation or explicit delegation must happen in a later response after the consequence is clear.

## Record a consequence receipt

Before treating a user-owned or consequential delegated choice as settled, restate:

- the option selected;
- the main consequence accepted;
- the important alternative declined;
- the remaining uncertainty and rollback path;
- whether the user chose it or explicitly delegated it.

Ask directly whether this is the consequence intended and wait. A user-owned decision becomes confirmed only after an explicit affirmative response to the receipt. Silence, a topic change, delivery of the receipt, an assumption, or an assistant recommendation is not confirmation.

Finish only when the observable planning destination is met: every consequential item is confirmed, explicitly delegated, or visibly evidence-blocked with a next step. Do not implement the resulting plan unless the user separately authorizes implementation.
