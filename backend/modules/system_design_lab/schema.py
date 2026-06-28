from __future__ import annotations
import sqlite3
from .seed import seed_system_design_topics


def create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_design_topics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brief TEXT NOT NULL,
            category TEXT NOT NULL,
            scale TEXT NOT NULL DEFAULT 'N/A',
            difficulty TEXT NOT NULL,
            is_lld INTEGER NOT NULL DEFAULT 0,
            subtopics_json TEXT NOT NULL DEFAULT '[]',
            is_custom INTEGER NOT NULL DEFAULT 0
        )
    """)


def register(cursor: sqlite3.Cursor) -> None:
    """Create tables and seed initial data. Called from init_db."""
    create_tables(cursor)
    seed_system_design_topics(cursor)
