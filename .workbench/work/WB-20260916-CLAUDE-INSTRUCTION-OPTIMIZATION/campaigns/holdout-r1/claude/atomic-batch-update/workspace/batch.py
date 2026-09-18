def apply_updates(state, updates, validate):
    # Consume updates once and validate everything before touching state, so a
    # failing validation leaves state unchanged.
    pending = []
    for key, value in updates:
        validate(key, value)
        pending.append((key, value))
    for key, value in pending:
        state[key] = value
    return state
