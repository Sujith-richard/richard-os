#!/usr/bin/env python3
"""
scripts/execution_engine.py - v4.0 #2 Execution Engine
Workflow says WHAT. Execution does it: queue, retry, parallel, dependencies,
progress, completion. Wraps workflow_engine._exec_step.
Persists jobs to 06-data/execution.db: jobs, job_steps.
"""
import json, sqlite3, pathlib, datetime, time, threading, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "execution.db"

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
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, workflow TEXT, steps TEXT,
        status TEXT DEFAULT 'queued', progress REAL DEFAULT 0,
        attempts INTEGER DEFAULT 0, max_retries INTEGER DEFAULT 2,
        error TEXT, started_at TEXT, ended_at TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS job_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, idx INTEGER, kind TEXT,
        title TEXT, deps TEXT DEFAULT '[]', parallel INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending', result TEXT, attempts INTEGER DEFAULT 0, started_at TEXT, ended_at TEXT);
    """)
    c.commit(); c.close()

def _exec_step(kind, step, job_name):
    """Wrap workflow_engine._exec_step (simulated execution)."""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from workflow_engine import _exec_step as we_exec
        return we_exec(kind, step, job_name)
    except Exception as e:
        return (False, f"exec error: {e}")

def enqueue(name, steps, max_retries=2):
    """Queue a job. Steps: [{k, t, deps:[idx], parallel:0|1}]."""
    init_db()
    c = _conn()
    cur = c.execute("INSERT INTO jobs (name, workflow, steps, status, max_retries, created_at) VALUES (?,?,?, 'queued', ?, ?)",
                    (name, name, json.dumps(steps), max_retries, _now()))
    job_id = cur.lastrowid
    for i, s in enumerate(steps):
        c.execute("INSERT INTO job_steps (job_id, idx, kind, title, deps, parallel, status) VALUES (?,?,?,?,?,?, 'pending')",
                  (job_id, i, s.get("k", "agent"), s.get("t", f"step {i}"),
                   json.dumps(s.get("deps", [])), 1 if s.get("parallel") else 0))
    c.commit()
    c.execute("UPDATE jobs SET status='running', started_at=? WHERE id=?", (_now(), job_id))
    c.commit(); c.close()
    return {"ok": True, "job_id": job_id, "name": name, "steps": len(steps), "status": "running"}

def _ready_steps(c, job_id):
    """Steps whose deps are all done, not yet run."""
    steps = c.execute("SELECT * FROM job_steps WHERE job_id=? AND status='pending' ORDER BY idx", (job_id,)).fetchall()
    ready = []
    for s in steps:
        deps = json.loads(s["deps"] or "[]")
        if all(c.execute("SELECT status FROM job_steps WHERE job_id=? AND idx=?", (job_id, d)).fetchone()["status"] == "done"
               for d in deps):
            ready.append(s)
    return ready

def _run_ready(c, job_id, job):
    """Run all currently-ready steps — parallel ones together, others in order."""
    ready = _ready_steps(c, job_id)
    done = 0
    parallel_group = [s for s in ready if s["parallel"]]
    serial = [s for s in ready if not s["parallel"]]
    group = parallel_group if parallel_group else serial[:1]
    for s in group:
        c.execute("UPDATE job_steps SET status='running', started_at=? WHERE id=?", (_now(), s["id"]))
        c.commit()
        ok, detail = _exec_step(s["kind"], {"k": s["kind"], "t": s["title"]}, job["name"])
        c.execute("UPDATE job_steps SET status=? , result=?, attempts=attempts+1, ended_at=? WHERE id=?",
                  ("done" if ok else "error", detail[:300], _now(), s["id"]))
        c.commit()
        done += ok
    return done

def execute_async(job_id):
    """Run a queued job to completion in a background thread (queue + retry + parallel)."""
    def work():
        init_db()
        c = _conn()
        job = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        total = c.execute("SELECT COUNT(*) n FROM job_steps WHERE job_id=?", (job_id,)).fetchone()["n"]
        while True:
            ready = _ready_steps(c, job_id)
            if not ready:
                break
            _run_ready(c, job_id, job)
            # progress
            ndone = c.execute("SELECT COUNT(*) n FROM job_steps WHERE job_id=? AND status='done'", (job_id,)).fetchone()["n"]
            nerr = c.execute("SELECT COUNT(*) n FROM job_steps WHERE job_id=? AND status='error'", (job_id,)).fetchone()["n"]
            c.execute("UPDATE jobs SET progress=? WHERE id=?", (round(ndone / total * 100, 1) if total else 0, job_id))
            c.commit()
            # retry errored steps
            if nerr:
                errored = c.execute("SELECT * FROM job_steps WHERE job_id=? AND status='error'", (job_id,)).fetchall()
                for e in errored:
                    if e["attempts"] < job["max_retries"]:
                        c.execute("UPDATE job_steps SET status='pending' WHERE id=?", (e["id"],))
                        c.commit()
                    else:
                        c.execute("UPDATE jobs SET status='error', error=?, ended_at=? WHERE id=?",
                                  (f"step {e['idx']} failed after {e['attempts']} attempts", _now(), job_id))
                        c.commit()
                        return
            if ndone == total:
                c.execute("UPDATE jobs SET status='done', progress=100, ended_at=? WHERE id=?", (_now(), job_id))
                c.commit()
                return
        c.close()
    t = threading.Thread(target=work, daemon=True)
    t.start()
    return {"ok": True, "job_id": job_id, "status": "running (background)"}

def job_status(job_id):
    init_db()
    c = _conn()
    j = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not j:
        c.close(); return {"ok": False, "error": "job not found"}
    steps = c.execute("SELECT * FROM job_steps WHERE job_id=? ORDER BY idx", (job_id,)).fetchall()
    c.close()
    return {"ok": True, "job": dict(j), "steps": [dict(s) for s in steps]}

def queue():
    init_db()
    c = _conn()
    rows = c.execute("SELECT id, name, status, progress, attempts, error, created_at, ended_at FROM jobs ORDER BY id DESC LIMIT 20").fetchall()
    c.close()
    return {"ok": True, "jobs": [dict(r) for r in rows]}

def retry(job_id):
    init_db()
    c = _conn()
    j = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not j:
        c.close(); return {"ok": False, "error": "job not found"}
    c.execute("UPDATE job_steps SET status='pending', attempts=0 WHERE job_id=?", (job_id,))
    c.execute("UPDATE jobs SET status='running', error=NULL, attempts=attempts+1, progress=0, started_at=? WHERE id=?", (_now(), job_id))
    c.commit(); c.close()
    return execute_async(job_id)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", nargs=2, metavar=("NAME", "JSON_STEPS"))
    ap.add_argument("--status", metavar="JOB_ID")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--retry", metavar="JOB_ID")
    args = ap.parse_args()
    if args.run:
        steps = json.loads(args.run[1])
        r = enqueue(args.run[0], steps)
        if r.get("ok"): execute_async(r["job_id"])
        print(json.dumps(r, indent=2)); return
    if args.status:
        print(json.dumps(job_status(int(args.status)), indent=2, default=str)); return
    if args.queue:
        for j in queue()["jobs"]:
            print(f"  [{j['id']}] {j['name']:30s} {j['status']:9s} {j['progress']:5.1f}% attempts={j['attempts']}")
        return
    if args.retry:
        print(json.dumps(retry(int(args.retry)), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
