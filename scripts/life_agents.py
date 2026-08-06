#!/usr/bin/env python3
"""
scripts/life_agents.py - #19 Personal Assistant: Health + Travel + Shopping
Three trackers (fake-data-first, seeded) with add/list/overview actions.
Persists to 06-data/life.db: health, trips, shopping.
"""
import sqlite3, pathlib, datetime, json, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "life.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS health (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, kind TEXT, detail TEXT,
        metric REAL, note TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT, destination TEXT, start_date TEXT,
        end_date TEXT, budget REAL, status TEXT DEFAULT 'planned', notes TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS shopping (
        id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, category TEXT,
        qty INTEGER DEFAULT 1, status TEXT DEFAULT 'open', price REAL, created_at TEXT);
    """)
    c.commit(); c.close()

def seed():
    init_db()
    c = _conn()
    if c.execute("SELECT COUNT(*) n FROM health").fetchone()["n"] == 0:
        c.execute("INSERT INTO health (date,kind,detail,metric,note) VALUES ('2026-08-05','workout','gym - upper body',60,'pull day')")
        c.execute("INSERT INTO health (date,kind,detail,metric,note) VALUES ('2026-08-06','steps','walk',12000,'daily')")
    if c.execute("SELECT COUNT(*) n FROM trips").fetchone()["n"] == 0:
        c.execute("INSERT INTO trips (destination,start_date,end_date,budget,status,notes) VALUES ('Mumbai','2026-09-12','2026-09-15',15000,'planned','client visit')")
    if c.execute("SELECT COUNT(*) n FROM shopping").fetchone()["n"] == 0:
        c.execute("INSERT INTO shopping (item,category,qty,status,price) VALUES ('Mechanical keyboard','electronics',1,'open',2500)")
        c.execute("INSERT INTO shopping (item,category,qty,status,price) VALUES ('Protein powder','health',1,'bought',1800)")
    c.commit(); c.close()
    return {"health": 2, "trips": 1, "shopping": 2}

# ---------- health ----------
def add_health(date, kind, detail, metric=None, note=""):
    init_db(); c = _conn()
    c.execute("INSERT INTO health (date,kind,detail,metric,note,created_at) VALUES (?,?,?,?,?,?)",
              (date, kind, detail, metric, note, _now()))
    c.commit(); c.close()
    return {"ok": True, "added": {"date": date, "kind": kind, "detail": detail}}

def list_health(limit=10):
    init_db(); c = _conn()
    rows = c.execute("SELECT * FROM health ORDER BY date DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "entries": [dict(r) for r in rows]}

# ---------- travel ----------
def add_trip(destination, start_date, end_date, budget=None, notes=""):
    init_db(); c = _conn()
    c.execute("INSERT INTO trips (destination,start_date,end_date,budget,status,notes,created_at) VALUES (?,?,?,?,?,?,?)",
              (destination, start_date, end_date, budget, "planned", notes, _now()))
    c.commit(); c.close()
    return {"ok": True, "added": {"destination": destination, "start": start_date}}

def list_trips():
    init_db(); c = _conn()
    rows = c.execute("SELECT * FROM trips ORDER BY start_date").fetchall()
    c.close()
    return {"ok": True, "trips": [dict(r) for r in rows]}

# ---------- shopping ----------
def add_shopping(item, category="general", qty=1, price=None):
    init_db(); c = _conn()
    c.execute("INSERT INTO shopping (item,category,qty,status,price,created_at) VALUES (?,?,?,?,?,?)",
              (item, category, qty, "open", price, _now()))
    c.commit(); c.close()
    return {"ok": True, "added": {"item": item, "qty": qty}}

def toggle_shopping(item_id):
    init_db(); c = _conn()
    c.execute("UPDATE shopping SET status='bought' WHERE id=?", (item_id,))
    c.commit(); c.close()
    return {"ok": True, "id": item_id, "status": "bought"}

def list_shopping():
    init_db(); c = _conn()
    rows = c.execute("SELECT * FROM shopping ORDER BY status DESC, id").fetchall()
    c.close()
    return {"ok": True, "items": [dict(r) for r in rows]}

# ---------- overview ----------
def overview():
    init_db(); c = _conn()
    h = c.execute("SELECT COUNT(*) n FROM health").fetchone()["n"]
    t = c.execute("SELECT COUNT(*) n FROM trips").fetchone()["n"]
    s = c.execute("SELECT COUNT(*) n FROM shopping").fetchone()["n"]
    open_s = c.execute("SELECT COUNT(*) n FROM shopping WHERE status='open'").fetchone()["n"]
    c.close()
    return {"ok": True, "health_entries": h, "trips": t, "shopping_items": s, "shopping_open": open_s}

def main():
    ap = argparse.ArgumentParser(description="Richard OS Life Agents (#19)")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--overview", action="store_true")
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--trips", action="store_true")
    ap.add_argument("--shopping", action="store_true")
    args = ap.parse_args()
    if args.seed: print(json.dumps(seed(), indent=2)); return
    if args.overview: print(json.dumps(overview(), indent=2)); return
    if args.health: print(json.dumps(list_health(), indent=2)); return
    if args.trips: print(json.dumps(list_trips(), indent=2)); return
    if args.shopping: print(json.dumps(list_shopping(), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
