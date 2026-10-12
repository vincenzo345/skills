# Evolving an existing model

Inspect the current schema, migration convention, active readers and writers, and permitted representative data. Separate what constraints claim from what existing records satisfy. Mark uninspected data assumptions explicitly.

Describe the transition in terms of:

- **Mapping:** how old identities, values, and relationships become the new representation; flag ambiguous records, duplicate keys, and missing references instead of silently assigning meaning.
- **Compatibility:** whether old and new application versions coexist, and how each reads and writes during the transition. If coordinated downtime is acceptable, a simpler transition may be appropriate.
- **Conversion:** ordering, batching or restart needs, reconciliation, and any interval of dual representation. Define the authoritative copy during that interval.
- **Verification:** checks that establish the intended invariants and consumer behavior after conversion. Row counts alone do not prove relationships or meaning survived.
- **Recovery and retirement:** how to stop or recover from a partial conversion, which transformations lose information, and when obsolete representations can be removed.

Use the repository's established migration tooling. A design handoff can include proposed DDL or mapping examples, clearly labeled as unexecuted. Execute production conversion only as separately authorized implementation work.
