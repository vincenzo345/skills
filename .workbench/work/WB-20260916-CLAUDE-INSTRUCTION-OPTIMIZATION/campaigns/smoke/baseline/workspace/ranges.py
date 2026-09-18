def partition(start: int, end: int, size: int) -> list[tuple[int, int]]:
    if size <= 0:
        raise ValueError("size must be positive")
    if start > end:
        return []
    result = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + size - 1, end)
        result.append((cursor, chunk_end))
        cursor = chunk_end + 1
    return result
