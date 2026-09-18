# Atomic settings write

Fix `settings.save_settings(path, data, replace=os.replace)` so an interrupted replacement cannot corrupt the existing file.

Completion criteria:

- Write valid JSON to a temporary file in the destination directory, then atomically call the injected `replace(temp, destination)` function.
- A successful call replaces the destination with the new data.
- If writing or replacement fails, preserve the old destination and remove task-owned temporary files.
- Propagate the original failure and keep the injectable `replace` parameter.
