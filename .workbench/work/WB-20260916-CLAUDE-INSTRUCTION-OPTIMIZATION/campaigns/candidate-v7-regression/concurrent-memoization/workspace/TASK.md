# Concurrent memoization

Fix `memo.Memo.get(key, compute)` so concurrent callers for the same missing key share one computation.

Completion criteria:

- Concurrent callers for one key all receive the same value from exactly one `compute()` call.
- Cached calls do not recompute.
- Different `Memo` instances remain independent.
- A failed computation is propagated and does not poison future retries.
