class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")

    for attempt in range(max_attempts):
        try:
            return operation()
        except TransientError:
            if attempt == max_attempts - 1:
                raise
