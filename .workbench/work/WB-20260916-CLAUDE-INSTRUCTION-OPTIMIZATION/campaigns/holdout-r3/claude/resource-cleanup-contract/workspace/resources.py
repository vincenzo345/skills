def read_payload(opener, path):
    handle = opener(path)
    try:
        result = handle.read()
    except BaseException:
        try:
            handle.close()
        except Exception:
            # A close failure must not mask the original read failure.
            pass
        raise
    handle.close()
    return result
