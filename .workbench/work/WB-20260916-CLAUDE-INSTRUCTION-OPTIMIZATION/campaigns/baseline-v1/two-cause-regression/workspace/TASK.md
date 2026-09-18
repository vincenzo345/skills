# Two-cause key normalization regression

Configuration keys must be case-insensitive and treat hyphens and underscores equivalently across mapping and environment inputs.

Completion criteria:

- `normalize_key` lowercases and converts `-` to `_`.
- `load_mapping(mapping)` normalizes every mapping key.
- `load_environment(environment, prefix="APP_")` strips the prefix and applies the same normalization.
- Ignore environment entries outside the requested prefix and preserve values unchanged.
