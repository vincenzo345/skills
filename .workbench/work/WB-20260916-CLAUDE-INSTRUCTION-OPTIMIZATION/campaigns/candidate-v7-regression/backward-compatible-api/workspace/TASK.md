# Backward-compatible API extension

Extend `labels.format_label` with an optional keyword-only `prefix` without breaking existing callers.

Completion criteria:

- Existing calls `format_label(name)` and `format_label(name, uppercase)` retain their behavior.
- `format_label(name, uppercase, prefix="...")` prepends the prefix before case conversion.
- `prefix` cannot be supplied as a third positional argument.
- The default prefix is an empty string.
