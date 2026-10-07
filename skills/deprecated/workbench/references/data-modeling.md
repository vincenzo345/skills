# Data-model design

Use this reference when routing or executing software work in an application that uses a database or other durable store. The objective is an explicit, reviewable persistence design—not a mandatory diagram or document.

## Route every software application explicitly

Inspect the repository and record a `data-model-design` stage recommendation for every greenfield or brownfield software profile:

- `applicable` when the application introduces a durable store or the work changes persisted concepts, relationships, invariants, ownership, lifecycle, access patterns, or migration behavior;
- `not-applicable` only when evidence shows that persistence semantics are unaffected; state what was inspected and why no data-model work is required; or
- `undetermined` when the impact cannot yet be established. Material uncertainty blocks dependent specification or implementation work.

At a proposal-only destination, a bounded deferral may be `not-applicable` for that destination, with re-evaluation required before a software specification or implementation destination.

## Produce the smallest sufficient model

One canonical artifact may combine schema definitions, ORM models, migrations, diagrams, and concise design notes. It is sufficient when a reviewer can determine:

- domain concepts, stable identities, ownership, tenancy, relationships, cardinality, and optionality;
- invariants and which layer enforces each one, favoring database constraints for persistent truths;
- state transitions, temporal history, deletion, retention, archival, and audit needs;
- transaction boundaries, concurrency behavior, idempotency, and consistency expectations;
- expected access patterns, representative queries, indexes, volume, growth, and hot paths;
- classification of sensitive data, authorization boundaries, encryption, and isolation;
- compatibility, migration, backfill, rollout, rollback or forward-recovery, and mixed-version behavior; and
- rejected alternatives, consequential decisions, assumptions, and unresolved obligations.

Use conceptual and logical modeling before physical tuning when the domain is unsettled. For a small change to a well-understood schema, an evidenced no-impact disposition or a migration plus focused notes may be enough.

## Gates and proof

The `data-model-disposition-recorded` exit gate requires either an evidence-backed no-impact disposition or a current `data-model` artifact with its material decisions and obligations. Specification and implementation inputs must reference that disposition when the activity is applicable.

Verification follows the actual risk. Check applicable constraints, migrations and backfills, rollback or forward recovery, tenant isolation and authorization, representative queries and indexes, lifecycle behavior, concurrency, and failure handling. Passing application tests alone does not prove migration safety or persistent invariants that those tests do not exercise.
