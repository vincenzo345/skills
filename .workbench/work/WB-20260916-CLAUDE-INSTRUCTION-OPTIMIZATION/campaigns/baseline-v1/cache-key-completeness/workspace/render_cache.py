from collections.abc import Mapping, Set


def _freeze(value):
    """Return a hashable, order-insensitive (for mappings/sets) form of value."""
    if isinstance(value, Mapping):
        return ("mapping", frozenset((_freeze(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, list):
        return ("list", tuple(_freeze(item) for item in value))
    if isinstance(value, tuple):
        return ("tuple", tuple(_freeze(item) for item in value))
    if isinstance(value, Set):
        return ("set", frozenset(_freeze(item) for item in value))
    hash(value)  # raise TypeError early for unsupported unhashable values
    return value


class RenderCache:
    def __init__(self):
        self._values = {}

    def render(self, document, options, renderer):
        key = (_freeze(document), _freeze(options))
        if key not in self._values:
            self._values[key] = renderer(document, options)
        return self._values[key]
