class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    if not isinstance(value, str):
        raise TypeError(f"port must be a str, not {type(value).__name__}")
    # int() also accepts whitespace, signs, underscores and non-ASCII digits;
    # only plain ASCII decimal strings are valid ports.
    if not (value.isascii() and value.isdigit()):
        raise ConfigError("port", value)
    # Strip leading zeros and cap the length so huge inputs never reach
    # int()'s digit limit, which raises a plain ValueError.
    digits = value.lstrip("0")
    if len(digits) > 5:
        raise ConfigError("port", value)
    port = int(digits or "0")
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
