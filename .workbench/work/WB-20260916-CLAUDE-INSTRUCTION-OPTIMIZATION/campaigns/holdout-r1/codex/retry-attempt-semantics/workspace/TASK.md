# Bounded retry semantics

Fix `retrying.run_with_retries(operation, max_attempts)`.

Completion criteria:

- `max_attempts` is the total number of permitted calls, not the number of retries after the first call.
- Return immediately with the first successful operation result.
- Retry only `TransientError`; after the final permitted transient failure, re-raise that exact exception.
- Propagate every other exception immediately without retrying it.
- Reject non-positive `max_attempts` with `ValueError` before calling the operation.
