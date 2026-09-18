# CLI stream and exit semantics

Fix the executable `cli_app.py`, which squares one integer argument.

Completion criteria:

- A valid integer prints its square to stdout and exits 0.
- Invalid input prints a concise `error:` message to stderr, prints nothing to stdout, exits 2, and shows no traceback.
- `--quiet` suppresses successful stdout while retaining exit 0.
- Keep `main(argv)` directly testable and the script executable.
