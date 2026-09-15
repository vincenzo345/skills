Quickstart:

```bash
npx skills add mattpocock/skills --skill to-tickets --skill delivery-proof --skill grilling
```

[Source](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets)

## What it does

`to-tickets` converts a ready spec into tracer-bullet vertical slices. It first builds a ledger of every source requirement, decision, dependency, and obligation, then persists a source-to-ticket-to-proof coverage matrix using the configured tracker.

Each ticket cites unchanged source criteria, states what it delivers and discharges, separates start blockers from later verification dependencies, and carries a full proof contract. If implementation slices do not prove the complete user journey, the skill creates a final outcome-verification ticket.

Draft or blocked specs do not become agent-ready tickets, and source criteria cannot be weakened during slicing. Deployment, data, access, and human validation are owned work rather than invisible footnotes.
