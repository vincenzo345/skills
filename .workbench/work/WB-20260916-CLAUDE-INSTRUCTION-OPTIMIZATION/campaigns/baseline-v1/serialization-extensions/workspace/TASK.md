# Serialization extension round trip

Fix `records.Record.from_dict` and `to_dict` so forward-compatible extension fields survive a round trip.

Completion criteria:

- `name` remains the required known field.
- Every unknown input field is preserved unchanged in `record.extensions`.
- `to_dict()` returns `name` plus all preserved extensions without mutating input data.
- An extension named `name` cannot override the record's known name.
