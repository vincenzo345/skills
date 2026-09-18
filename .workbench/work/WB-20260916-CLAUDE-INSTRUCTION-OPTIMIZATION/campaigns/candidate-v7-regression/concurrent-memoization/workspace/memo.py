import threading


class _Pending:
    """One in-flight computation that concurrent callers for a key wait on."""

    __slots__ = ("done", "value", "error")

    def __init__(self):
        self.done = threading.Event()
        self.value = None
        self.error = None


class Memo:
    def __init__(self):
        self._values = {}
        self._pending = {}
        self._lock = threading.Lock()

    def get(self, key, compute):
        with self._lock:
            if key in self._values:
                return self._values[key]
            pending = self._pending.get(key)
            owner = pending is None
            if owner:
                pending = _Pending()
                self._pending[key] = pending

        if not owner:
            pending.done.wait()
            if pending.error is not None:
                raise pending.error
            return pending.value

        # Compute outside the lock so other keys are not blocked.
        try:
            value = compute()
        except BaseException as exc:
            # Drop the in-flight entry without caching, so a later call retries.
            with self._lock:
                del self._pending[key]
            pending.error = exc
            pending.done.set()
            raise

        with self._lock:
            self._values[key] = value
            del self._pending[key]
        pending.value = value
        pending.done.set()
        return value
