def read_payload(opener, path):
    handle = opener(path)
    try:
        payload = handle.read()
    except BaseException:
        # Close, but never let a close failure mask the original read error.
        try:
            handle.close()
        except Exception:
            pass
        raise
    handle.close()
    return payload
