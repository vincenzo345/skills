"""Immutable task catalog for coding-agent harness evaluations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re


_TASK_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CATEGORIES = {"algorithmic", "integration", "robustness", "work-discipline"}


@dataclass(frozen=True)
class FileSpec:
    path: str
    content: str

    def __post_init__(self) -> None:
        candidate = PurePosixPath(self.path)
        if candidate.is_absolute() or not self.path or ".." in candidate.parts:
            raise ValueError(f"unsafe task file path: {self.path!r}")


@dataclass(frozen=True)
class TaskSpec:
    id: str
    title: str
    category: str
    tags: tuple[str, ...]
    instruction: str
    seed_files: tuple[FileSpec, ...]
    reference_files: tuple[FileSpec, ...]
    acceptance_program: str
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not _TASK_ID.fullmatch(self.id):
            raise ValueError(f"invalid task id: {self.id!r}")
        if self.category not in _CATEGORIES:
            raise ValueError(f"invalid task category: {self.category!r}")
        if not self.title.strip() or not self.tags or not self.instruction.strip():
            raise ValueError(f"incomplete task metadata: {self.id}")
        if not self.seed_files or not self.reference_files or not self.acceptance_program.strip():
            raise ValueError(f"incomplete task executable contract: {self.id}")
        if self.timeout_seconds <= 0:
            raise ValueError(f"invalid task timeout: {self.id}")
        for label, files in (("seed", self.seed_files), ("reference", self.reference_files)):
            paths = [file.path for file in files]
            if len(paths) != len(set(paths)):
                raise ValueError(f"duplicate {label} path in task {self.id}")


_RANGE_INSTRUCTION = """# Inclusive range partition

Fix `ranges.partition(start, end, size)` so it partitions the inclusive integer range from `start` through `end` into ordered inclusive `(chunk_start, chunk_end)` pairs.

Completion criteria:

- Every integer in the requested range appears exactly once.
- Empty ranges return an empty list.
- Singleton, exact-size, and remainder ranges work.
- A non-positive size raises `ValueError`.
- Keep the existing public function name and parameters.
"""

_RANGE_SEED = """def partition(start: int, end: int, size: int) -> list[tuple[int, int]]:
    if size <= 0:
        raise ValueError("size must be positive")
    if start > end:
        return []
    result = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + size - 1, end - 1)
        result.append((cursor, chunk_end))
        cursor = chunk_end + 1
    return result
"""

_RANGE_REFERENCE = """def partition(start: int, end: int, size: int) -> list[tuple[int, int]]:
    if size <= 0:
        raise ValueError("size must be positive")
    if start > end:
        return []
    result = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + size - 1, end)
        result.append((cursor, chunk_end))
        cursor = chunk_end + 1
    return result
"""

_RANGE_ACCEPTANCE = """from pathlib import Path
import sys

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from ranges import partition

assert partition(1, 5, 2) == [(1, 2), (3, 4), (5, 5)]
assert partition(4, 4, 3) == [(4, 4)]
assert partition(2, 5, 4) == [(2, 5)]
assert partition(9, 8, 2) == []
for start, end, size in [(-3, 4, 3), (0, 9, 1), (5, 17, 5)]:
    chunks = partition(start, end, size)
    flattened = [value for left, right in chunks for value in range(left, right + 1)]
    assert flattened == list(range(start, end + 1))
try:
    partition(1, 2, 0)
except ValueError:
    pass
else:
    raise AssertionError("non-positive size must raise ValueError")
"""


_TASKS = (
    TaskSpec(
        id="inclusive-range-partition",
        title="Inclusive range partition",
        category="algorithmic",
        tags=("boundaries", "regression", "hidden-tests"),
        instruction=_RANGE_INSTRUCTION,
        seed_files=(FileSpec("ranges.py", _RANGE_SEED),),
        reference_files=(FileSpec("ranges.py", _RANGE_REFERENCE),),
        acceptance_program=_RANGE_ACCEPTANCE,
    ),
)


def _files(**files: str) -> tuple[FileSpec, ...]:
    result = []
    for encoded_path, content in files.items():
        path = encoded_path.replace("___", "/")
        for suffix in ("py", "txt", "json"):
            marker = "_" + suffix
            if path.endswith(marker):
                path = path[: -len(marker)] + "." + suffix
                break
        result.append(FileSpec(path, content))
    return tuple(result)


def _program(body: str) -> str:
    return "from pathlib import Path\nimport sys\nroot = Path(sys.argv[1])\nsys.path.insert(0, str(root))\n" + body


_TASKS += (
    TaskSpec(
        id="unicode-username-match",
        title="Unicode username matching",
        category="algorithmic",
        tags=("unicode", "normalization", "public-contract"),
        instruction="""# Unicode username matching

Fix `users.find_user(query, users)` so matching is Unicode-aware while returning the original display spelling.

Completion criteria:

- Normalize usernames with Unicode NFKC normalization and case-insensitive `casefold()` semantics.
- Composed and decomposed spellings compare equally.
- Return the original string from `users`, or `None` when no user matches.
- Keep the existing function names and parameters.
""",
        seed_files=_files(users_py="""def canonical_username(value: str) -> str:
    return value.lower()


def find_user(query: str, users: list[str]) -> str | None:
    wanted = canonical_username(query)
    return next((user for user in users if canonical_username(user) == wanted), None)
"""),
        reference_files=_files(users_py="""import unicodedata


