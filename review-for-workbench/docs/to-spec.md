Quickstart:

```bash
npx skills add mattpocock/skills --skill to-spec --skill delivery-proof
```

[Source](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec)

## What it does

`to-spec` synthesizes the existing conversation and repository evidence without starting a new interview. It publishes a spec as `draft`, `blocked`, or `ready`. A ready spec routes to `to-tickets` with `ready-for-tickets`; `ready-for-agent` is reserved for executable implementation tickets.

The spec uses stable IDs for outcomes, stories, invariants, acceptance criteria, decisions, dependencies, and delivery obligations. Every criterion names its required proof level, target environment, public journey or seam, independent oracle, expected nonzero population, procedure, and evidence artifact. Each outcome has a criterion that observes it where users or consuming systems experience it; available local access does not lower the required proof.

## Readiness

Unresolved choices remain visible rather than being guessed. Rollout, compatibility/parity, cutover, rollback, data/access needs, and human validation are included where relevant. End-to-end traceability ensures no desired outcome or obligation disappears between planning sections.

Use it after informed discovery or Wayfinder and before `to-tickets`.
