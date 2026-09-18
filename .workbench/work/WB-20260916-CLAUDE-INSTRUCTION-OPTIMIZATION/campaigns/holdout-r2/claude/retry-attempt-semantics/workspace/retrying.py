class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be positive, got {max_attempts!r}")
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except TransientError:
            if attempt == max_attempts:
                raise
