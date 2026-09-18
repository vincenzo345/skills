class ConfigError(ValueError):
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
