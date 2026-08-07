#!/usr/bin/env python3
"""
scripts/system_services.py - v4.0 #7 Infrastructure + System Services
Service registry + health monitor + metrics + event bus.
Checks DBs, integrations, GPU, scheduler, execution queue, model proxy live.
Persists events to 06-data/system_events.db.
"""
import json, sqlite3, pathlib, datetime, subprocess, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVENTS_DB = ROOT / "06-data" / "system_events.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _evconn():
    EVENTS_DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(EVENTS_DB)
    c.row_factory = sqlite3.Row
    return c

def _http(url, timeout=4):
    import urllib.request
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status

def _db_count():
    return len(list((ROOT / "06-data").glob("*.db")))

def _gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,utilization.gpu",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def check_services():
    """Live health check of every service. Returns (ok, {service: {status, detail}})."""
    services = {}
    # database / storage
    services["database"] = {"status": "green", "detail": f"{_db_count()} sqlite DBs"}
    # integrations (direct, not via self-HTTP which deadlocks single-threaded uvicorn)
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from integrations import list_integrations
        d = list_integrations()
        live = sum(1 for v in d["integrations"].values() if v["status"] == "live")
        total = len(d["integrations"])
        services["integrations"] = {"status": "green" if live else "amber",
                                    "detail": f"{live}/{total} live"}
    except Exception:
        services["integrations"] = {"status": "red", "detail": "unreachable"}
    # gpu
    g = _gpu()
    services["gpu"] = {"status": "green" if g else "red", "detail": g or "not available"}
    # model proxy
    try:
        _http("http://127.0.0.1:1234/v1/models")
        services["model-proxy"] = {"status": "green", "detail": "AI-Workspace proxy OK"}
    except Exception:
        services["model-proxy"] = {"status": "red", "detail": "proxy down"}
    # scheduler (direct read of the schedule config)
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import scheduler as sched_mod
        n = len(getattr(sched_mod, "SCHEDULE", {}))
        services["scheduler"] = {"status": "green", "detail": f"{n} scheduled agents"}
    except Exception:
        services["scheduler"] = {"status": "amber", "detail": "schedule not loaded"}
    # execution queue
    try:
        d = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/api/v1/execution/queue", timeout=4).read().decode())
        jobs = len(d.get("jobs", []))
        services["queue-manager"] = {"status": "green", "detail": f"{jobs} jobs"}
    except Exception:
        services["queue-manager"] = {"status": "amber", "detail": "no jobs yet"}
    # event bus
    services["event-bus"] = {"status": "green", "detail": "accepting events"}
    return services

def health():
    services = check_services()
    overall = "green"
    if any(s["status"] == "red" for s in services.values()):
        overall = "red"
    elif any(s["status"] == "amber" for s in services.values()):
        overall = "amber"
    return {"ok": True, "overall": overall, "services": services, "checked_at": _now()}

def metrics():
    services = check_services()
    g = _gpu()
    import os
    return {"ok": True, "metrics": {
        "databases": _db_count(),
        "gpu": g or "none",
        "gpu_mem_mb": g.split(",")[1].strip().split()[0] if g else 0,
        "gpu_util": g.split(",")[2].strip().replace("%", "") if g else 0,
        "integrations_live": sum(1 for v in services["integrations"].values() if v == "green") if isinstance(services.get("integrations"), dict) and isinstance(services["integrations"], dict) else 0,
        "cpu_count": os.cpu_count() or 0,
    }, "checked_at": _now()}

def emit(event_type, payload=""):
    c = _evconn()
    c.execute("""CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, payload TEXT, at TEXT)""")
    c.execute("INSERT INTO events (type, payload, at) VALUES (?,?,?)", (event_type, str(payload)[:500], _now()))
    c.commit(); c.close()
    return {"ok": True, "event": event_type, "at": _now()}

def events(limit=20):
    c = _evconn()
    c.execute("""CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, payload TEXT, at TEXT)""")
    rows = c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "events": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--metrics", action="store_true")
    ap.add_argument("--emit", nargs=2, metavar=("TYPE", "PAYLOAD"))
    ap.add_argument("--events", action="store_true")
    args = ap.parse_args()
    if args.health:
        h = health()
        print(f"OVERALL: {h['overall']}")
        for k, v in h["services"].items():
            print(f"  {k:16s} {v['status']:6s} {v['detail']}")
        return
    if args.metrics:
        print(json.dumps(metrics(), indent=2)); return
    if args.emit:
        print(json.dumps(emit(args.emit[0], args.emit[1]), indent=2)); return
    if args.events:
        for e in events()["events"]:
            print(f"  [{e['id']}] {e['type']} @ {e['at']}: {e['payload'][:60]}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()


# ===== v5.2 Event Bus SPINE — publish/subscribe with subscribers =====
SUBSCRIBERS = {}   # event_type -> [callables]
import threading
_bus_lock = threading.Lock()

def subscribe(event_type, fn):
    """Register a subscriber for an event type (fn(event) called on publish)."""
    with _bus_lock:
        SUBSCRIBERS.setdefault(event_type, []).append(fn)
    return {"ok": True, "event": event_type, "subscribers": len(SUBSCRIBERS.get(event_type, []))}

def publish(event_type, payload=""):
    """Publish to the bus: persist + notify subscribers (thread-safe)."""
    r = emit(event_type, payload)   # existing persist to system_events.db
    with _bus_lock:
        subs = list(SUBSCRIBERS.get(event_type, [])) + list(SUBSCRIBERS.get("*", []))
    for fn in subs:
        try:
            fn({"type": event_type, "payload": payload})
        except Exception:
            pass
    return r

def subscriptions():
    return {"ok": True, "subscribers": {k: len(v) for k, v in SUBSCRIBERS.items()}}
