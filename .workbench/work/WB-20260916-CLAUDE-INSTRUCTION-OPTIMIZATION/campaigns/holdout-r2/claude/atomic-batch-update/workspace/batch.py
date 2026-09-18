def apply_updates(state, updates, validate):
    # Materialize once so one-shot iterables work, and validate everything
    # before touching state so a failure leaves it unchanged.
    pending = []
    for key, value in updates:
        validate(key, value)
        pending.append((key, value))
    for key, value in pending:
        state[key] = value
    return state
