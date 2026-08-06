#!/usr/bin/env python3
"""
scripts/agent_lifecycle.py - v4.0 #4 Agent Lifecycle
State machine per agent:
created -> assigned -> thinking -> uses_models -> uses_skills -> uses_tools ->
uses_knowledge -> returns_result -> reviewer_checks -> memory_updated -> sleeps
Persists to 06-data/lifecycle.db: agents + transitions.
"""
import json, sqlite3, pathlib, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "lifecycle.db"

STATES = ["created", "assigned", "thinking", "uses_models", "uses_skills",
          "uses_tools", "uses_knowledge", "returns_result", "reviewer_checks",
          "memory_updated", "sleeps"]

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
    CREATE TABLE IF NOT EXISTS agents (
        name TEXT PRIMARY KEY, dept TEXT, role TEXT, state TEXT DEFAULT 'created',
        state_idx INTEGER DEFAULT 0, started_at TEXT, updated_at TEXT, cycles INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, from_state TEXT, to_state TEXT, at TEXT);
    """)
    c.commit(); c.close()

def _roster():
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from collab_engine import collab_graph
        return collab_graph().get("nodes", [])
    except Exception:
        return []

def start(agent, dept=None, role=""):
    init_db()
    roster = {a["id"]: a for a in _roster()}
    info = roster.get(agent)
    if info:
        dept = dept or info.get("dept", ""); role = role or info.get("role", "")
    c = _conn()
    c.execute("""INSERT OR REPLACE INTO agents (name, dept, role, state, state_idx, started_at, updated_at, cycles)
                 VALUES (?,?,?, 'created', 0, ?, ?, ?)""",
              (agent, dept or "general", role, _now(), _now(), 1))
    c.execute("INSERT INTO transitions (agent, from_state, to_state, at) VALUES (?, 'none', 'created', ?)",
              (agent, _now()))
    c.commit(); c.close()
    return {"ok": True, "agent": agent, "state": "created", "state_idx": 0}

def advance(agent):
    """Move one step forward in the lifecycle. After sleeps, wraps to created (new cycle)."""
    init_db()
    c = _conn()
    a = c.execute("SELECT * FROM agents WHERE name=?", (agent,)).fetchone()
    if not a:
        c.close(); return {"ok": False, "error": "agent not started — call start first"}
    cur = a["state_idx"]
    if cur >= len(STATES) - 1:
        # new cycle
        c.execute("UPDATE agents SET state='created', state_idx=0, cycles=cycles+1, updated_at=? WHERE name=?", (_now(), agent))
        c.execute("INSERT INTO transitions (agent, from_state, to_state, at) VALUES (?, ?, 'created', ?)",
                  (agent, STATES[-1], _now()))
        c.commit(); c.close()
        return {"ok": True, "agent": agent, "from": STATES[-1], "to": "created", "state_idx": 0, "cycles": a["cycles"] + 1}
    nxt = STATES[cur + 1]
    c.execute("UPDATE agents SET state=?, state_idx=?, updated_at=? WHERE name=?", (nxt, cur + 1, _now(), agent))
    c.execute("INSERT INTO transitions (agent, from_state, to_state, at) VALUES (?,?,?,?)",
              (agent, STATES[cur], nxt, _now()))
    c.commit(); c.close()
    return {"ok": True, "agent": agent, "from": STATES[cur], "to": nxt, "state_idx": cur + 1}

def agent_state(agent):
    init_db()
    c = _conn()
    a = c.execute("SELECT * FROM agents WHERE name=?", (agent,)).fetchone()
    tr = c.execute("SELECT * FROM transitions WHERE agent=? ORDER BY id DESC LIMIT 12", (agent,)).fetchall()
    c.close()
    if not a:
        return {"ok": False, "error": "not started"}
    return {"ok": True, "agent": dict(a), "transitions": [dict(t) for t in tr]}

def all_states():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM agents ORDER BY dept, name").fetchall()
    c.close()
    return {"ok": True, "agents": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", metavar="AGENT")
    ap.add_argument("--advance", metavar="AGENT")
    ap.add_argument("--state", metavar="AGENT")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.start:
        print(json.dumps(start(args.start), indent=2)); return
    if args.advance:
        print(json.dumps(advance(args.advance), indent=2)); return
    if args.state:
        d = agent_state(args.state)
        if d.get("ok"):
            print(f"{d['agent']['name']}: {d['agent']['state']} (idx {d['agent']['state_idx']}, cycles {d['agent']['cycles']})")
            for t in d["transitions"][:6]:
                print(f"  {t['from_state']} -> {t['to_state']} @ {t['at']}")
        else:
            print(d)
        return
    if args.all:
        for a in all_states()["agents"]:
            print(f"  {a['name']:22s} {a['state']:16s} idx={a['state_idx']} cycles={a['cycles']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
