"""
db.py
SQLite persistence for alert history.
Kept as a separate module so the storage layer can be swapped
(e.g. for Postgres) without touching the UI or monitoring logic.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "alerts.db"


def init_db():
    """Create the alerts table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def insert_alert(source: str, severity: str, message: str):
    """Persist a single alert row."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO alerts (timestamp, source, severity, message) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), source, severity, message),
    )
    conn.commit()
    conn.close()


def get_alerts(limit: int = 100):
    """Return the most recent alerts, newest first, as a list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_alerts():
    """Wipe alert history (used by the 'Clear history' button in the UI)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()
