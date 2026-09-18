def normalize_key(value):
    return value.strip().lower().replace("-", "_")


def load_mapping(mapping):
    return {normalize_key(key): value for key, value in mapping.items()}


def load_environment(environment, prefix="APP_"):
    return {
        normalize_key(key[len(prefix):]): value
        for key, value in environment.items()
        if key.startswith(prefix)
    }
