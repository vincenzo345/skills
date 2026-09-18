import operator


class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    try:
        attempts = operator.index(max_attempts)
    except TypeError:
        raise ValueError(
            f"max_attempts must be a positive integer, got {max_attempts!r}"
        ) from None
    if attempts < 1:
        raise ValueError(
            f"max_attempts must be a positive integer, got {max_attempts!r}"
        )
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except TransientError:
            if attempt == attempts:
                raise
