Quickstart:

```bash
npx skills add mattpocock/skills --skill delivery-proof
```

[Source](https://github.com/mattpocock/skills/tree/main/skills/engineering/delivery-proof)

## What it does

`delivery-proof` is the shared definition of truthful completion. It traces desired outcomes through specs, tickets, changes, and criterion-specific proof receipts.

It distinguishes four levels: `implemented`, `locally-verified`, `deployed-verified`, and `outcome-verified`. Each receipt records required and achieved level; a lower level never implies a higher one or pass a higher-level criterion.

## Why it exists

A green test suite can still be irrelevant, vacuous, self-derived, mocked at the wrong seam, or run in the wrong environment. This skill requires every criterion to name its environment, public journey, independent oracle, expected nonzero population, procedure, and artifact before work begins. Candidate, quarantined, staged, or rejected artifacts do not count as accepted output.

Wrong observed behavior is `failed`; missing deployment, access, data, or human validation is `blocked`. Acceptance criteria cannot be silently weakened during implementation or review.

## Where it fits

It is model-invoked beneath `wayfinder`, `to-spec`, `to-tickets`, `implement`, `tdd`, and `code-review`. Install the full collection for the integrated flow; when a phase skill is installed alone, its own local proof rules still apply.
