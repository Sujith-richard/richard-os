#!/usr/bin/env python3
"""
scripts/collab_engine.py - #17 Neural Collaboration
WHO talks to WHOM through the graph, not point-to-point.
A shared message bus: agents send/read messages, validate each other's work,
and the collab graph reflects live edge activity.
Persists to 06-data/collab.db: agents, messages, edges.
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "collab.db"

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
        name TEXT PRIMARY KEY, dept TEXT, role TEXT, model TEXT, autonomy INTEGER, active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, recipient TEXT, subject TEXT,
        body TEXT, created_at TEXT, read INTEGER DEFAULT 0, validated INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS edges (
        sender TEXT, recipient TEXT, msgs INTEGER DEFAULT 0, last_at TEXT,
        PRIMARY KEY (sender, recipient));
    """)
    c.commit(); c.close()

# Agent roster matching the real OS agents (company + personal + persona + core)
ROSTER = [
    # core engines
    ("executive-ai", "core", "CEO brief", "deepseek-v4-flash-free", 2),
    ("planner-ai", "core", "goal -> plan", "deepseek-v4-flash-free", 3),
    ("task-manager", "core", "assigns tasks", "deepseek-v4-flash-free", 3),
    ("workflow-engine", "core", "runs workflows", "deepseek-v4-flash-free", 3),
    ("model-orchestrator", "core", "routes models", "deepseek-v4-flash-free", 3),
    ("memory-engine", "core", "second brain", "deepseek-v4-flash-free", 3),
    ("knowledge-engine", "core", "knowledge graph", "deepseek-v4-flash-free", 3),
    ("quality-checker", "core", "validates work", "deepseek-v4-flash-free", 2),
    # company
    ("recruiter", "hr", "screens CVs", "deepseek-v4-flash-free", 2),
    ("payroll", "hr", "salary calc", "deepseek-v4-flash-free", 3),
    ("onboarding", "hr", "docs", "deepseek-v4-flash-free", 2),
    ("backend", "development", "API work", "deepseek-v4-flash-free", 3),
    ("frontend", "development", "UI work", "deepseek-v4-flash-free", 3),
    ("tester", "development", "test cases", "deepseek-v4-flash-free", 2),
    ("invoicing", "finance", "invoices", "deepseek-v4-flash-free", 2),
    ("expense", "finance", "expenses", "deepseek-v4-flash-free", 3),
    ("fulfillment", "operations", "delivery", "deepseek-v4-flash-free", 3),
    ("support", "operations", "tickets", "deepseek-v4-flash-free", 2),
    # personal
    ("email-agent", "personal", "triage", "deepseek-v4-flash-free", 2),
    ("calendar-agent", "personal", "events", "deepseek-v4-flash-free", 2),
    ("reminder-agent", "personal", "follow-ups", "deepseek-v4-flash-free", 3),
    # persona specialists
    ("script-writer", "youtube", "scripts", "deepseek-v4-flash-free", 2),
    ("hook-writer", "youtube", "hooks", "deepseek-v4-flash-free", 2),
    ("thumbnail-designer", "youtube", "thumbnails", "deepseek-v4-flash-free", 2),
    ("title-strategist", "youtube", "titles", "deepseek-v4-flash-free", 2),
    ("community-manager", "youtube", "engagement", "deepseek-v4-flash-free", 2),
    ("postmortem-analyst", "youtube", "review", "deepseek-v4-flash-free", 2),
]

# Default collaboration edges (who talks to whom) — mirrors the graph layout
DEFAULT_EDGES = [
    ("executive-ai", "planner-ai"), ("planner-ai", "task-manager"), ("task-manager", "workflow-engine"),
    ("workflow-engine", "model-orchestrator"), ("model-orchestrator", "memory-engine"),
    ("memory-engine", "knowledge-engine"), ("knowledge-engine", "quality-checker"),
    ("quality-checker", "executive-ai"),
    ("recruiter", "onboarding"), ("backend", "tester"), ("frontend", "tester"),
    ("invoicing", "expense"), ("fulfillment", "support"),
    ("email-agent", "calendar-agent"), ("email-agent", "reminder-agent"),
    ("script-writer", "hook-writer"), ("hook-writer", "thumbnail-designer"),
    ("title-strategist", "community-manager"), ("postmortem-analyst", "script-writer"),
]

def seed():
    init_db()
    c = _conn()
    for name, dept, role, model, auto in ROSTER:
        c.execute("INSERT OR IGNORE INTO agents (name,dept,role,model,autonomy) VALUES (?,?,?,?,?)",
                  (name, dept, role, model, auto))
    for s, r in DEFAULT_EDGES:
        c.execute("INSERT OR IGNORE INTO edges (sender, recipient, msgs, last_at) VALUES (?,?,0,?)",
                  (s, r, _now()))
    c.commit(); c.close()
    return len(ROSTER)

