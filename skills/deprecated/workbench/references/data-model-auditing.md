# Data-model auditing

Use this reference when the user asks to review or audit an existing data model. Read [data-modeling.md](data-modeling.md) as the governing persistence contract, then apply both audit lenses unless the user narrows the request.

## Two lenses

1. **Requirements fitness** — trace each material persisted requirement to the entity, field, relationship, invariant, or lifecycle representation that supports it; classify unsupported requirements and distinguish confirmed requirements from provisional ones.
2. **Intrinsic health** — evaluate the relevant existing tables and flows independently of new requirements: identity, ownership and tenancy, cardinality, nullability, constraints, state and history, deletion and retention, sensitive data, read/write paths, indexes and access patterns, ORM/schema drift, and migration safety.

Give each relevant table or aggregate one evidence-bounded disposition: `keep`, `keep-with-additions`, `rework`, `consolidate`, `retire`, or `unknown-pending-evidence`. State missing fields only when their requirement and grain are known. Treat row populations, active writers, and production behavior as unknown until inspected; a code-only audit may recommend containment but cannot safely select a destructive consolidation path.

Separate four claim types in the artifact and summary:

- observed facts with locators;
- inferences and the cheapest confirming check;
- proposed model changes and rejected alternatives; and
- consequential decisions with owner, dependency, and effect on the route.

Sequence recommendations by dependency. Isolate urgent containment from schema consolidation, then establish live usage and canonical ownership before designing migrations or extensions. A concise summary may lead with the dominant gaps, but it must also answer whether the existing model is healthy and link to the per-table dispositions.

When a follow-up materially extends an active audit, preserve it as a new versioned artifact or addendum under the same work item. Keep the registered predecessor immutable and link the new artifact through source lineage.
