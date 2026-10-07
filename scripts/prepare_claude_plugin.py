"""Create a clean, tracked-files-only Claude marketplace snapshot of this checkout."""

from __future__ import annotations

import io
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True
    ).stdout


def main() -> None:
    revision = git("rev-parse", "HEAD").decode().strip()
    destination = Path.home() / ".claude" / "skillsrepo-v2-snapshots" / revision[:12]
    manifest = destination / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(git("archive", "--format=zip", "HEAD"))) as archive:
            for entry in archive.namelist():
                path = PurePosixPath(entry)
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError(f"unsafe archive path: {entry}")
            archive.extractall(destination)
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    print(destination)


if __name__ == "__main__":
    main()
