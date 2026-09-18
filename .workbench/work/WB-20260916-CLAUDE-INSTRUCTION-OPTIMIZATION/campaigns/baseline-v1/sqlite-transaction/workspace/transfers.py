import sqlite3

_SAVEPOINT = "transfer_atomic"


def transfer(conn, source_id, target_id, amount, fail_after_debit=False):
    # A savepoint gives an explicit transaction boundary regardless of the
    # connection's isolation_level/autocommit configuration.
    conn.execute(f"SAVEPOINT {_SAVEPOINT}")
    try:
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, source_id))
        if fail_after_debit:
            raise RuntimeError("injected failure")
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, target_id))
    except BaseException:
        try:
            conn.execute(f"ROLLBACK TO {_SAVEPOINT}")
            conn.execute(f"RELEASE {_SAVEPOINT}")
        except sqlite3.Error:
            # SQLite may already have rolled back the whole transaction
            # (e.g. on SQLITE_FULL); make sure nothing stays open.
            if conn.in_transaction:
                conn.rollback()
        raise
    conn.execute(f"RELEASE {_SAVEPOINT}")
    conn.commit()
