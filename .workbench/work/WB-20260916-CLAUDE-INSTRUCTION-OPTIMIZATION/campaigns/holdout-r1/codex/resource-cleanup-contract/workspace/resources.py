def read_payload(opener, path):
    handle = opener(path)
    return handle.read()
