from collections.abc import Mapping

REDACTED = "[REDACTED]"


def safe_diagnostic(error, secrets):
    message = f"{type(error).__name__}: {error}"

    if secrets is None:
        return message
    values = secrets.values() if isinstance(secrets, Mapping) else secrets
    needles = {str(value) for value in values if value is not None and str(value) != ""}
    if not needles:
        return message

    # Mark every character covered by any occurrence of any secret, including
    # overlapping occurrences, all measured against the original message so
    # that overlapping secrets cannot leave partial fragments behind.
    covered = [False] * len(message)
    for needle in needles:
        start = message.find(needle)
        while start != -1:
            for index in range(start, start + len(needle)):
                covered[index] = True
            start = message.find(needle, start + 1)

    parts = []
    index = 0
    while index < len(message):
        if covered[index]:
            parts.append(REDACTED)
            while index < len(message) and covered[index]:
                index += 1
        else:
            parts.append(message[index])
            index += 1
    return "".join(parts)
