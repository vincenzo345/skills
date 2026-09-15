Quickstart:

```bash
npx skills add mattpocock/skills --skill wayfinder --skill grilling --skill domain-modeling --skill research --skill prototype --skill delivery-proof
```

[Source](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder)

## What it does

`wayfinder` maps an effort too large and foggy for one session as decision tickets on the configured tracker. It resolves one non-research ticket per session and produces decisions and owned delivery obligations, not implementation.

## Two destinations

The map separates the real **desired outcome** from its **planning destination**, normally a ready spec handoff. This prevents a completed decision map from being mistaken for a delivered result.

Every user-owned consequential resolution records whether it was confirmed or explicitly delegated; only factual questions may resolve from evidence alone. Confused acknowledgements do not close tickets, and missing facts produce an open `evidence-blocked` state. Necessary downstream work becomes a stable `OBL-*` obligation with an owner and discharge condition.

## Handoff

Before handing off to `to-spec`, Wayfinder audits outcome traceability, decision provenance, exclusions, fog, and obligations through `delivery-proof`. An item is out of scope only if the desired outcome remains achievable without it or it is carried by another owned effort.
