class TransientError(RuntimeError):
    pass


def run_with_retries(operation, max_attempts):
    for _ in range(max_attempts + 1):
        try:
            return operation()
        except Exception:
            pass
    return None
