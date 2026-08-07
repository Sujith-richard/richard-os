#!/usr/bin/env python3
"""scripts/agent_runtime.py - v5.5 Agent Runtime service
Unifies: agent registry (roster) + scheduler + communication (collab bus) +
lifecycle into one runtime. Run agents on demand or scheduled."""
import json, sqlite3, pathlib, datetime, subprocess, sys, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "06-data" / "agent_runtime.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, task TEXT, status TEXT,
        started_at TEXT, ended_at TEXT, result TEXT)""")
    c.commit(); c.close()

def registry():
    """Agent registry from collab roster."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from collab_engine import collab_graph
        g = collab_graph()
        return {"ok": True, "agents": g["nodes"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def run_agent(agent, task):
    """Execute an agent task (via agents_runner or collab), log to runtime."""
    init_db()
    c = _conn()
    c.execute("INSERT INTO runs (agent, task, status, started_at) VALUES (?,?, 'running', ?)",
              (agent, task, _now()))
    rid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.commit()
    result = "simulated"
    try:
        # try launching the real agent runner
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "agents_runner.py"), agent],
                           capture_output=True, text=True, timeout=60, cwd=str(ROOT / "scripts"))
        result = (r.stdout or r.stderr)[-150:]
    except Exception as e:
        result = f"error: {str(e)[:120]}"
    c.execute("UPDATE runs SET status='done', ended_at=?, result=? WHERE id=?", (_now(), result, rid))
    c.commit()
    # publish event
    try:
        from system_services import publish
        publish("agent.started", f"{agent} running: {task}")
    except Exception: pass
    c.close()
    return {"ok": True, "run_id": rid, "agent": agent, "status": "done", "result": result[:100]}

def schedule(agent, task, time_str):
    """Register a scheduled agent run (persisted, read by scheduler)."""
    import json as j
    p = ROOT / "06-data" / "agent_runtime_schedule.json"
    sched = j.loads(p.read_text()) if p.exists() else []
    sched.append({"agent": agent, "task": task, "time": time_str, "created": _now()})
    p.write_text(j.dumps(sched, indent=2))
    return {"ok": True, "scheduled": f"{agent} @ {time_str}"}

def recent_runs(limit=10):
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "runs": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", action="store_true")
    ap.add_argument("--run", nargs=2, metavar=("AGENT", "TASK"))
    ap.add_argument("--schedule", nargs=3, metavar=("AGENT", "TASK", "TIME"))
    ap.add_argument("--runs", action="store_true")
    args = ap.parse_args()
    if args.registry:
        d = registry()
        print(f"agents: {len(d.get('agents', []))}")
        for a in d.get("agents", [])[:8]: print(f"  {a['id']}")
        return
    if args.run:
        print(json.dumps(run_agent(*args.run), indent=2)); return
    if args.schedule:
        print(json.dumps(schedule(*args.schedule), indent=2)); return
    if args.runs:
        for r in recent_runs()["runs"]:
            print(f"  [{r['id']}] {r['agent']:18s} {r['status']:8s} {r['result'][:40]}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
