# Cross-file symbol rename

Introduce the preferred public name `to_slug` for the existing `slugify` behavior and update the small integration surface.

Completion criteria:

- `slug.to_slug` implements the existing slug conversion.
- `slug.slugify` remains as a backward-compatible alias.
- `api.make_slug` calls the preferred name.
- `registry.CALLS` registers the behavior under key `"to_slug"` with no stale `"slugify"` key.
