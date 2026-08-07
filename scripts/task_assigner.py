#!/usr/bin/env python3
"""
scripts/task_assigner.py - #10 Task Manager real assign service
Assigns a task to the best agent from the Neural Collaboration roster,
by keyword/skill matching (agent dept + role words vs task title).
Persists assignments to 06-data/assignments.db (assignments table).
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "assignments.db"

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
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, agent TEXT, dept TEXT,
        reason TEXT, status TEXT DEFAULT 'assigned', created_at TEXT);
    """)
    c.commit(); c.close()

def _roster():
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from collab_engine import collab_graph
        g = collab_graph()
        return g.get("nodes", [])
    except Exception:
        return []

# keyword -> agent dept/role hints (task type -> who should own it)
HINTS = {
    "email|inbox|reply|triage": "email-agent",
    "calendar|meeting|schedule|event": "calendar-agent",
    "remind|follow-up|due": "reminder-agent",
    "code|backend|api|database|bug|refactor": "backend",
    "frontend|ui|component|design": "frontend",
    "test|qa|quality": "tester",
    "invoice|payment|expense|finance": "invoicing",
    "recruit|hiring|cv|interview": "recruiter",
    "content|post|blog|social": "content-ops",
    "lead|pipeline|prospect|crm": "recruiter",
    "health|workout|steps|sleep": "health-agent",
    "trip|travel|flight|hotel": "travel-agent",
    "shopping|buy|grocery": "shopping-agent",
    "plan|strategy|goal": "planner-ai",
    "workflow|automation": "workflow-engine",
}

def assign_task(title, dept=None):
    init_db()
    roster = _roster()
    if not roster:
        return {"ok": False, "error": "no agent roster"}
    t = title.lower()
    chosen = None; reason = ""
    # 1) explicit dept -> agent in that dept
    if dept:
        matches = [a for a in roster if a.get("dept") == dept]
        if matches:
            chosen = matches[0]["id"]; reason = f"explicit dept {dept}"
    # 2) keyword hints
    if not chosen:
        for pattern, agent in HINTS.items():
            if re.search(pattern, t):
                chosen = agent; reason = f"matched '{pattern}'"
                break
    # 3) fallback: agent with best role-word overlap
    if not chosen:
        words = set(re.findall(r'[a-z0-9]+', t))
        best = None; best_n = 0
        for a in roster:
            blob = (a.get("dept","") + " " + a.get("role","") + " " + a.get("id","")).lower()
            n = len(words & set(re.findall(r'[a-z0-9]+', blob)))
            if n > best_n:
                best_n = n; best = a["id"]
        chosen = best or "task-manager"; reason = "best word overlap" if best else "default task-manager"
    dept_of = next((a.get("dept","") for a in roster if a.get("id")==chosen), dept or "")
    c = _conn()
    c.execute("INSERT INTO assignments (task, agent, dept, reason, status, created_at) VALUES (?,?,?,?,?,?)",
              (title, chosen, dept_of, reason, "assigned", _now()))
    try:
        import sys as _eb
        _eb.path.insert(0, str(ROOT / "scripts"))
        from system_services import publish
        publish("task.created", f"{title} -> {chosen}")
    except Exception:
        pass
    c.commit()
    aid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return {"ok": True, "assignment_id": aid, "task": title, "agent": chosen,
            "dept": dept_of, "reason": reason}

def list_assignments(limit=20):
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM assignments ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "assignments": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assign", nargs="+", metavar="TITLE")
    ap.add_argument("--dept", metavar="DEPT")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.assign:
        print(json.dumps(assign_task(" ".join(args.assign), args.dept), indent=2)); return
    if args.list:
        d = list_assignments()
        for a in d["assignments"]:
            print(f"  [{a['id']}] {a['task'][:40]:42s} -> {a['agent']:20s} ({a['dept']})")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
