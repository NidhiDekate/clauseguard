# logging_db.py
# structured sqlite logging - one row per real request. what came in, what
# came out, how long it took. this is what lets you actually debug
# something later instead of guessing what happened.

import sqlite3
import time
from pathlib import Path

DB_PATH = Path("data/processed/requests.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            document_type TEXT,
            document_length INTEGER,
            num_categories INTEGER,
            num_concerning INTEGER,
            num_neutral INTEGER,
            num_favorable INTEGER,
            num_not_addressed INTEGER,
            latency_seconds REAL,
            error TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_request(document_type, document_length, decision_report, latency_seconds, error=None):
    init_db()

    concerning = sum(1 for f in decision_report if f.get("label") == "concerning")
    neutral = sum(1 for f in decision_report if f.get("label") == "neutral")
    favorable = sum(1 for f in decision_report if f.get("label") == "favorable")
    not_addressed = sum(1 for f in decision_report if f.get("status") == "not_addressed")

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO requests
        (timestamp, document_type, document_length, num_categories, num_concerning,
         num_neutral, num_favorable, num_not_addressed, latency_seconds, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            time.strftime("%Y-%m-%d %H:%M:%S"),
            document_type,
            document_length,
            len(decision_report),
            concerning,
            neutral,
            favorable,
            not_addressed,
            latency_seconds,
            error,
        ),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # quick manual check - log a fake request, then read it back
    log_request(
        document_type="lease",
        document_length=2000,
        decision_report=[{"label": "concerning"}, {"label": "neutral"}, {"status": "not_addressed"}],
        latency_seconds=12.4,
    )

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM requests").fetchall()
    for row in rows:
        print(row)
    conn.close()
