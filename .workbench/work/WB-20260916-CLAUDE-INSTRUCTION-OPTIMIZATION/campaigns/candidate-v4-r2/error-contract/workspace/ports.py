import re

_DECIMAL = re.compile(r"[0-9]+")


class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    # Non-string input is a caller bug: re.fullmatch raises TypeError, which
    # is deliberately left to propagate rather than being reported as config.
    if not _DECIMAL.fullmatch(value):
        raise ConfigError("port", value)
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
