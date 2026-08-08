#!/usr/bin/env python3
"""scripts/kernel.py - Phase A8 Richard Kernel boot sequence
Initializes subsystems in order: storage -> memory -> knowledge -> skills ->
tools -> departments -> models -> services -> brain -> conversation.
Each step reports ok/fail; a failed (non-critical) step is retried once.
Logs the boot to 06-data/kernel_boot.json."""
import json, pathlib, datetime, sys, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOT_LOG = ROOT / "06-data" / "kernel_boot.json"

BOOT_ORDER = [
    ("storage",    lambda: _db_count()),
    ("memory",     lambda: _import("memory_system")),
    ("knowledge",  lambda: _import("knowledge_graph")),
    ("skills",     lambda: _import("skill_layer")),
    ("tools",      lambda: _import("mcp_tools")),
    ("departments", lambda: _import("department_engine")),
    ("models",     lambda: _import("model_orchestrator")),
    ("services",   lambda: _import("system_services")),
    ("brain",      lambda: _import("escalation_engine")),
    ("conversation", lambda: _import("doc_chat")),
]

def _import(module):
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "tools"))
    __import__(module)
    return True

def _db_count():
    n = len(list((ROOT / "06-data").glob("*.db")))
    return n > 0

def boot():
    results = []
    for name, check in BOOT_ORDER:
        ok = False
        try:
            ok = bool(check())
        except Exception:
            ok = False
        if not ok:
            time.sleep(0.2)
            try:
                ok = bool(check())
            except Exception:
                ok = False
        results.append({"subsystem": name, "status": "ok" if ok else "fail"})
    overall = "ok" if all(r["status"] == "ok" for r in results) else "degraded"
    entry = {"booted_at": datetime.datetime.now().isoformat(timespec="seconds"),
             "overall": overall, "steps": results}
    BOOT_LOG.parent.mkdir(parents=True, exist_ok=True)
    BOOT_LOG.write_text(json.dumps(entry, indent=2))
    return entry

def main():
    r = boot()
    print(f"kernel boot: {r['overall']}")
    for s in r["steps"]:
        print(f"  {s['subsystem']:14s} {s['status']}")

if __name__ == "__main__":
    main()


# ===== v5.7 Kernel completeness: config/process/storage managers =====
def config_manager():
    """Configuration manager: reads settings + model routes + integrations config."""
    out = {}
    for name, path in [("settings", "settings.json"), ("model_routes", "model_routes.json"),
                       ("integrations", "integrations.json")]:
        try:
            p = ROOT / "06-data" / path
            out[name] = json.loads(p.read_text()) if p.exists() else {}
        except Exception:
            out[name] = {}
    return {"ok": True, "configs": list(out.keys()), "detail": {k: len(v) for k, v in out.items()}}

def process_manager():
    """Process manager: list running OS processes (server, autonomy, scheduler)."""
    import subprocess as sp
    procs = []
    try:
        r = sp.run(["ps", "aux"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if any(k in line for k in ["uvicorn scripts.server", "autonomy.py", "scheduler.py"]):
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    procs.append({"pid": parts[1], "cpu": parts[2], "mem": parts[3], "cmd": parts[10][:60]})
    except Exception:
        pass
    return {"ok": True, "processes": procs}

def storage_manager():
    """Storage manager: DB inventory + sizes + datasets."""
    dbs = list((ROOT / "06-data").glob("*.db"))
    sizes = []
    for d in dbs:
        try:
            sizes.append({"name": d.name, "kb": round(d.stat().st_size / 1024, 1)})
        except Exception:
            pass
    datasets = sum(1 for f in (ROOT / "06-data" / "datasets").glob("*.jsonl"))
    return {"ok": True, "databases": len(dbs), "total_kb": round(sum(s["kb"] for s in sizes), 1),
            "datasets": datasets, "sizes": sorted(sizes, key=lambda x: -x["kb"])[:8]}
