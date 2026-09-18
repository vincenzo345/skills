import os
from pathlib import Path


def _resolve(path):
    # os.fspath accepts str and os.PathLike; resolve() makes the path absolute,
    # collapses ".." segments, and follows symlinks for components that exist.
    # Anchoring to cwd first guards against older Windows Pythons returning a
    # relative result for nonexistent paths, without collapsing ".." textually.
    path = Path(os.fspath(path))
    if not path.is_absolute():
        path = Path.cwd() / path
    return os.path.normcase(str(path.resolve()))


def is_within(root, candidate):
    """Return True if candidate is root itself or lies beneath it on disk."""
    root_resolved = _resolve(root)
    candidate_resolved = _resolve(candidate)
    try:
        common = os.path.commonpath([root_resolved, candidate_resolved])
    except ValueError:
        # Different drives on Windows, or otherwise incomparable paths.
        return False
    return common == root_resolved