def canonical_username(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def find_user(query: str, users: list[str]) -> str | None:
    wanted = canonical_username(query)
    return next((user for user in users if canonical_username(user) == wanted), None)
"""),
        acceptance_program=_program("""from users import canonical_username, find_user
names = ["Straße", "José", "Ａｌｉｃｅ"]
assert find_user("STRASSE", names) == "Straße"
assert find_user("Jose\u0301", names) == "José"
assert find_user("alice", names) == "Ａｌｉｃｅ"
assert find_user("missing", names) is None
assert canonical_username("É") == canonical_username("E\u0301")
"""),
    ),
    TaskSpec(
        id="one-shot-iterator",
        title="One-shot iterator support",
        category="algorithmic",
        tags=("iterators", "generators", "regression"),
        instruction="""# One-shot iterator support

Fix `batch.describe(values)` so it works identically for lists and one-shot iterators.

Completion criteria:

- Return `{"count": N, "total": T}` for every finite iterable of numbers.
- Lists, generators, and empty iterables behave identically.
- Iterate the supplied iterable only once.
- Preserve exceptions raised by the iterable.
""",
        seed_files=_files(batch_py="""def describe(values):
    total = sum(values)
    count = sum(1 for _ in values)
    return {"count": count, "total": total}
"""),
        reference_files=_files(batch_py="""def describe(values):
    items = list(values)
    return {"count": len(items), "total": sum(items)}
"""),
        acceptance_program=_program("""from batch import describe
assert describe([2, 3, 5]) == {"count": 3, "total": 10}
assert describe((value for value in [2, 3, 5])) == {"count": 3, "total": 10}
assert describe(iter(())) == {"count": 0, "total": 0}
seen = []
def once():
    for value in [4, 7]:
        seen.append(value)
        yield value
assert describe(once()) == {"count": 2, "total": 11}
assert seen == [4, 7]
"""),
    ),
    TaskSpec(
        id="pagination-cursor",
        title="Pagination cursor termination",
        category="integration",
        tags=("pagination", "termination", "boundaries"),
        instruction="""# Pagination cursor termination

Fix `pagination.collect_pages(fetch_page, page_size)` where `fetch_page(cursor, page_size)` returns `(items, next_cursor)`.

Completion criteria:

- Start with cursor `None` and concatenate pages in order.
- Stop exactly when `next_cursor` is `None`, including after a full final page.
- Empty sources return an empty list after one fetch.
- Never repeat a cursor or request another page after termination.
""",
        seed_files=_files(pagination_py="""def collect_pages(fetch_page, page_size: int = 2):
    result = []
    cursor = None
    while True:
        items, next_cursor = fetch_page(cursor, page_size)
        result.extend(items)
        if not items:
            return result
        cursor = next_cursor
"""),
        reference_files=_files(pagination_py="""def collect_pages(fetch_page, page_size: int = 2):
    result = []
    cursor = None
    seen = set()
    while True:
        if cursor in seen:
            raise ValueError("pagination cursor repeated")
        seen.add(cursor)
        items, next_cursor = fetch_page(cursor, page_size)
        result.extend(items)
        if next_cursor is None:
            return result
        cursor = next_cursor
"""),
        acceptance_program=_program("""from pagination import collect_pages
def source(values):
    calls = []
    def fetch(cursor, size):
        calls.append(cursor)
        if len(calls) > 10:
            raise AssertionError("pagination did not terminate")
        start = 0 if cursor is None else cursor
        items = values[start:start + size]
        next_cursor = start + size if start + size < len(values) else None
        return items, next_cursor
    return fetch, calls
for values, size in [([], 2), ([1], 1), ([1, 2, 3, 4], 2), ([1, 2, 3, 4, 5], 2)]:
    fetch, calls = source(values)
    assert collect_pages(fetch, size) == values
    assert len(calls) == max(1, (len(values) + size - 1) // size)
"""),
    ),
    TaskSpec(
        id="cache-key-completeness",
        title="Cache key completeness",
        category="integration",
        tags=("cache", "contracts", "state"),
        instruction="""# Cache key completeness

Fix `render_cache.RenderCache.render(document, options, renderer)` so cached results respect every output-changing option.

Completion criteria:

- Calls with the same document and equivalent option mappings reuse one cached value.
- Calls whose options differ compute and cache separate values.
- Option key order does not change equivalence.
- Keep cache state private to each `RenderCache` instance.
""",
        seed_files=_files(render_cache_py="""class RenderCache:
    def __init__(self):
        self._values = {}

    def render(self, document, options, renderer):
        if document not in self._values:
            self._values[document] = renderer(document, options)
        return self._values[document]
"""),
        reference_files=_files(render_cache_py="""class RenderCache:
    def __init__(self):
        self._values = {}

    def render(self, document, options, renderer):
        key = (document, tuple(sorted(options.items())))
        if key not in self._values:
            self._values[key] = renderer(document, options)
        return self._values[key]
"""),
        acceptance_program=_program("""from render_cache import RenderCache
calls = []
def renderer(document, options):
    calls.append((document, dict(options)))
    return f"{document}:{options['theme']}:{options.get('width', 0)}"
cache = RenderCache()
assert cache.render("doc", {"theme": "light", "width": 80}, renderer) == "doc:light:80"
assert cache.render("doc", {"width": 80, "theme": "light"}, renderer) == "doc:light:80"
assert cache.render("doc", {"theme": "dark", "width": 80}, renderer) == "doc:dark:80"
assert len(calls) == 2
other = RenderCache()
other.render("doc", {"theme": "light", "width": 80}, renderer)
assert len(calls) == 3
"""),
    ),
    TaskSpec(
        id="config-precedence",
        title="Configuration precedence with falsey values",
        category="integration",
        tags=("configuration", "precedence", "falsey-values"),
        instruction="""# Configuration precedence

Fix `config_loader.load_config(keys, cli, environment, file_values, defaults)`.

Completion criteria:

- Resolve each key in this order: CLI, environment, file, default.
- Presence, not truthiness, selects a value; `False`, `0`, and an empty string are explicit values.
- Missing keys resolve to `None` when absent from every source.
- Do not mutate any source mapping.
""",
        seed_files=_files(config_loader_py="""def load_config(keys, cli, environment, file_values, defaults):
    return {
        key: cli.get(key) or environment.get(key) or file_values.get(key) or defaults.get(key)
        for key in keys
    }
"""),
        reference_files=_files(config_loader_py="""def load_config(keys, cli, environment, file_values, defaults):
    result = {}
    sources = (cli, environment, file_values, defaults)
    for key in keys:
        result[key] = next((source[key] for source in sources if key in source), None)
    return result
"""),
        acceptance_program=_program("""from config_loader import load_config
cli = {"debug": False, "workers": 0}
env = {"debug": True, "workers": 8, "label": ""}
file_values = {"label": "file", "region": "file-region"}
defaults = {"debug": True, "workers": 4, "label": "default", "region": "default"}
snapshots = [dict(value) for value in (cli, env, file_values, defaults)]
assert load_config(["debug", "workers", "label", "region", "missing"], cli, env, file_values, defaults) == {
    "debug": False, "workers": 0, "label": "", "region": "file-region", "missing": None
}
assert snapshots == [cli, env, file_values, defaults]
"""),
    ),
)

_TASKS += (
    TaskSpec(
        id="backward-compatible-api",
        title="Backward-compatible API extension",
        category="integration",
        tags=("api", "compatibility", "callers"),
        instruction="""# Backward-compatible API extension

Extend `labels.format_label` with an optional keyword-only `prefix` without breaking existing callers.

Completion criteria:

- Existing calls `format_label(name)` and `format_label(name, uppercase)` retain their behavior.
- `format_label(name, uppercase, prefix="...")` prepends the prefix before case conversion.
- `prefix` cannot be supplied as a third positional argument.
- The default prefix is an empty string.
""",
        seed_files=_files(labels_py="""def format_label(name: str, uppercase: bool = False) -> str:
    return name.upper() if uppercase else name
"""),
        reference_files=_files(labels_py="""def format_label(name: str, uppercase: bool = False, *, prefix: str = "") -> str:
    value = prefix + name
    return value.upper() if uppercase else value
"""),
        acceptance_program=_program("""from labels import format_label
assert format_label("report") == "report"
assert format_label("report", True) == "REPORT"
assert format_label("report", prefix="draft: ") == "draft: report"
assert format_label("report", True, prefix="draft: ") == "DRAFT: REPORT"
try:
    format_label("report", False, "draft: ")
except TypeError:
    pass
else:
    raise AssertionError("prefix must remain keyword-only")
"""),
    ),
    TaskSpec(
        id="error-contract",
        title="Public error-contract preservation",
        category="integration",
        tags=("exceptions", "contracts", "validation"),
        instruction="""# Public error contract

Fix `ports.parse_port(value)` while preserving its public exception contract.

Completion criteria:

- Decimal strings representing ports 1 through 65535 return an integer.
- Invalid text and out-of-range values raise `ConfigError`.
- `ConfigError` exposes `key == "port"` and the original `value`.
- The error message contains both the key and original value; unexpected programmer errors must not be swallowed.
""",
        seed_files=_files(ports_py="""class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    return port if 1 <= port <= 65535 else None
"""),
        reference_files=_files(ports_py="""class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError("port", value) from exc
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
"""),
        acceptance_program=_program("""from ports import ConfigError, parse_port
assert parse_port("1") == 1
assert parse_port("65535") == 65535
for value in ["nope", "0", "65536", None]:
    try:
        parse_port(value)
    except ConfigError as error:
        assert error.key == "port"
        assert error.value == value
        assert "port" in str(error) and str(value) in str(error)
    else:
        raise AssertionError(f"{value!r} did not raise ConfigError")
"""),
    ),
    TaskSpec(
        id="cross-file-symbol-rename",
        title="Cross-file symbol rename",
        category="integration",
        tags=("refactor", "exports", "registry"),
        instruction="""# Cross-file symbol rename

Introduce the preferred public name `to_slug` for the existing `slugify` behavior and update the small integration surface.

Completion criteria:

- `slug.to_slug` implements the existing slug conversion.
- `slug.slugify` remains as a backward-compatible alias.
- `api.make_slug` calls the preferred name.
- `registry.CALLS` registers the behavior under key `"to_slug"` with no stale `"slugify"` key.
""",
        seed_files=_files(
            slug_py="""def slugify(value: str) -> str:
    return "-".join(value.strip().lower().split())
""",
            api_py="""from slug import slugify


def make_slug(value: str) -> str:
    return slugify(value)
""",
            registry_py="""from slug import slugify

CALLS = {"slugify": slugify}
""",
        ),
        reference_files=_files(
            slug_py="""def to_slug(value: str) -> str:
    return "-".join(value.strip().lower().split())


slugify = to_slug
""",
            api_py="""from slug import to_slug


def make_slug(value: str) -> str:
    return to_slug(value)
""",
            registry_py="""from slug import to_slug

CALLS = {"to_slug": to_slug}
""",
        ),
        acceptance_program=_program("""import api
import registry
import slug
assert slug.to_slug("  Hello World ") == "hello-world"
assert slug.slugify("  Hello World ") == "hello-world"
assert slug.slugify is slug.to_slug
assert api.make_slug("A B") == "a-b"
assert set(registry.CALLS) == {"to_slug"}
assert registry.CALLS["to_slug"]("A B") == "a-b"
assert "to_slug" in (root / "api.py").read_text(encoding="utf-8")
"""),
    ),
    TaskSpec(
        id="serialization-extensions",
        title="Serialization extension round trip",
        category="integration",
        tags=("serialization", "compatibility", "round-trip"),
        instruction="""# Serialization extension round trip

Fix `records.Record.from_dict` and `to_dict` so forward-compatible extension fields survive a round trip.

Completion criteria:

- `name` remains the required known field.
- Every unknown input field is preserved unchanged in `record.extensions`.
- `to_dict()` returns `name` plus all preserved extensions without mutating input data.
- An extension named `name` cannot override the record's known name.
""",
        seed_files=_files(records_py="""class Record:
    def __init__(self, name, extensions=None):
        self.name = name
        self.extensions = dict(extensions or {})

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"])

    def to_dict(self):
        return {"name": self.name}
"""),
        reference_files=_files(records_py="""class Record:
    def __init__(self, name, extensions=None):
        self.name = name
        self.extensions = {key: value for key, value in dict(extensions or {}).items() if key != "name"}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], {key: value for key, value in data.items() if key != "name"})

    def to_dict(self):
        return {"name": self.name, **self.extensions}
