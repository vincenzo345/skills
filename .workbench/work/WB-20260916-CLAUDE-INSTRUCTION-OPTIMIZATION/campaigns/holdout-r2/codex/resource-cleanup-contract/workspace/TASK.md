# Resource cleanup contract

Fix `resources.read_payload(opener, path)` so the handle returned by `opener(path)` is always closed after it is opened.

Completion criteria:

- Return the exact result of `handle.read()` on success.
- Close the handle exactly once after either a successful read or a read failure.
- Preserve the original exception raised by `read()`; do not replace or swallow it.
- If `opener` itself fails, propagate that exception without attempting cleanup.
- Do not assume the returned handle implements a context manager.
