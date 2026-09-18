import threading


class _InFlight:
    def __init__(self):
        self.done = threading.Event()
        self.value = None
        self.error = None


class Memo:
    def __init__(self):
        self._values = {}
        self._in_flight = {}
        self._lock = threading.Lock()

    def get(self, key, compute):
        with self._lock:
            if key in self._values:
                return self._values[key]
            flight = self._in_flight.get(key)
            owner = flight is None
            if owner:
                flight = _InFlight()
                self._in_flight[key] = flight

        if not owner:
            flight.done.wait()
            if flight.error is not None:
                raise flight.error
            return flight.value

        # Run compute() outside the lock so other keys are not blocked.
        try:
            value = compute()
        except BaseException as exc:
            flight.error = exc
            with self._lock:
                # Drop the in-flight entry without caching, so a later call retries.
                del self._in_flight[key]
            flight.done.set()
            raise

        flight.value = value
        with self._lock:
            self._values[key] = value
            del self._in_flight[key]
        flight.done.set()
        return value
