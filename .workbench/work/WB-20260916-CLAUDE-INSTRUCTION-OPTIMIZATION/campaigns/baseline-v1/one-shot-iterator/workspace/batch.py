def describe(values):
    count = 0
    total = 0
    for value in values:
        count += 1
        total += value
    return {"count": count, "total": total}