"""),
        acceptance_program=_program("""from records import Record
source = {"name": "alpha", "future": {"enabled": True}, "count": 0}
snapshot = {"name": "alpha", "future": {"enabled": True}, "count": 0}
record = Record.from_dict(source)
assert record.name == "alpha"
assert record.extensions == {"future": {"enabled": True}, "count": 0}
assert record.to_dict() == snapshot
assert source == snapshot
manual = Record("fixed", {"name": "wrong", "extra": 1})
assert manual.to_dict() == {"name": "fixed", "extra": 1}
"""),
    ),
    TaskSpec(
        id="cli-stream-semantics",
        title="CLI stream and exit semantics",
        category="integration",
        tags=("cli", "stderr", "exit-code"),
        instruction="""# CLI stream and exit semantics

Fix the executable `cli_app.py`, which squares one integer argument.

Completion criteria:

- A valid integer prints its square to stdout and exits 0.
- Invalid input prints a concise `error:` message to stderr, prints nothing to stdout, exits 2, and shows no traceback.
- `--quiet` suppresses successful stdout while retaining exit 0.
- Keep `main(argv)` directly testable and the script executable.
""",
        seed_files=_files(cli_app_py="""import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in args
    args = [arg for arg in args if arg != "--quiet"]
    try:
        value = int(args[0])
    except (IndexError, ValueError):
        print("error: expected an integer")
        return 0
    if not quiet:
        print(value * value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""),
        reference_files=_files(cli_app_py="""import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in args
    args = [arg for arg in args if arg != "--quiet"]
    try:
        if len(args) != 1:
            raise ValueError
        value = int(args[0])
    except ValueError:
        print("error: expected one integer", file=sys.stderr)
        return 2
    if not quiet:
        print(value * value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""),
        acceptance_program=_program("""import subprocess
success = subprocess.run([sys.executable, str(root / "cli_app.py"), "7"], capture_output=True, text=True)
assert success.returncode == 0 and success.stdout == "49\\n" and success.stderr == ""
quiet = subprocess.run([sys.executable, str(root / "cli_app.py"), "--quiet", "7"], capture_output=True, text=True)
assert quiet.returncode == 0 and quiet.stdout == "" and quiet.stderr == ""
failure = subprocess.run([sys.executable, str(root / "cli_app.py"), "bad"], capture_output=True, text=True)
assert failure.returncode == 2
assert failure.stdout == ""
assert failure.stderr.startswith("error:")
assert "Traceback" not in failure.stderr
"""),
    ),
)

_TASKS += (
    TaskSpec(
        id="atomic-settings-write",
        title="Atomic settings write",
        category="robustness",
        tags=("filesystem", "atomicity", "failure-path"),
        instruction="""# Atomic settings write

Fix `settings.save_settings(path, data, replace=os.replace)` so an interrupted replacement cannot corrupt the existing file.

Completion criteria:

- Write valid JSON to a temporary file in the destination directory, then atomically call the injected `replace(temp, destination)` function.
- A successful call replaces the destination with the new data.
- If writing or replacement fails, preserve the old destination and remove task-owned temporary files.
- Propagate the original failure and keep the injectable `replace` parameter.
""",
        seed_files=_files(settings_py="""import json
import os


def save_settings(path, data, *, replace=os.replace):
    with open(path, "w", encoding="utf-8") as destination:
        json.dump(data, destination, sort_keys=True)
"""),
        reference_files=_files(settings_py="""import json
import os
from pathlib import Path
import tempfile


def save_settings(path, data, *, replace=os.replace):
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(data, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())
        replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
"""),
        acceptance_program=_program("""import json
from settings import save_settings
path = root / "settings.json"
path.write_text('{"version": 1}', encoding="utf-8")
def fail_replace(source, destination):
    raise RuntimeError("injected replacement failure")
try:
    save_settings(path, {"version": 2}, replace=fail_replace)
except RuntimeError as error:
    assert "injected" in str(error)
else:
    raise AssertionError("replacement failure was not propagated")
assert json.loads(path.read_text(encoding="utf-8")) == {"version": 1}
assert sorted(item.name for item in root.iterdir()) == [".harness-eval.json", "TASK.md", "settings.json", "settings.py"]
save_settings(path, {"version": 3, "enabled": False})
assert json.loads(path.read_text(encoding="utf-8")) == {"enabled": False, "version": 3}
"""),
    ),
    TaskSpec(
        id="path-containment",
        title="Path containment",
        category="robustness",
        tags=("paths", "security", "cross-platform"),
        instruction="""# Path containment

Fix `paths.is_within(root, candidate)` so it checks resolved filesystem containment rather than text prefixes.

Completion criteria:

- Return true for the root itself and normal descendants.
- Return false for parents, sibling-prefix paths, and `..` escapes.
- Resolve symlinks before deciding when the platform permits symlink creation.
- Accept strings or path-like values and remain cross-platform.
""",
        seed_files=_files(paths_py="""from pathlib import Path


def is_within(root, candidate):
    return str(Path(candidate).resolve()).startswith(str(Path(root).resolve()))
"""),
        reference_files=_files(paths_py="""from pathlib import Path


def is_within(root, candidate):
    resolved_root = Path(root).resolve()
    resolved_candidate = Path(candidate).resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError:
        return False
    return True
"""),
        acceptance_program=_program("""import tempfile
from paths import is_within
base = Path(tempfile.mkdtemp())
allowed = base / "app"
allowed.mkdir()
(allowed / "nested").mkdir()
sibling = base / "application-secrets"
sibling.mkdir()
assert is_within(allowed, allowed)
assert is_within(allowed, allowed / "nested")
assert not is_within(allowed, sibling)
assert not is_within(allowed, allowed / ".." / "application-secrets")
link = allowed / "escape-link"
try:
    link.symlink_to(sibling, target_is_directory=True)
except OSError:
    pass
else:
    assert not is_within(allowed, link / "token.txt")
"""),
    ),
    TaskSpec(
        id="secret-safe-diagnostics",
        title="Secret-safe diagnostics",
        category="robustness",
        tags=("secrets", "errors", "redaction"),
        instruction="""# Secret-safe diagnostics

Fix `diagnostics.safe_diagnostic(error, secrets)` so actionable errors never expose supplied secret values.

Completion criteria:

- Return a string containing the exception type and its redacted message.
- Replace every nonempty supplied secret value wherever it appears, regardless of surrounding label or punctuation.
- Use the literal marker `[REDACTED]` and handle overlapping secrets without partial leakage.
- Ignore empty secret values and do not mutate the exception or input collection.
""",
        seed_files=_files(diagnostics_py="""def safe_diagnostic(error, secrets):
    message = f"{type(error).__name__}: {error}"
    for secret in secrets:
        message = message.replace(f"TOKEN={secret}", "TOKEN=[REDACTED]")
    return message
"""),
        reference_files=_files(diagnostics_py="""def safe_diagnostic(error, secrets):
    message = f"{type(error).__name__}: {error}"
    for secret in sorted((value for value in secrets if value), key=len, reverse=True):
        message = message.replace(secret, "[REDACTED]")
    return message
"""),
        acceptance_program=_program("""from diagnostics import safe_diagnostic
secrets = ["abc123", "abc", "p@ss-word", ""]
snapshot = list(secrets)
error = RuntimeError("TOKEN=abc123 password:p@ss-word bare=abc123")
result = safe_diagnostic(error, secrets)
assert result.startswith("RuntimeError:")
assert result.count("[REDACTED]") == 3
for secret in ["abc123", "p@ss-word"]:
    assert secret not in result
assert secrets == snapshot
assert str(error) == "TOKEN=abc123 password:p@ss-word bare=abc123"
"""),
    ),
    TaskSpec(
        id="sqlite-transaction",
        title="SQLite transaction boundary",
        category="robustness",
        tags=("sqlite", "transactions", "rollback"),
        instruction="""# SQLite transaction boundary

Fix `transfers.transfer(conn, source_id, target_id, amount, fail_after_debit=False)` so the two balance updates are atomic.

Completion criteria:

- A successful transfer debits the source and credits the target exactly once.
- If any failure occurs after the debit, neither balance change is committed.
- Propagate the failure and leave the connection usable.
- Use the supplied connection; do not close it or create another database.
""",
        seed_files=_files(transfers_py="""def transfer(conn, source_id, target_id, amount, fail_after_debit=False):
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, source_id))
    conn.commit()
    if fail_after_debit:
        raise RuntimeError("injected failure")
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, target_id))
    conn.commit()
