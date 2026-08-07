#!/usr/bin/env python3
"""
scripts/workflow_engine.py - #10 Workflow Engine
Executes workflows (from planner.py or seeded) as a state machine.
Step kinds: trigger -> agent -> data -> approve -> action.
Persists to 06-data/workflows.db: workflows, runs, steps.
Fake-first: step executors simulate work + log, approval steps block on
autonomy and go to the approval queue.
"""
import json, sqlite3, pathlib, datetime, argparse, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "workflows.db"

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
    CREATE TABLE IF NOT EXISTS workflows (
        name TEXT PRIMARY KEY, title TEXT, goal TEXT, steps TEXT, status TEXT DEFAULT 'idle',
        runs INTEGER DEFAULT 0, errors INTEGER DEFAULT 0, last_run TEXT, created_at TEXT, updated_at TEXT);
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, workflow TEXT, started_at TEXT, ended_at TEXT,
        status TEXT DEFAULT 'running', steps_total INTEGER, steps_done INTEGER, log TEXT);
    """)
    c.commit(); c.close()

# ---- the 4 starter workflows (mirrors the existing static UI WFS) ----
STARTERS = [
    {"name": "new-job-lead", "title": "New Job Lead → Pipeline",
     "goal": "Process new job lead into the pipeline.",
     "steps": [{"k":"trigger","t":"New lead","info":"second_brain"},
               {"k":"agent","t":"Job Hunter","info":"screens & scores"},
               {"k":"data","t":"CRM update","info":"crm.db"},
               {"k":"agent","t":"Draft outreach","info":"job_hunter"},
               {"k":"approve","t":"Founder approval","info":"approval queue"},
               {"k":"action","t":"Send","info":"outreach"}]},
    {"name": "email-triage", "title": "Email → Triage → Reply",
     "goal": "Classify inbox, draft reply, get approval, send.",
     "steps": [{"k":"trigger","t":"Email arrives","info":"imap/comms"},
               {"k":"agent","t":"Email Agent","info":"triage"},
               {"k":"data","t":"Classify","info":"action-needed"},
               {"k":"agent","t":"Draft reply","info":"in your voice"},
               {"k":"approve","t":"Founder approval","info":"approval queue"},
               {"k":"action","t":"Send reply","info":"done"}]},
    {"name": "daily-brief", "title": "Daily Brief",
     "goal": "The 7am summary the OS works on while you sleep.",
     "steps": [{"k":"trigger","t":"7:00 AM","info":"scheduler"},
               {"k":"agent","t":"Agents run","info":"jobs/tasks/finance"},
               {"k":"data","t":"Collect","info":"all systems"},
               {"k":"action","t":"Morning Brief","info":"one screen"}]},
    {"name": "content-pipeline", "title": "Content Pipeline",
     "goal": "From idea to published post.",
     "steps": [{"k":"trigger","t":"Content idea","info":"creator.db"},
               {"k":"agent","t":"Content Ops","info":"drafts"},
               {"k":"data","t":"Schedule","info":"calendar"},
               {"k":"approve","t":"Founder approval","info":"approval queue"},
               {"k":"action","t":"Publish","info":"social"}]},
]

def seed():
    init_db()
    c = _conn()
    for w in STARTERS:
        c.execute("""INSERT OR IGNORE INTO workflows (name,title,goal,steps,status,created_at,updated_at)
                     VALUES (?,?,?,?, 'idle', ?, ?)""",
                  (w["name"], w["title"], w["goal"], json.dumps(w["steps"]), _now(), _now()))
    c.commit(); c.close()
    return len(STARTERS)
def _exec_step(kind, step, workflow):
    """Simulate executing one step. Returns (ok, detail). Approval steps go to queue."""
    t, info = step.get("t", "step"), step.get("info", "")
    if kind == "trigger":
        return True, f"trigger: {t} ({info}) — detected"
    if kind == "agent":
        time.sleep(0.15)
        return True, f"agent: {t} ({info}) — ran (simulated)"
    if kind == "data":
        return True, f"data: {t} ({info}) — read/write (simulated)"
    if kind == "approve":
        # autonomy: approval steps queue for human; record as pending (non-blocking in sim)
        return True, f"approval: {t} — queued for founder approval"
    if kind == "action":
        time.sleep(0.1)
        return True, f"action: {t} ({info}) — executed (simulated)"
    return False, f"unknown step kind: {kind}"

def run_workflow(name):
    init_db()
    c = _conn()
    w = c.execute("SELECT * FROM workflows WHERE name=?", (name,)).fetchone()
    if not w:
        c.close()
        return {"ok": False, "error": "workflow not found"}
    steps = json.loads(w["steps"])
    c.execute("UPDATE workflows SET status='running', updated_at=? WHERE name=?", (_now(), name))
    run_id = c.execute("""INSERT INTO runs (workflow, started_at, status, steps_total, steps_done, log)
                          VALUES (?,?, 'running', ?, 0, ?)""",
                       (name, _now(), len(steps), "[]")).lastrowid
    c.commit()
    log_entries = []
    ok_all = True
    for i, step in enumerate(steps, 1):
        ok, detail = _exec_step(step.get("k"), step, w["name"])
        entry = {"step": i, "kind": step.get("k"), "title": step.get("t"), "ok": ok, "detail": detail}
        log_entries.append(entry)
        if not ok:
            ok_all = False
            break
    status = "done" if ok_all else "error"
    ended = _now()
    c.execute("""UPDATE runs SET status=?, ended_at=?, steps_done=?, log=? WHERE id=?""",
              (status, ended, len(log_entries), json.dumps(log_entries, indent=2), run_id))
    c.execute("""UPDATE workflows SET status=?, runs=runs+1, errors=errors+?, last_run=?, updated_at=? WHERE name=?""",
              (status, 0 if ok_all else 1, ended, _now(), name))
    try:
        import sys as _eb2
        _eb2.path.insert(0, str(ROOT / "scripts"))
        from system_services import publish
        publish("workflow.finished", f"{name} -> {status}")
    except Exception:
        pass
    c.commit()
    w2 = c.execute("SELECT * FROM workflows WHERE name=?", (name,)).fetchone()
    c.close()
    return {"ok": True, "workflow": name, "run_id": run_id, "status": status,
            "steps": len(log_entries), "log": log_entries, "workflow_row": dict(w2)}

def list_workflows():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM workflows ORDER BY created_at").fetchall()
    c.close()
    return {"ok": True, "workflows": [dict(r) for r in rows]}

def workflow_detail(name):
    init_db()
    c = _conn()
    w = c.execute("SELECT * FROM workflows WHERE name=?", (name,)).fetchone()
    runs = c.execute("SELECT * FROM runs WHERE workflow=? ORDER BY id DESC LIMIT 10", (name,)).fetchall()
    c.close()
    if not w:
        return {"ok": False, "error": "not found"}
    return {"ok": True, "workflow": dict(w), "runs": [dict(r) for r in runs]}

def main():
    ap = argparse.ArgumentParser(description="Richard OS Workflow Engine (#10)")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", metavar="NAME")
    ap.add_argument("--detail", metavar="NAME")
    args = ap.parse_args()
    if args.seed:
        print(f"seeded {seed()} workflows"); return
    if args.list:
        for w in list_workflows()["workflows"]:
            print(f"{w['status']:8s} {w['name']:20s} runs={w['runs']} errors={w['errors']}")
        return
    if args.run:
        r = run_workflow(args.run)
        if not r.get("ok"): print(r); return
        print(f"run {r['run_id']}: {r['status']} — {r['steps']} steps")
        for e in r["log"]:
            print(f"  [{e['kind']:7s}] {e['title']}: {e['detail']}")
        return
    if args.detail:
        import pprint; pprint.pprint(workflow_detail(args.detail)); return
    ap.print_help()

if __name__ == "__main__":
    main()

