def read_payload(opener, path):
    handle = opener(path)
    try:
        payload = handle.read()
    except BaseException:
        try:
            handle.close()
        except BaseException:
            pass
        raise

    handle.close()
    return payload
