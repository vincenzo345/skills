import re


_DECIMAL = re.compile(r"[0-9]+")


class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    if not isinstance(value, str):
        raise TypeError(f"port value must be a str, not {type(value).__name__}")
    if not _DECIMAL.fullmatch(value):
        raise ConfigError("port", value)
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
