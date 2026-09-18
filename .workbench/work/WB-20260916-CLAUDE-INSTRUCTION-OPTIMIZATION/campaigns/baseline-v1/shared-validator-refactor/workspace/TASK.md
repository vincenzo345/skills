# Shared validator refactor

Refactor the duplicated email normalization in `user_models.py` and `admin_models.py` into `validators.py` without changing the public creation functions.

Completion criteria:

- Define one shared `validators.normalize_email(value)` implementation that trims surrounding whitespace and lowercases the address.
- Both `create_user` and `create_admin` import and use that shared implementation.
- Keep both public function names and their dictionary result shapes.
- Remove the duplicated local normalization definitions.
