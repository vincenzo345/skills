def apply_updates(state, updates, validate):
    validated_updates = []
    for key, value in updates:
        validate(key, value)

        validated_updates.append((key, value))

    for key, value in validated_updates:
        state[key] = value

    return state
