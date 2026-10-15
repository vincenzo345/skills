## What it does

`ontology-map` reads and maintains a reviewed JSON map of an application's business concepts, attributes, rules, and relationships. It gives an agent the relevant neighborhood when a task names an entity or relationship. The map contains no application records, and proposed changes do not become accepted until the user reviews them.

## When to reach for it

Type `/ontology-map`, or the agent reaches for it automatically when a task depends on business entities or relationships. Use it to draft the first map, inspect an existing one, or propose changes after scope, design, or implementation work.

## Prerequisites

The accepted map lives at `docs/ontology/graph.json` in the application repo. The skill can draft the first proposal when no map exists. Its Python helper validates the JSON and retrieves a bounded neighborhood without a graph database.

## The review boundary

The graph's nodes name business concepts. Edges describe business relationships and rules. Source paths point to scope, glossary entries, accepted decisions, or code. A separate optional implementation bindings file records tables and join fields when code navigation needs them. Two tables can implement one business concept.

`docs/ontology/graph.proposed.json` is a candidate, not the accepted map. The user reviews proposed nodes and edges before they move into `graph.json`. During [to-scope](to-scope.md), inferred workflow statements can suggest changes, while expert corrections carry stronger evidence.

## Common questions

**Does this replace the glossary or ADRs?**

No. The [domain-modeling](domain-modeling.md) glossary settles words, and ADRs explain consequential decisions. The ontology map connects those concepts through relationships and rules so an agent can retrieve the relevant context for a task.

**Can a table become a node?**

Only when it also represents a genuine business concept. Table mappings belong in the separate implementation bindings file.

## It's working if

- A task about a domain concept retrieves its adjacent relationships before design or code changes.
- A proposed edge shows its business meaning, source, and review status.
- Conflicts with code or an ADR are reported to the user rather than quietly flattened.

## Where it fits

`ontology-map` is a model-invoked reference and maintenance skill that can run at any stage. [To-scope](to-scope.md) uses it to surface possible changes from expert review, while [guide-me](guide-me.md) points to it when domain relationships are the question.
