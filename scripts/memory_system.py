#!/usr/bin/env python3
"""
scripts/memory_system.py - v4.0 #5 Memory System
11-type memory hierarchy: user, conversation, project, department, agent,
tool, workflow, knowledge, experience, long-term, temporary.
Add/get/search per type; promote temporary -> long-term.
Persists to 06-data/memory.db.
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "memory.db"

TYPES = ["user", "conversation", "project", "department", "agent",
         "tool", "workflow", "knowledge", "experience", "long-term", "temporary"]

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
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT, mtype TEXT, content TEXT, tags TEXT DEFAULT '[]',
        importance INTEGER DEFAULT 1, created_at TEXT, updated_at TEXT);
    CREATE INDEX IF NOT EXISTS idx_mtype ON memories(mtype);
    """)
    c.commit(); c.close()

def add(mtype, content, tags=None, importance=1):
    init_db()
    if mtype not in TYPES:
        return {"ok": False, "error": f"type must be one of {TYPES}"}
    c = _conn()
    cur = c.execute("INSERT INTO memories (mtype, content, tags, importance, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                    (mtype, content, json.dumps(tags or []), importance, _now(), _now()))
    c.commit(); c.close()
    return {"ok": True, "id": cur.lastrowid, "mtype": mtype, "content": content[:80]}

def get(mtype=None, limit=50):
    init_db()
    c = _conn()
    if mtype:
        rows = c.execute("SELECT * FROM memories WHERE mtype=? ORDER BY id DESC LIMIT ?", (mtype, limit)).fetchall()
    else:
        rows = c.execute("SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "memories": [dict(r) for r in rows]}

def counts():
    init_db()
    c = _conn()
    out = {}
    for t in TYPES:
        out[t] = c.execute("SELECT COUNT(*) n FROM memories WHERE mtype=?", (t,)).fetchone()["n"]
    c.close()
    return {"ok": True, "counts": out}

def search(query, limit=20):
    init_db()
    c = _conn()
    q = f"%{query}%"
    rows = c.execute("SELECT * FROM memories WHERE content LIKE ? OR tags LIKE ? ORDER BY importance DESC, id DESC LIMIT ?",
                     (q, q, limit)).fetchall()
    c.close()
    return {"ok": True, "query": query, "results": [dict(r) for r in rows]}

def promote(mem_id):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM memories WHERE id=?", (mem_id,)).fetchone()
    if not row:
        c.close(); return {"ok": False, "error": "memory not found"}
    c.execute("UPDATE memories SET mtype='long-term', importance=importance+1, updated_at=? WHERE id=?", (_now(), mem_id))
    c.commit(); c.close()
    return {"ok": True, "id": mem_id, "mtype": "long-term", "content": row["content"][:60]}

def seed_from_second_brain():
    """Pull captures/inbox from second_brain into typed memories (once)."""
    sb = ROOT / "06-data" / "second_brain.db"
    if not sb.exists():
        return 0
    init_db()
    c = _conn()
    if c.execute("SELECT COUNT(*) n FROM memories").fetchone()["n"] > 0:
        c.close(); return 0
    con = sqlite3.connect(sb); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM captures ORDER BY id DESC LIMIT 40").fetchall()
    con.close()
    n = 0
    for r in rows:
        content = " | ".join(str(r[k]) for k in r.keys() if r[k] not in (None, ""))
        c.execute("INSERT INTO memories (mtype, content, importance, created_at, updated_at) VALUES (?,?,?,?,?)",
                  ("knowledge", content[:500], 1, _now(), _now()))
        n += 1
    c.commit(); c.close()
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", nargs=3, metavar=("TYPE", "CONTENT", "IMPORTANCE"))
    ap.add_argument("--get", metavar="TYPE")
    ap.add_argument("--counts", action="store_true")
    ap.add_argument("--search", metavar="Q")
    ap.add_argument("--promote", metavar="ID")
    ap.add_argument("--seed", action="store_true")
    args = ap.parse_args()
    if args.add:
        print(json.dumps(add(args.add[0], args.add[1], importance=int(args.add[2])), indent=2)); return
    if args.get:
        d = get(args.get)
        for m in d["memories"][:8]:
            print(f"  [{m['id']}] {m['mtype']:12s} {m['content'][:60]}")
        return
    if args.counts:
        for k, v in counts()["counts"].items():
            print(f"  {k:14s} {v}")
        return
    if args.search:
        for m in search(args.search)["results"][:8]:
            print(f"  [{m['id']}] {m['mtype']:12s} {m['content'][:60]}")
        return
    if args.promote:
        print(json.dumps(promote(int(args.promote)), indent=2)); return
    if args.seed:
        print(f"seeded {seed_from_second_brain()} memories from second_brain"); return
    ap.print_help()

if __name__ == "__main__":
    main()
