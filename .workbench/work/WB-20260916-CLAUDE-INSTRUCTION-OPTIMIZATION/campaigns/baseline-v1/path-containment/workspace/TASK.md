# Path containment

Fix `paths.is_within(root, candidate)` so it checks resolved filesystem containment rather than text prefixes.

Completion criteria:

- Return true for the root itself and normal descendants.
- Return false for parents, sibling-prefix paths, and `..` escapes.
- Resolve symlinks before deciding when the platform permits symlink creation.
- Accept strings or path-like values and remain cross-platform.
