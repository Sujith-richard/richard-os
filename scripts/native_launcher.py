#!/usr/bin/env python3
"""native_launcher.py - Launch Richard OS in a DESKTOP-STYLE window (no browser chrome).
Tries in order: pywebview (real native window) -> Tauri (if built) -> browser (fallback)."""
import subprocess, sys, time, socket, pathlib, webbrowser
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
        venv = ROOT / ".venv" / "bin" / "python3"
        py = str(venv) if venv.exists() else sys.executable
        subprocess.Popen([py, "-m", "uvicorn", "scripts.server:app", "--port", str(PORT)],
                         cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(40):
            time.sleep(0.5)
            if _is_up(): break
    # 1) real native window via pywebview
    try:
        import webview
        webview.create_window("Richard OS", URL, width=1280, height=800, resizable=True)
        webview.start()
        return
    except Exception as e:
        print("pywebview unavailable (%s); trying Tauri-built app..." % str(e)[:50])
    # 2) Tauri built binary (if present)
    for cand in ["src-tauri/target/release/richard-os", "src-tauri/target/release/richard-os-studio.exe"]:
        if (ROOT / cand).exists():
            subprocess.Popen([str(ROOT / cand)]); return
    # 3) fallback: browser
    print("no native runtime — opening in browser (install pywebview or Rust for a desktop window)")
    webbrowser.open(URL)
if __name__ == "__main__":
    main()
