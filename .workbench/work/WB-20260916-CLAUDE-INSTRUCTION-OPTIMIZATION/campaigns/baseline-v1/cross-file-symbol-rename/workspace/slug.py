def to_slug(value: str) -> str:
    return "-".join(value.strip().lower().split())


# Backward-compatible alias for the previous public name.
slugify = to_slug