def send_message(sender, recipient, subject, body):
    init_db()
    c = _conn()
    a = c.execute("SELECT 1 FROM agents WHERE name=?", (sender,)).fetchone()
    b = c.execute("SELECT 1 FROM agents WHERE name=?", (recipient,)).fetchone()
    if not a or not b:
        c.close()
        return {"ok": False, "error": "unknown agent(s) — use registered names"}
    c.execute("INSERT INTO messages (sender, recipient, subject, body, created_at) VALUES (?,?,?,?,?)",
              (sender, recipient, subject, body, _now()))
    c.execute("""INSERT INTO edges (sender, recipient, msgs, last_at) VALUES (?,?,1,?)
                 ON CONFLICT(sender, recipient) DO UPDATE SET msgs = msgs + 1, last_at = excluded.last_at""",
              (sender, recipient, _now()))
    c.commit()
    mid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return {"ok": True, "message_id": mid, "sender": sender, "recipient": recipient}

def inbox(agent, unread_only=False):
    init_db()
    c = _conn()
    q = "SELECT * FROM messages WHERE recipient=? ORDER BY id DESC LIMIT 30"
    rows = c.execute(q, (agent,)).fetchall()
    if unread_only:
        rows = [r for r in rows if not r["read"]]
    c.close()
    return {"ok": True, "agent": agent, "messages": [dict(r) for r in rows]}

def mark_read(msg_id):
    init_db()
    c = _conn()
    c.execute("UPDATE messages SET read=1 WHERE id=?", (msg_id,))
    c.commit(); c.close()
    return {"ok": True, "message_id": msg_id, "read": True}

def validate(validator, target, verdict, note=""):
    """Quality Checker (or any agent) validates another agent's work."""
    init_db()
    c = _conn()
    if verdict not in ("approved", "needs-work"):
        c.close(); return {"ok": False, "error": "verdict must be approved|needs-work"}
    c.execute("""INSERT INTO messages (sender, recipient, subject, body, created_at, validated)
                 VALUES (?,?,?,?,?, 1)""",
              (validator, target, f"validation: {verdict}", f"{note}\nVerdict: {verdict}".strip(), _now()))
    c.execute("""INSERT INTO edges (sender, recipient, msgs, last_at) VALUES (?,?,1,?)
                 ON CONFLICT(sender, recipient) DO UPDATE SET msgs = msgs + 1, last_at = excluded.last_at""",
              (validator, target, _now()))
    c.commit(); c.close()
    return {"ok": True, "validator": validator, "target": target, "verdict": verdict}

def collab_graph():
    init_db()
    c = _conn()
    agents = c.execute("SELECT * FROM agents ORDER BY dept, name").fetchall()
    edges = c.execute("SELECT * FROM edges WHERE msgs > 0 ORDER BY msgs DESC").fetchall()
    c.close()
    nodes = [{"id": a["name"], "label": a["name"].replace("-", " ").title(), "dept": a["dept"],
              "role": a["role"], "model": a["model"], "autonomy": a["autonomy"]} for a in agents]
    links = [{"source": e["sender"], "target": e["recipient"], "value": e["msgs"],
              "last_at": e["last_at"]} for e in edges]
    return {"ok": True, "nodes": nodes, "links": links, "agent_count": len(nodes),
            "active_edges": len(links)}

def main():
    ap = argparse.ArgumentParser(description="Richard OS Neural Collaboration (#17)")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--graph", action="store_true")
    ap.add_argument("--send", nargs=3, metavar=("SENDER", "RECIPIENT", "SUBJECT"))
    ap.add_argument("--inbox", metavar="AGENT")
    ap.add_argument("--validate", nargs=3, metavar=("VALIDATOR", "TARGET", "VERDICT"))
    args = ap.parse_args()
    if args.seed:
        print(f"seeded {seed()} agents"); return
    if args.graph:
        g = collab_graph()
        print(f"agents: {g['agent_count']}, active edges: {g['active_edges']}")
        for l in g["links"]:
            print(f"  {l['source']} -> {l['target']} ({l['value']})")
        return
    if args.send:
        s, r, subj = args.send
        print(json.dumps(send_message(s, r, subj, "auto message"), indent=2)); return
    if args.inbox:
        d = inbox(args.inbox)
        print(f"inbox for {args.inbox}: {len(d['messages'])} messages")
        for m in d["messages"]:
            print(f"  [{m['id']}] {m['sender']} -> {m['subject']} (read={m['read']})")
        return
    if args.validate:
        v, t, verdict = args.validate
        print(json.dumps(validate(v, t, verdict, "quality check"), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()

