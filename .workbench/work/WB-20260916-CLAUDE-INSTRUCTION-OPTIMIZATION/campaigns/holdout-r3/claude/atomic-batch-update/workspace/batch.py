def apply_updates(state, updates, validate):
    pending = list(updates)
    for key, value in pending:
        validate(key, value)
    for key, value in pending:
        state[key] = value
    return state