"""),
        reference_files=_files(transfers_py="""def transfer(conn, source_id, target_id, amount, fail_after_debit=False):
    with conn:
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, source_id))
        if fail_after_debit:
            raise RuntimeError("injected failure")
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, target_id))
"""),
        acceptance_program=_program("""import sqlite3
from transfers import transfer
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL)")
conn.executemany("INSERT INTO accounts VALUES (?, ?)", [(1, 100), (2, 20)])
conn.commit()
try:
    transfer(conn, 1, 2, 30, fail_after_debit=True)
except RuntimeError:
    pass
else:
    raise AssertionError("injected failure was not propagated")
assert conn.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall() == [(1, 100), (2, 20)]
transfer(conn, 1, 2, 30)
assert conn.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall() == [(1, 70), (2, 50)]
assert conn.execute("SELECT 1").fetchone() == (1,)
"""),
    ),
    TaskSpec(
        id="concurrent-memoization",
        title="Concurrent memoization",
        category="robustness",
        tags=("concurrency", "cache", "synchronization"),
        instruction="""# Concurrent memoization

Fix `memo.Memo.get(key, compute)` so concurrent callers for the same missing key share one computation.

Completion criteria:

- Concurrent callers for one key all receive the same value from exactly one `compute()` call.
- Cached calls do not recompute.
- Different `Memo` instances remain independent.
- A failed computation is propagated and does not poison future retries.
""",
        seed_files=_files(memo_py="""class Memo:
    def __init__(self):
        self._values = {}

    def get(self, key, compute):
        if key not in self._values:
            self._values[key] = compute()
        return self._values[key]
