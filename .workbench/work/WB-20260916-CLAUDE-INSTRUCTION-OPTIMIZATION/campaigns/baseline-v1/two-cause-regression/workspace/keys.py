def normalize_key(value):
    return value.strip().lower().replace("-", "_")


def load_mapping(mapping):
    return {normalize_key(key): value for key, value in mapping.items()}


def load_environment(environment, prefix="APP_"):
    normalized_prefix = normalize_key(prefix)
    loaded = {}
    for key, value in environment.items():
        normalized = normalize_key(key)
        if normalized.startswith(normalized_prefix):
            loaded[normalized[len(normalized_prefix):]] = value
    return loaded
