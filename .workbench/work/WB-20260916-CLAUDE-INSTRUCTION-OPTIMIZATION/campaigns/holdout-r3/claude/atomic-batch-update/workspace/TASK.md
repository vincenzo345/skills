# Atomic batch update

Fix `batch.apply_updates(state, updates, validate)`.

Completion criteria:

- Validate every `(key, value)` before changing `state`.
- If all values are valid, apply the updates and return the original `state` object.
- If validation raises, propagate the exact exception and leave `state` completely unchanged.
- Iterate `updates` only once; callers may provide a one-shot iterable.
- Preserve keys not named by an update.
