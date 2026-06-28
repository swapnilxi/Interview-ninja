from __future__ import annotations
import sqlite3
from .seed import seed_dsa_topics


def create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dsa_topics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brief TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            prerequisites_json TEXT NOT NULL DEFAULT '[]',
            subtopics_json TEXT NOT NULL DEFAULT '[]',
            is_custom INTEGER NOT NULL DEFAULT 0
        )
    """)


def register(cursor: sqlite3.Cursor) -> None:
    """Create tables and seed initial data. Called from init_db."""
    create_tables(cursor)
    seed_dsa_topics(cursor)
