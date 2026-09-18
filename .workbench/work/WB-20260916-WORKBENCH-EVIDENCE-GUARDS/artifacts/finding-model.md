# Typed finding model

`findings[]` accepts either a legacy string or a typed object:

```json
{
  "statement": "Observed statement",
  "basis": "fact | measurement | hypothesis | inference",
  "source_references": []
}
```

- `fact` and `measurement` require at least one resolvable source reference and project as `evidence-established` using only those references.
- `hypothesis` and `inference` may cite contextual sources but project as `draft` with an explicit next action to gather discriminating evidence.
- A legacy string remains schema-valid for replay/producer compatibility and projects as an untyped `draft`, never as established evidence.
- No existing persisted map, event, or handoff is rewritten.

This is intentionally not a causal-proof framework. Classification prevents accidental promotion; the two conformance cases define the behavioral threshold for root-cause language.
