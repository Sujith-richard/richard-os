#!/usr/bin/env python3
"""scripts/audit.py - Phase I4 Audit Logs
Log every API action to 06-data/audit.db: timestamp, endpoint, method, user, status.
"""
import json, sqlite3, pathlib, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "audit.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, method TEXT, path TEXT,
        user TEXT, status INTEGER, detail TEXT)""")
    c.commit(); c.close()

def log(method, path, user="anonymous", status=200, detail=""):
    init_db()
    c = _conn()
    c.execute("INSERT INTO audit (ts, method, path, user, status, detail) VALUES (?,?,?,?,?,?)",
              (_now(), method, path, user, status, str(detail)[:200]))
    c.commit(); c.close()

def recent(limit=50):
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "entries": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", nargs=5, metavar=("METHOD","PATH","USER","STATUS","DETAIL"))
    ap.add_argument("--recent", type=int, default=20)
    args = ap.parse_args()
    if args.log:
        print(json.dumps(log(*args.log), indent=2)); return
    if args.recent:
        for e in recent(args.recent)["entries"]:
            print(f"  [{e['id']}] {e['ts']} {e['method']:6s} {e['path'][:40]:42s} {e['user']:10s} {e['status']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
