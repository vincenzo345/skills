# Unicode username matching

Fix `users.find_user(query, users)` so matching is Unicode-aware while returning the original display spelling.

Completion criteria:

- Normalize usernames with Unicode NFKC normalization and case-insensitive `casefold()` semantics.
- Composed and decomposed spellings compare equally.
- Return the original string from `users`, or `None` when no user matches.
- Keep the existing function names and parameters.
