def read_payload(opener, path):
    handle = opener(path)
    try:
        result = handle.read()
    except BaseException:
        try:
            handle.close()
        except BaseException:
            # Cleanup must not replace the exception raised by read().
            pass
        raise

    handle.close()
    return result
