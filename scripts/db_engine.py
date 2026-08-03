#!/usr/bin/env python3
"""Richard OS — data engine switcher: sqlite (default) or mysql.
Usage:
  from db_engine import connect, DATA
  conn = connect("pm.db")
Agents keep working unchanged regardless of DB_ENGINE.
"""
import os, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"

def load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def engine():
    load_env()
    return os.environ.get("DB_ENGINE", "sqlite").lower()

def connect(db_name):
    """db_name like 'pm.db'. If engine=mysql, routes to the MySQL server."""
    load_env()
    if engine() == "mysql":
        import pymysql  # optional; install only if you use MySQL
        table = db_name.replace(".db", "")
        return pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASS", ""),
            database=os.environ.get("DB_NAME", "richard_os") or table,
            cursorclass=pymysql.cursors.DictCursor,
        )
    return sqlite3.connect(DATA / db_name)
