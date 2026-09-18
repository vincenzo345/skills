import json
import os
import tempfile


def save_settings(path, data, *, replace=os.replace):
    directory = os.path.dirname(os.path.abspath(path))
    fd, temp_path = tempfile.mkstemp(
        prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=directory
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            json.dump(data, temp_file, sort_keys=True)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        replace(temp_path, path)
    except BaseException:
        try:
            os.remove(temp_path)
        except OSError:
            # Never let cleanup mask the original failure.
            pass
        raise
