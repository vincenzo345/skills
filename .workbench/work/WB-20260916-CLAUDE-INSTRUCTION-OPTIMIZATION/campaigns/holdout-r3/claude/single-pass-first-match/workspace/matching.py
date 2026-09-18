def first_match(records, predicate):
    for record in records:
        if predicate(record):
            return record
    return None
