"""
Lightweight startup migrations for SQLite.
Add new columns here — they'll be applied automatically on next server start
without touching existing data.

To add a future migration:
  1. Add a new entry to USERS_COLUMNS or SHIFTS_COLUMNS (or a new table dict).
  2. Restart the server — done.
"""

import sqlite3
from sqlalchemy.engine import Engine


def _columns(conn: sqlite3.Connection, table: str) -> set:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _tables(conn: sqlite3.Connection) -> set:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


# Column migrations: (column_name, ALTER TABLE SQL)
USERS_COLUMNS = [
    ("employer",          "ALTER TABLE users ADD COLUMN employer TEXT"),
]

SHIFTS_COLUMNS = [
    ("direct_hours",      "ALTER TABLE shifts ADD COLUMN direct_hours REAL"),
]


def run(engine: Engine) -> None:
    """Called at startup after create_all. Safe to run on every boot."""
    db_path = str(engine.url).replace("sqlite:///", "")
    if not db_path or db_path == ":memory:":
        return

    conn = sqlite3.connect(db_path)
    try:
        existing_tables = _tables(conn)

        if "users" in existing_tables:
            existing = _columns(conn, "users")
            for col, sql in USERS_COLUMNS:
                if col not in existing:
                    conn.execute(sql)

        if "shifts" in existing_tables:
            existing = _columns(conn, "shifts")
            for col, sql in SHIFTS_COLUMNS:
                if col not in existing:
                    conn.execute(sql)

        # Data migrations
        if "users" in existing_tables:
            # Ensure all weekly users start on Monday (pay_period_value=0)
            conn.execute(
                "UPDATE users SET pay_period_value = 0 WHERE pay_period_type = 'weekly'"
            )

        conn.commit()
    finally:
        conn.close()
