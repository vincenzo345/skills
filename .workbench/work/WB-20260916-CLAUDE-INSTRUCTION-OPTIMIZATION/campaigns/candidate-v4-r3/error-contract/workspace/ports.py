class ConfigError(ValueError):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(f"invalid {key}: {value}")


def parse_port(value):
    # Accept only plain ASCII decimal digits; int() would also allow
    # whitespace, signs, underscores and non-ASCII digits.
    if not isinstance(value, str) or not (value.isascii() and value.isdigit()):
        raise ConfigError("port", value)
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigError("port", value)
    return port
