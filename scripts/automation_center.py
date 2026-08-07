#!/usr/bin/env python3
"""
scripts/automation_center.py - Phase H5 Automation Center
Registry of scheduled jobs: scheduler agents + execution jobs.
Enable/disable, run-now, create scheduled jobs. Persists to 06-data/automations.json.
"""
import json, pathlib, datetime, argparse, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUTOMATIONS = ROOT / "06-data" / "automations.json"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _load():
    if AUTOMATIONS.exists():
        try:
            return json.loads(AUTOMATIONS.read_text())
        except Exception:
            pass
    return {"jobs": []}

def _save(d):
    AUTOMATIONS.parent.mkdir(parents=True, exist_ok=True)
    AUTOMATIONS.write_text(json.dumps(d, indent=2))

def list_jobs():
    """Scheduler agents + execution jobs + user automations."""
    jobs = []
    # scheduler agents (from scheduler.py SCHEDULE)
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import scheduler as sched
        for agent, times in sched.SCHEDULE.items():
            jobs.append({"id": f"sched-{agent}", "name": agent, "kind": "scheduler",
                         "schedule": ", ".join(times), "enabled": True, "source": "scheduler"})
    except Exception:
        pass
    # execution jobs (recent)
    try:
        import sqlite3
        c = sqlite3.connect(ROOT / "06-data" / "execution.db"); c.row_factory = sqlite3.Row
        for r in c.execute("SELECT DISTINCT name FROM jobs ORDER BY id DESC LIMIT 10"):
            jobs.append({"id": f"exec-{r['name']}", "name": r["name"], "kind": "execution",
                         "schedule": "manual", "enabled": True, "source": "execution"})
        c.close()
    except Exception:
        pass
    # user automations (persisted)
    user = _load()["jobs"]
    jobs += user
    # dedupe by id
    seen = {}
    for j in jobs:
        seen[j["id"]] = j
    return {"ok": True, "jobs": list(seen.values())}

def create(name, schedule, kind="workflow", run_cmd=""):
    d = _load()
    jid = f"auto-{len(d['jobs']) + 1}"
    job = {"id": jid, "name": name, "kind": kind, "schedule": schedule,
           "enabled": True, "run_cmd": run_cmd, "created_at": _now(), "source": "automation"}
    d["jobs"].append(job)
    _save(d)
    return {"ok": True, "job": job}

def toggle(job_id):
    d = _load()
    for j in d["jobs"]:
        if j["id"] == job_id:
            j["enabled"] = not j.get("enabled", True)
            _save(d)
            return {"ok": True, "id": job_id, "enabled": j["enabled"]}
    return {"ok": False, "error": "not a user automation (scheduler/exec jobs are read-only)"}

def run_now(job_id, request=""):
    """Run a job now. For scheduler agents, call the agent script; for execution, note it."""
    name = job_id
    if job_id.startswith("sched-"):
        agent = job_id.replace("sched-", "")
        try:
            subprocess.Popen([sys.executable, str(ROOT / "scripts" / "agents_runner.py"), agent],
                             cwd=str(ROOT / "scripts"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"ok": True, "id": job_id, "action": "launched", "detail": f"agent {agent} running"}
        except Exception as e:
            return {"ok": False, "error": str(e)[:120]}
    return {"ok": True, "id": job_id, "action": "queued",
            "detail": f"run {name} (simulated via execution engine)"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--create", nargs=2, metavar=("NAME", "SCHEDULE"))
    ap.add_argument("--toggle", metavar="ID")
    ap.add_argument("--run", metavar="ID")
    args = ap.parse_args()
    if args.list:
        for j in list_jobs()["jobs"]:
            print(f"  {j['id']:28s} {j['name']:22s} {j['kind']:12s} {j['schedule']:14s} enabled={j['enabled']}")
        return
    if args.create:
        print(json.dumps(create(*args.create), indent=2)); return
    if args.toggle:
        print(json.dumps(toggle(args.toggle), indent=2)); return
    if args.run:
        print(json.dumps(run_now(args.run), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
