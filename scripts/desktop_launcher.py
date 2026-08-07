#!/usr/bin/env python3
"""scripts/desktop_launcher.py - Phase H2 Native wrapper (desktop launcher)
Starts the Richard OS server (if not running) and opens the shell.
Cross-platform (webbrowser + subprocess)."""
import subprocess, sys, time, webbrowser, socket, pathlib, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8000
URL = f"http://127.0.0.1:{PORT}/ui/"

def _is_up():
    s = socket.socket(); s.settimeout(1)
    try:
        s.connect(("127.0.0.1", PORT)); s.close(); return True
    except Exception:
        return False
    finally:
        s.close()

def main():
    if not _is_up():
        print("starting Richard OS server...")
        venv = ROOT / ".venv" / "bin" / "python3"
        py = str(venv) if venv.exists() else sys.executable
        subprocess.Popen([py, "-m", "uvicorn", "scripts.server:app", "--port", str(PORT)],
                         cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            time.sleep(0.5)
            if _is_up():
                break
    print("opening", URL)
    webbrowser.open(URL)

if __name__ == "__main__":
    main()
