def format_label(name: str, uppercase: bool = False, *, prefix: str = "") -> str:
    label = name if prefix == "" else prefix + name
    return label.upper() if uppercase else label
