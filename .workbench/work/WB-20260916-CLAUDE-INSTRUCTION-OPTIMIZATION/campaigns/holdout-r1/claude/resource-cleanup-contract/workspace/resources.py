def read_payload(opener, path):
    handle = opener(path)
    try:
        payload = handle.read()
    except BaseException as read_error:
        try:
            handle.close()
        except BaseException:
            # Keep the read failure primary; the close failure stays attached
            # as __context__.
            raise read_error
        raise
    handle.close()
    return payload
