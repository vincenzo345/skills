# Business ontology map format

`docs/ontology/graph.json` is a versioned JSON object with `version`, `nodes`, and `edges`. A proposal uses the same shape at `docs/ontology/graph.proposed.json`. It describes business meaning, not a database schema. It contains no application records.

`nodes` is an object keyed by canonical business concept name. The key is the reference used by edges; there is no generated ID. Each node has `kind` (`entity`, `value_object`, `process`, or `concept`), `description`, `attributes`, `sources`, and `review` (`proposed` or `confirmed`). `attributes` is an object keyed by business attribute name; each value has a description. Optional `rules` lists business invariants or lifecycle rules. Sources are repository-relative paths. Do not put table names, database columns, or joins in a node.

`edges` is a list of relationships between concepts. Each has `from`, `to`, `type`, `description`, `sources`, and `review`. Optional `cardinality`, `conditions`, and `rules` express business constraints, not database constraints. A join table generally becomes a relationship, perhaps with attributes or rules, rather than its own concept. Do not infer an `is_a` edge from a database type discriminator alone.

When implementation navigation matters, use a separate `docs/ontology/implementation-bindings.json`, or `.proposed.json` during review. Its `concepts` object maps each business concept to one or more storage models with `table` and `sources`. Its `relationships` list records a graph edge reference (`from`, `type`, `to`) and one or more `joins`, each naming `from_table`, `from_field`, `to_table`, `to_field`, `constraint`, and `sources`. Multiple storage models can represent one business concept. A binding can be incomplete; do not manufacture a join to fill a gap.

Example:

```json
{
  "version": 1,
  "nodes": {
    "InsuranceIllustration": {
      "kind": "entity",
      "description": "A carrier's proposed policy design for a client need.",
      "attributes": {"processingStatus": {"description": "Whether its source document has been processed."}},
      "sources": ["backend/app/db/models/illustration.py"],
      "review": "proposed"
    },
    "Case": {
      "kind": "entity",
      "description": "A client engagement organized around an insurance need.",
      "attributes": {},
      "sources": ["backend/app/db/models/case.py"],
      "review": "proposed"
    }
  },
  "edges": [{
    "from": "InsuranceIllustration",
    "to": "Case",
    "type": "considered_in",
    "description": "The case considers the proposed design.",
    "sources": ["backend/app/services/case_service.py"],
    "review": "proposed"
  }]
}
```
