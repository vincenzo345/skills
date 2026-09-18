# Single-pass first match

Fix `matching.first_match(records, predicate)`.

Completion criteria:

- Return the first record for which `predicate(record)` is truthy.
- Return `None` when no record matches.
- Consume `records` at most once so one-shot iterators work.
- Call `predicate` exactly once for each inspected record and stop inspecting immediately after the first match.
- Do not materialize the entire iterable.
