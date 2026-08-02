#!/usr/bin/env python3
"""Richard OS — backup & restore (os export / os import).
Exports all SQLite DBs to JSON in 06-data/backups/ (portable, cross-platform)."""
import sqlite3, json, sys
from pathlib import Path
from datetime import datetime

DATA = Path(__file__).resolve().parent.parent / "06-data"
BACKUP = DATA / "backups"

def export():
    BACKUP.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = {}
    for db_file in sorted(DATA.glob("*.db")):
        if db_file.name == "approvals.db":
            continue
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        out[db_file.name] = {}
        for t in tables:
            rows = [dict(r) for r in conn.execute(f"SELECT * FROM {t}").fetchall()]
            out[db_file.name][t] = rows
        conn.close()
    path = BACKUP / f"backup-{stamp}.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"✓ Exported {len(out)} databases → {path.name}")

def import_backup(path_str):
    path = Path(path_str)
    if not path.exists():
        print(f"❌ No backup at {path}")
        return
    data = json.loads(path.read_text())
    for db_name, tables in data.items():
        db_path = DATA / db_name
        conn = sqlite3.connect(db_path)
        for table, rows in tables.items():
            if not rows:
                continue
            cols = ", ".join(rows[0].keys())
            ph = ", ".join("?" * len(rows[0]))
            conn.execute(f"DELETE FROM {table}")
            conn.executemany(f"INSERT INTO {table} ({cols}) VALUES ({ph})",
                             [list(r.values()) for r in rows])
        conn.commit()
        conn.close()
        print(f"✓ Restored {db_name} ({len(tables)} tables)")

def list_backups():
    BACKUP.mkdir(exist_ok=True)
    files = sorted(BACKUP.glob("backup-*.json"))
    if not files:
        print("(no backups yet — run: python3 scripts/backup.py export)")
        return
    print("Backups:")
    for f in files:
        print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "export":
        export()
    elif cmd == "import" and len(sys.argv) > 2:
        import_backup(sys.argv[2])
    elif cmd == "list":
        list_backups()
    else:
        print("Usage: python3 scripts/backup.py [export|import <file>|list]")
