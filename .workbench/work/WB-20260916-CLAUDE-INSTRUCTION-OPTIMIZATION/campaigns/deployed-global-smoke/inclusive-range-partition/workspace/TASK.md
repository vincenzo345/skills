# Inclusive range partition

Fix `ranges.partition(start, end, size)` so it partitions the inclusive integer range from `start` through `end` into ordered inclusive `(chunk_start, chunk_end)` pairs.

Completion criteria:

- Every integer in the requested range appears exactly once.
- Empty ranges return an empty list.
- Singleton, exact-size, and remainder ranges work.
- A non-positive size raises `ValueError`.
- Keep the existing public function name and parameters.
