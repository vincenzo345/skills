def collect_pages(fetch_page, page_size: int = 2):
    result = []
    cursor = None
    seen = set()
    while True:
        items, next_cursor = fetch_page(cursor, page_size)
        result.extend(items)
        if next_cursor is None:
            return result
        if next_cursor in seen:
            raise RuntimeError(f"cursor {next_cursor!r} was already requested")
        seen.add(next_cursor)
        cursor = next_cursor
