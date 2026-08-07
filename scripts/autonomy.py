#!/usr/bin/env python3
"""scripts/autonomy.py - Phase J2 Autonomy (self-healing + self-scheduling)
Periodic health check -> restart failed services; auto-run scheduler loops."""
import subprocess, sys, time, pathlib, json, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK_INTERVAL = 60   # seconds

def _health():
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/system/health", timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"overall": "red", "error": str(e)}

def heal_once():
    """Check health; if server unreachable, restart it. Return action taken."""
    h = _health()
    if h.get("overall") == "red" or h.get("error"):
        print(f"[autonomy] health red ({h.get('error','?')}) — restarting server")
        try:
            import socket
            s = socket.socket(); s.settimeout(1); s.connect(("127.0.0.1", 8000)); s.close()
        except Exception:
            pass
        venv = ROOT / ".venv" / "bin" / "python3"
        py = str(venv) if venv.exists() else sys.executable
        subprocess.Popen([py, "-m", "uvicorn", "scripts.server:app", "--port", "8000"],
                         cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "restarted"
    return "ok"

def run_loop(once=False):
    while True:
        action = heal_once()
        print(f"[autonomy] {datetime.datetime.now().isoformat(timespec='seconds')} health={_health().get('overall')} action={action}", flush=True)
        if once:
            return
        time.sleep(CHECK_INTERVAL)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    run_loop(once=args.once)

if __name__ == "__main__":
    main()
