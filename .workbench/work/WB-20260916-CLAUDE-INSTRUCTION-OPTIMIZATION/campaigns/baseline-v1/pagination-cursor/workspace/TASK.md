# Pagination cursor termination

Fix `pagination.collect_pages(fetch_page, page_size)` where `fetch_page(cursor, page_size)` returns `(items, next_cursor)`.

Completion criteria:

- Start with cursor `None` and concatenate pages in order.
- Stop exactly when `next_cursor` is `None`, including after a full final page.
- Empty sources return an empty list after one fetch.
- Never repeat a cursor or request another page after termination.