"""),
        reference_files=_files(memo_py="""import threading


class Memo:
    def __init__(self):
        self._values = {}
        self._running = {}
        self._lock = threading.Lock()

    def get(self, key, compute):
        with self._lock:
            if key in self._values:
                return self._values[key]
            event = self._running.get(key)
            owner = event is None
            if owner:
                event = threading.Event()
                self._running[key] = event
        if not owner:
            event.wait()
            with self._lock:
                if key in self._values:
                    return self._values[key]
            return self.get(key, compute)
        try:
            value = compute()
        except BaseException:
            with self._lock:
                self._running.pop(key).set()
            raise
        with self._lock:
            self._values[key] = value
            self._running.pop(key).set()
        return value
"""),
        acceptance_program=_program("""import threading
from memo import Memo
memo = Memo()
start = threading.Barrier(3)
release = threading.Event()
entered_twice = threading.Event()
count_lock = threading.Lock()
calls = [0]
results = []
def compute():
    with count_lock:
        calls[0] += 1
        if calls[0] == 2:
            entered_twice.set()
    release.wait(2)
    return 42
def worker():
    start.wait()
    results.append(memo.get("answer", compute))
threads = [threading.Thread(target=worker) for _ in range(2)]
for thread in threads:
    thread.start()
start.wait()
entered_twice.wait(0.3)
release.set()
for thread in threads:
    thread.join(2)
