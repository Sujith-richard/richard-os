#!/usr/bin/env python3
"""Richard OS — create all 5 systems-of-record databases."""
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "06-data"
DATA.mkdir(exist_ok=True)

SCHEMAS = {
    "second_brain.db": """
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT, source TEXT, status TEXT DEFAULT 'inbox',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, status TEXT DEFAULT 'active', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "pm.db": """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, project TEXT, status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium', due TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, client TEXT, value REAL DEFAULT 0, status TEXT DEFAULT 'prospect'
        );
    """,
    "finance.db": """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, type TEXT, balance REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT, account TEXT, amount REAL, note TEXT, date TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "crm.db": """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, company TEXT, email TEXT, stage TEXT DEFAULT 'lead'
        );
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, company TEXT, value REAL DEFAULT 0, stage TEXT DEFAULT 'prospect'
        );
    """,
    "creator.db": """
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, platform TEXT, status TEXT DEFAULT 'idea',
            scheduled TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """,
}

for name, sql in SCHEMAS.items():
    conn = sqlite3.connect(DATA / name)
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print(f"  ✓  {name}")

print("\n✓ All 5 systems of record ready.")
