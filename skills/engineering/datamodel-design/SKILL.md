---
name: datamodel-design
description: Design logical and physical data models with explicit identity, relationships, constraints, and lifecycle semantics. Use for schema design, history and provenance decisions, or schema evolution planning; serves the data-model branch of design. Domain-modeling owns business meaning; migration execution belongs to implementation.
---

# Data Model Design

Design for **data integrity**: the stored representation preserves the meaning and rules of the work as records are created, changed, related, and removed. Use established domain language and realistic operations to judge the model. The goal is a model whose valid states, source of truth, and evolution are explicit.

This is the specialist discipline used by `design`; it can also be used directly. Follow the project's accepted decisions. Investigate existing schemas, migrations, queries, and representative data before proposing changes. Present consequential alternatives to the human with a recommendation; wait for unresolved business semantics or tradeoffs before designing dependent structures. Routine schema details can follow established conventions.

## Glossary

**Entity**: a domain thing with an identity that persists across changes. An entity need not correspond to exactly one table or document.

**Identity**: the rule for recognizing the same entity over time. Distinguish an internal key from a changeable display value or an external identifier, including the scope in which each is unique.

**Relationship**: an association between entities, with explicit cardinality, optionality, and lifecycle behavior. Storage ownership and authorization are separate questions from association.

**Invariant**: a rule that must hold in every committed state, or at a specifically defined consistency boundary. State the enforcement mechanism and any period in which a weaker condition is allowed.

**Logical model**: entities, attributes, relationships, and constraints expressed independently of a particular storage engine.

**Physical model**: the chosen representation in tables, documents, keys, constraints, indexes, and other storage structures supporting actual reads and writes.

**Source of truth**: the authoritative representation of a fact. A derived representation needs an update or rebuild rule and a defined tolerance for staleness.

**Revision**: an identifiable state of an entity retained for a stated purpose. Distinguish entity identity from revision identity; versioning is a requirement-driven choice.

**Provenance**: the retained relationship between a result and the inputs and transformations that produced it. A timestamp alone does not identify those inputs.

**Migration**: a transition from one stored representation to another, including existing data and readers and writers active during the transition.

## Logical vs physical

Start with the rule and operations that must hold, then choose their storage representation:

```text
Requirement: a person's membership is unique within a workspace
Logical:     Workspace 1 -> many Memberships many <- 1 Person
Physical:    membership(workspace_id, person_id, role)
Constraint:  unique(workspace_id, person_id), plus relationship integrity
```

Use the actual storage engine's capabilities when specifying enforcement. Confirm uncertain engine behavior from its documentation or an isolated experiment. Inspect the current implementation, but distinguish existing behavior from the intended rule.

For each important relationship, ask:

- Which identities does it connect, and can either end be absent or repeated?
- What happens when either end changes, is merged, or is removed?
- Which write preserves the invariant, including concurrent or repeated requests?
- Which reads require the current value, a historical value, or an explicitly derived view?

## Principles

- **Model the rule before the storage convenience.** Resolve ambiguous domain meaning through the existing domain record and the human. UI layout and ORM defaults do not establish entity identity or ownership.
- **Make invalid states detectable and preventable.** For each invariant, name its enforcement point: a storage constraint, transaction, conditional write, application rule, or reconciliation process. An application check followed by a write requires a concurrency strategy when the invariant can race.
- **State scope explicitly.** Identify whether keys, uniqueness, and references are global, per account, or per tenant where applicable. Scoped integrity does not by itself provide authorization.
- **Keep facts authoritative.** Prefer one authoritative fact; introduce duplication or derived views for a demonstrated access need, with update, consistency, and rebuild behavior. Choose normalization or embedding from relationship semantics and access patterns rather than a universal storage preference.
- **Preserve the history the work requires.** Separate correction, new business work, and revision where their meanings differ. Retain snapshots, immutable revisions, or events only when required; simple mutable records are valid when prior values have no required use.
- **Define absence and deletion.** Distinguish unknown, not applicable, empty, and zero where the domain does. Choose deletion, archival, reference behavior, and retention from actual requirements. Soft deletion alone does not settle history or retention.
- **Make the physical design earn its complexity.** Base indexes, partitioning, and denormalization on representative queries, write rates, and measured or explicitly assumed scale. Keep unmeasured performance claims provisional.

## Designing for integrity

Evaluate a model with concrete records and operations, not only an entity diagram:

1. **Trace a normal lifecycle.** Show a representative create, read, update, and removal or archival operation. Include the important repeat cycle when one exists. For example, a new request might create a new Scenario while preserving the prior Scenario; it is not automatically a revision of the same entity.
2. **Try to violate a rule.** Use duplicate identities, missing references, a disallowed cross-scope relationship, or concurrent updates as relevant. Explain which mechanism rejects or resolves the operation. Avoid adding unrelated edge cases just to fill a checklist.
3. **Check what a consumer sees later.** If a past decision must remain reproducible, follow its references after source correction. If only current state matters, show how consumers obtain that state without unnecessary history machinery.

The handoff contains the logical model, representative operations, identity and relationship rules, invariant enforcement, and open semantic decisions. Add a physical schema and access-path rationale when the engine and workload are established; otherwise mark those choices open. For an existing model, include compatibility and data-conversion implications. Writing a design does not execute a production migration.

## Relationships

- An **Entity** has an **Identity**; a retained **Revision** identifies a particular state of that entity.
- A **Relationship** connects identities or specific revisions according to its meaning.
- An **Invariant** constrains committed states and transitions; the **Physical model** supplies some of its enforcement mechanisms.
- A **Logical model** can have different physical representations with different operational costs.
- **Provenance** connects results to their source facts or retained input states.
- A **Migration** must account for both stored records and their active consumers.

## Rejected framings

- **One screen equals one entity**: derive entities from identity and lifecycle; screens may combine many entities.
- **An ORM type is the complete model**: include cross-record constraints, history semantics, and concurrency behavior that field declarations omit.
- **Every entity needs revisions or event sourcing**: choose historical representation from actual retrieval, audit, or reproducibility needs.
- **Every schema change is only DDL**: existing values and reader/writer compatibility can determine whether the transition is workable.

## Going deeper

- **History, corrections, and reproducible results:** read [HISTORY.md](HISTORY.md) when consumers must retain or reconstruct a past state.
- **Changing a populated schema:** read [EVOLUTION.md](EVOLUTION.md) when existing records or active consumers must survive a representation change.