assert not any(thread.is_alive() for thread in threads)
assert sorted(results) == [42, 42]
assert calls[0] == 1
assert memo.get("answer", lambda: 99) == 42
failed = Memo()
try:
    failed.get("x", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
except RuntimeError:
    pass
else:
    raise AssertionError("failure was not propagated")
assert failed.get("x", lambda: 7) == 7
"""),
    ),
)

_TASKS += (
    TaskSpec(
        id="shared-validator-refactor",
        title="Shared validator refactor",
        category="work-discipline",
        tags=("refactor", "duplication", "call-sites"),
        instruction="""# Shared validator refactor

Refactor the duplicated email normalization in `user_models.py` and `admin_models.py` into `validators.py` without changing the public creation functions.

Completion criteria:

- Define one shared `validators.normalize_email(value)` implementation that trims surrounding whitespace and lowercases the address.
- Both `create_user` and `create_admin` import and use that shared implementation.
- Keep both public function names and their dictionary result shapes.
- Remove the duplicated local normalization definitions.
""",
        seed_files=_files(
            user_models_py="""def normalize_email(value):
    return value.strip().lower()


def create_user(email):
    return {"kind": "user", "email": normalize_email(email)}
""",
            admin_models_py="""def normalize_email(value):
    return value.lower()


def create_admin(email):
    return {"kind": "admin", "email": normalize_email(email)}
""",
        ),
        reference_files=_files(
            validators_py="""def normalize_email(value):
    return value.strip().lower()
""",
            user_models_py="""from validators import normalize_email


def create_user(email):
    return {"kind": "user", "email": normalize_email(email)}
""",
            admin_models_py="""from validators import normalize_email


def create_admin(email):
    return {"kind": "admin", "email": normalize_email(email)}
""",
        ),
        acceptance_program=_program("""from admin_models import create_admin
from user_models import create_user
from validators import normalize_email
assert normalize_email("  Person@Example.COM ") == "person@example.com"
assert create_user("  Person@Example.COM ") == {"kind": "user", "email": "person@example.com"}
assert create_admin("  Person@Example.COM ") == {"kind": "admin", "email": "person@example.com"}
sources = [(root / name).read_text(encoding="utf-8") for name in ["validators.py", "user_models.py", "admin_models.py"]]
assert sum("def normalize_email" in source for source in sources) == 1
assert "from validators import normalize_email" in sources[1]
assert "from validators import normalize_email" in sources[2]
"""),
    ),
    TaskSpec(
        id="implementation-not-tests",
        title="Repair implementation without weakening tests",
        category="work-discipline",
        tags=("regression", "test-integrity", "scope"),
        instruction="""# Repair the implementation, not the tests

Fix `mathlib.multiply(a, b)`, which currently fails the visible regression checks.

Completion criteria:

- Return the mathematical product for positive, negative, and zero operands.
- Preserve the public function signature.
- Keep `test_mathlib.py` byte-for-byte unchanged; it is a protected regression asset.
- Make the visible regression script and additional inputs pass by changing the implementation.
""",
        seed_files=_files(
            mathlib_py="""def multiply(a, b):
    return a - b
""",
            test_mathlib_py="""from mathlib import multiply

assert multiply(3, 4) == 12
assert multiply(0, 9) == 0
""",
        ),
        reference_files=_files(mathlib_py="""def multiply(a, b):
    return a * b
"""),
        acceptance_program=_program("""import subprocess
from mathlib import multiply
expected_test = 'from mathlib import multiply\\n\\nassert multiply(3, 4) == 12\\nassert multiply(0, 9) == 0\\n'
assert (root / "test_mathlib.py").read_text(encoding="utf-8") == expected_test
visible = subprocess.run([sys.executable, str(root / "test_mathlib.py")], cwd=root, capture_output=True, text=True)
assert visible.returncode == 0, visible.stderr
assert multiply(-3, 4) == -12
assert multiply(-3, -4) == 12
assert multiply(7, 1) == 7
"""),
    ),
    TaskSpec(
        id="two-cause-regression",
        title="Two-cause key normalization regression",
        category="work-discipline",
        tags=("regression", "multiple-paths", "call-sites"),
        instruction="""# Two-cause key normalization regression

Configuration keys must be case-insensitive and treat hyphens and underscores equivalently across mapping and environment inputs.

Completion criteria:

- `normalize_key` lowercases and converts `-` to `_`.
- `load_mapping(mapping)` normalizes every mapping key.
- `load_environment(environment, prefix="APP_")` strips the prefix and applies the same normalization.
- Ignore environment entries outside the requested prefix and preserve values unchanged.
""",
        seed_files=_files(keys_py="""def normalize_key(value):
    return value.strip().lower().replace("-", "_")


def load_mapping(mapping):
    return {normalize_key(key): value for key, value in mapping.items()}


def load_environment(environment, prefix="APP_"):
    return {
        key[len(prefix):].lower(): value
        for key, value in environment.items()
        if key.startswith(prefix)
    }
"""),
        reference_files=_files(keys_py="""def normalize_key(value):
    return value.strip().lower().replace("-", "_")


def load_mapping(mapping):
    return {normalize_key(key): value for key, value in mapping.items()}


def load_environment(environment, prefix="APP_"):
    return {
        normalize_key(key[len(prefix):]): value
        for key, value in environment.items()
        if key.startswith(prefix)
    }
"""),
        acceptance_program=_program("""from keys import load_environment, load_mapping, normalize_key
assert normalize_key(" Feature-Flag ") == "feature_flag"
assert load_mapping({"Feature-Flag": False, "MAX-WORKERS": 0}) == {"feature_flag": False, "max_workers": 0}
environment = {"APP_FEATURE-FLAG": "off", "APP_MAX_WORKERS": "3", "OTHER_VALUE": "ignored"}
assert load_environment(environment) == {"feature_flag": "off", "max_workers": "3"}
assert environment["OTHER_VALUE"] == "ignored"
"""),
    ),
    TaskSpec(
        id="preserve-dirty-file",
        title="Preserve unrelated user work",
        category="work-discipline",
        tags=("scope", "dirty-worktree", "preservation"),
        instruction="""# Preserve unrelated user work

Fix `app.greet(name)` so it returns a conventional greeting with a comma.

Completion criteria:

- `greet("Ada")` returns `"Hello, Ada!"` and other names follow the same format.
- Keep the public function name and parameter.
- Preserve `notes.txt` byte-for-byte; it represents an unrelated pre-existing user change.
- Make no generated artifacts part of the solution.
""",
        seed_files=_files(
            app_py="""def greet(name):
    return f"Hello {name}!"
""",
            notes_txt="""UNRELATED USER DRAFT
keep this spacing
do not rewrite
""",
        ),
        reference_files=_files(app_py="""def greet(name):
    return f"Hello, {name}!"
"""),
        acceptance_program=_program("""from app import greet
assert greet("Ada") == "Hello, Ada!"
assert greet("Grace Hopper") == "Hello, Grace Hopper!"
assert (root / "notes.txt").read_bytes() == b"UNRELATED USER DRAFT\\nkeep this spacing\\ndo not rewrite\\n"
unexpected = {".pytest_cache", "__pycache__"} & {item.name for item in root.iterdir()}
assert not unexpected
"""),
    ),
    TaskSpec(
        id="resource-cleanup-contract",
        title="Resource cleanup without exception masking",
        category="robustness",
        tags=("resources", "exceptions", "cleanup"),
        instruction="""# Resource cleanup contract

Fix `resources.read_payload(opener, path)` so the handle returned by `opener(path)` is always closed after it is opened.

Completion criteria:

- Return the exact result of `handle.read()` on success.
- Close the handle exactly once after either a successful read or a read failure.
- Preserve the original exception raised by `read()`; do not replace or swallow it.
- If `opener` itself fails, propagate that exception without attempting cleanup.
- Do not assume the returned handle implements a context manager.
""",
        seed_files=_files(resources_py="""def read_payload(opener, path):
    handle = opener(path)
    return handle.read()
"""),
        reference_files=_files(resources_py="""def read_payload(opener, path):
    handle = opener(path)
    try:
        return handle.read()
    finally:
        handle.close()
"""),
        acceptance_program=_program("""from resources import read_payload

class ReadFailure(RuntimeError):
    pass

class Handle:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self.close_calls = 0
    def read(self):
        if self.error is not None:
            raise self.error
        return self.value
    def close(self):
        self.close_calls += 1

success = Handle(value={"payload": 1})
assert read_payload(lambda path: success, "x") is success.value
assert success.close_calls == 1

failure = ReadFailure("read failed")
broken = Handle(error=failure)
try:
    read_payload(lambda path: broken, "x")
except ReadFailure as error:
    assert error is failure
else:
    raise AssertionError("read failure was swallowed")
assert broken.close_calls == 1

open_failure = ReadFailure("open failed")
try:
    read_payload(lambda path: (_ for _ in ()).throw(open_failure), "x")
except ReadFailure as error:
    assert error is open_failure
else:
    raise AssertionError("open failure was swallowed")
"""),
    ),
    TaskSpec(
        id="retry-attempt-semantics",
        title="Bounded retry and exception contract",
        category="robustness",
        tags=("retries", "exceptions", "boundaries"),
        instruction="""# Bounded retry semantics

Fix `retrying.run_with_retries(operation, max_attempts)`.

Completion criteria:

- `max_attempts` is the total number of permitted calls, not the number of retries after the first call.
- Return immediately with the first successful operation result.
- Retry only `TransientError`; after the final permitted transient failure, re-raise that exact exception.
- Propagate every other exception immediately without retrying it.
- Reject non-positive `max_attempts` with `ValueError` before calling the operation.
""",
        seed_files=_files(retrying_py="""class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    for _ in range(max_attempts + 1):
        try:
            return operation()
        except Exception:
            pass
    return None
"""),
        reference_files=_files(retrying_py="""class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")
    for attempt in range(max_attempts):
        try:
            return operation()
        except TransientError:
            if attempt + 1 == max_attempts:
                raise
"""),
        acceptance_program=_program("""from retrying import TransientError, run_with_retries

calls = []
failure = TransientError("temporary")
def eventually():
    calls.append(1)
    if len(calls) < 3:
        raise failure
    return "ok"
assert run_with_retries(eventually, 3) == "ok"
assert len(calls) == 3

calls.clear()
last = TransientError("last")
def always_transient():
    calls.append(1)
    raise last
try:
    run_with_retries(always_transient, 2)
except TransientError as error:
    assert error is last
else:
    raise AssertionError("final transient error was swallowed")
assert len(calls) == 2

calls.clear()
fatal = TypeError("fatal")
def non_transient():
    calls.append(1)
    raise fatal
try:
    run_with_retries(non_transient, 5)
except TypeError as error:
    assert error is fatal
else:
    raise AssertionError("non-transient error was swallowed")
assert len(calls) == 1

calls.clear()
try:
    run_with_retries(lambda: calls.append(1), 0)
except ValueError:
    pass
else:
    raise AssertionError("non-positive attempts were accepted")
assert calls == []
"""),
    ),
    TaskSpec(
        id="atomic-batch-update",
        title="Atomic in-place batch update",
        category="integration",
        tags=("atomicity", "state", "exceptions"),
        instruction="""# Atomic batch update

Fix `batch.apply_updates(state, updates, validate)`.

Completion criteria:

- Validate every `(key, value)` before changing `state`.
- If all values are valid, apply the updates and return the original `state` object.
- If validation raises, propagate the exact exception and leave `state` completely unchanged.
- Iterate `updates` only once; callers may provide a one-shot iterable.
- Preserve keys not named by an update.
""",
        seed_files=_files(batch_py="""def apply_updates(state, updates, validate):
    for key, value in updates:
        validate(key, value)
        state[key] = value
    return state
"""),
        reference_files=_files(batch_py="""def apply_updates(state, updates, validate):
    pending = []
    for key, value in updates:
        validate(key, value)
        pending.append((key, value))
    state.update(pending)
    return state
"""),
        acceptance_program=_program("""from batch import apply_updates

state = {"keep": 1, "replace": 2}
identity = state
seen = []
result = apply_updates(state, iter([("replace", 3), ("new", 4)]), lambda k, v: seen.append((k, v)))
assert result is identity
assert state == {"keep": 1, "replace": 3, "new": 4}
assert seen == [("replace", 3), ("new", 4)]

class Invalid(ValueError):
    pass

state = {"keep": 1, "replace": 2}
before = state.copy()
failure = Invalid("bad value")
def validate(key, value):
    if key == "bad":
        raise failure
try:
    apply_updates(state, iter([("replace", 9), ("bad", 0), ("later", 5)]), validate)
except Invalid as error:
    assert error is failure
else:
    raise AssertionError("validation failure was swallowed")
assert state == before
"""),
    ),
    TaskSpec(
        id="single-pass-first-match",
        title="Single-pass first matching record",
        category="algorithmic",
        tags=("iterators", "side-effects", "single-pass"),
        instruction="""# Single-pass first match

Fix `matching.first_match(records, predicate)`.

Completion criteria:

- Return the first record for which `predicate(record)` is truthy.
- Return `None` when no record matches.
- Consume `records` at most once so one-shot iterators work.
- Call `predicate` exactly once for each inspected record and stop inspecting immediately after the first match.
- Do not materialize the entire iterable.
""",
        seed_files=_files(matching_py="""def first_match(records, predicate):
    if any(predicate(record) for record in records):
        return next(record for record in records if predicate(record))
    return None
"""),
        reference_files=_files(matching_py="""def first_match(records, predicate):
    for record in records:
        if predicate(record):
            return record
    return None
"""),
        acceptance_program=_program("""from matching import first_match

seen = []
def predicate(value):
    seen.append(value)
    return value == 3
assert first_match(iter([1, 2, 3, 4]), predicate) == 3
assert seen == [1, 2, 3]

seen.clear()
assert first_match((value for value in [1, 2]), predicate) is None
assert seen == [1, 2]

class ExplodingTail:
    def __iter__(self):
        yield "match"
        raise AssertionError("iterated past first match")
assert first_match(ExplodingTail(), lambda value: value == "match") == "match"
"""),
    ),
)

_BY_ID = {task.id: task for task in _TASKS}
if len(_BY_ID) != len(_TASKS):
    raise ValueError("task catalog contains duplicate IDs")


def list_tasks() -> tuple[TaskSpec, ...]:
    return _TASKS


def get_task(task_id: str) -> TaskSpec:
    try:
        return _BY_ID[task_id]
    except KeyError as exc:
        raise KeyError(f"unknown task: {task_id}") from exc
