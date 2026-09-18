# SQLite transaction boundary

Fix `transfers.transfer(conn, source_id, target_id, amount, fail_after_debit=False)` so the two balance updates are atomic.

Completion criteria:

- A successful transfer debits the source and credits the target exactly once.
- If any failure occurs after the debit, neither balance change is committed.
- Propagate the failure and leave the connection usable.
- Use the supplied connection; do not close it or create another database.
