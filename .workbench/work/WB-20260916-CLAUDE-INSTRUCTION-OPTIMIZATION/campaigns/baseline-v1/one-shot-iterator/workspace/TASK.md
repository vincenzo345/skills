# One-shot iterator support

Fix `batch.describe(values)` so it works identically for lists and one-shot iterators.

Completion criteria:

- Return `{"count": N, "total": T}` for every finite iterable of numbers.
- Lists, generators, and empty iterables behave identically.
- Iterate the supplied iterable only once.
- Preserve exceptions raised by the iterable.
