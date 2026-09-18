def load_config(keys, cli, environment, file_values, defaults):
    sources = (cli, environment, file_values, defaults)
    result = {}
    for key in keys:
        value = None
        for source in sources:
            if key in source:
                value = source[key]
                break
        result[key] = value
    return result
