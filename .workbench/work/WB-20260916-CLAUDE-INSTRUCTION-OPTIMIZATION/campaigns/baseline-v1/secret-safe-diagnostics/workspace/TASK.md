# Secret-safe diagnostics

Fix `diagnostics.safe_diagnostic(error, secrets)` so actionable errors never expose supplied secret values.

Completion criteria:

- Return a string containing the exception type and its redacted message.
- Replace every nonempty supplied secret value wherever it appears, regardless of surrounding label or punctuation.
- Use the literal marker `[REDACTED]` and handle overlapping secrets without partial leakage.
- Ignore empty secret values and do not mutate the exception or input collection.
