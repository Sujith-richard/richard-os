#!/usr/bin/env python3
"""Richard OS — Approval queue: autonomy-2 drafts wait for your one-click approve.
Items are stored in 06-data/approvals.db. Approve → execute action."""
import sqlite3, sys, json
from pathlib import Path
from datetime import datetime

DATA = Path(__file__).resolve().parent.parent / "06-data"

def _conn():
    conn = sqlite3.connect(DATA / "approvals.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT, action TEXT, payload TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return conn

def add(agent, action, payload):
    """Queue a draft for approval."""
    conn = _conn()
    conn.execute("INSERT INTO approvals (agent, action, payload) VALUES (?,?,?)",
                 (agent, action, json.dumps(payload)))
    conn.commit(); conn.close()
    print(f"⏳ Queued for approval: {agent} → {action} (id auto)")

def list_pending():
    conn = _conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM approvals WHERE status='pending' ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve(approval_id):
    """Approve a queued draft → mark done + print payload (execution hook)."""
    conn = _conn()
    row = conn.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
    if not row:
        print(f"❌ No approval with id {approval_id}")
        return
    payload = json.loads(row[3])
    conn.execute("UPDATE approvals SET status='approved' WHERE id=?", (approval_id,))
    conn.commit(); conn.close()
    try:
        import sys as _s
        _s.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
        from governance_bridge import audit
        audit(row[1], row[2], row[3], True)
    except Exception:
        pass
    print(f"✅ Approved {row[1]} → {row[2]}")
    print(f"   Execute: {payload.get('execute', 'no action defined')}")
    # TODO: wire execute hook (send email, create invoice, etc.)

def reject(approval_id):
    conn = _conn()
    conn.execute("UPDATE approvals SET status='rejected' WHERE id=?", (approval_id,))
    conn.commit(); conn.close()
    try:
        import sys as _s
        _s.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
        from governance_bridge import audit
        audit(row[1], row[2], row[3], False)
    except Exception:
        pass
    print(f"❌ Rejected approval {approval_id}")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for a in list_pending():
            print(f"#{a['id']} [{a['agent']}] {a['action']} — {a['payload'][:80]}")
        if not list_pending():
            print("(empty — nothing waiting for approval)")
    elif cmd == "add":
        add(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
    elif cmd == "approve":
        approve(int(sys.argv[2]))
    elif cmd == "reject":
        reject(int(sys.argv[2]))
    else:
        print("Usage: python scripts/approval_queue.py [list|add <agent> <action> <json>|approve <id>|reject <id>]")

if __name__ == "__main__":
    main()
