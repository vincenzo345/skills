# Cache key completeness

Fix `render_cache.RenderCache.render(document, options, renderer)` so cached results respect every output-changing option.

Completion criteria:

- Calls with the same document and equivalent option mappings reuse one cached value.
- Calls whose options differ compute and cache separate values.
- Option key order does not change equivalence.
- Keep cache state private to each `RenderCache` instance.
