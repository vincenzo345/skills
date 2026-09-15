Quickstart:

```bash
npx skills add mattpocock/skills --skill grilling
```

[Source](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)

## What it does

`grilling` stress-tests a plan one informed choice at a time. It investigates discoverable facts first, then classifies each open item as delegable, user-owned, or evidence-blocked.

For a consequential question it explains the decision, gives a concrete example, compares options and consequences, states reversibility and unknowns, and gives a conditional recommendation last.

## Confusion is not consent

If you say you do not understand and ask the agent to choose, that response cannot also approve or delegate the choice. The agent must simplify or gather evidence first. Confirmation or bounded delegation happens in a later response, followed by a consequence receipt that states what was selected, what trade-off was accepted, and how it can be reversed. A user-owned choice becomes settled only after you explicitly affirm that receipt.

## Completion

The session ends when every consequential item is confirmed, explicitly delegated, or visibly evidence-blocked with an owner and next step. It does not implement the resulting plan without separate authorization.
