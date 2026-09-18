# Configuration precedence

Fix `config_loader.load_config(keys, cli, environment, file_values, defaults)`.

Completion criteria:

- Resolve each key in this order: CLI, environment, file, default.
- Presence, not truthiness, selects a value; `False`, `0`, and an empty string are explicit values.
- Missing keys resolve to `None` when absent from every source.
- Do not mutate any source mapping.
