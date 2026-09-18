import json
import os
import tempfile


def save_settings(path, data, *, replace=os.replace):
    directory = os.path.dirname(os.path.abspath(path))
    fd, temp_path = tempfile.mkstemp(dir=directory)
    try:
        try:
            temp_file = os.fdopen(fd, "w", encoding="utf-8")
        except BaseException:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
        with temp_file:
            json.dump(data, temp_file, sort_keys=True)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        replace(temp_path, path)
    except BaseException:
        # Best-effort cleanup; never mask the original failure.
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise
