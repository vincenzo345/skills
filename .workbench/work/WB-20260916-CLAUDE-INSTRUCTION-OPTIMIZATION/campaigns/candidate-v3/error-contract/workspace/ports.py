import re


class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


_DECIMAL = re.compile(r"[0-9]+")


def parse_port(value):
    # Only plain ASCII decimal strings are accepted; int() alone would also
    # take signs, whitespace, underscores, and non-ASCII digits.
    if not isinstance(value, str) or not _DECIMAL.fullmatch(value):
        raise ConfigError("port", value)
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
