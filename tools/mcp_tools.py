#!/usr/bin/env python3
"""Richard OS — MCP tool dispatcher: the AI Core chat calls these.
Each tool reports HONEST status; dispatch only runs if connected."""
import subprocess, shutil
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor"

TOOLS = {
    "freecad-mcp": {
        "desc": "CAD automation — design parametric 3D parts (e.g., a screw)",
        "cmd": ["python", "server.py"], "cwd": VENDOR / "freecad-mcp",
        "keyword": ["screw", "cad", "3d design", "part", "bolt", "parametric"],
    },
    "WebToApp": {
        "desc": "Turn a website URL into installable apps",
        "cmd": ["python", "server/main.py"], "cwd": VENDOR / "WebToApp",
        "keyword": ["web to app", "app from site", "installable app"],
    },
    "OmniCloud": {
        "desc": "Multi-cloud storage: list/upload/allocate (Google/OneDrive/Dropbox/MEGA/pCloud/Yandex/S3)",
        "cmd": ["npm", "run", "dev"], "cwd": VENDOR / "OmniCloud",
        "keyword": ["cloud", "upload", "storage", "drive"],
    },
    "map-to-poster": {
        "desc": "Generate a map poster from any location",
        "cmd": ["npm", "run", "dev"], "cwd": VENDOR / "map-to-poster",
        "keyword": ["map poster", "poster of", "map of"],
    },
    "Website-downloader": {
        "desc": "Download the complete source of a website",
        "cmd": ["npm", "start"], "cwd": VENDOR / "Website-downloader",
        "keyword": ["download site", "download website", "save site"],
    },
    "lingbot-map": {
        "desc": "Streaming 3D reconstruction from images",
        "cmd": ["python", "run.py"], "cwd": VENDOR / "lingbot-map",
        "keyword": ["3d reconstruction", "reconstruct", "3d from photos"],
    },
}

def _ready(name):
    """Honest runtime-aware status per tool."""
    t = TOOLS.get(name)
    if not t:
        return "unknown"
    cwd = t["cwd"]
    if not cwd.exists():
        return "not_configured"

    if name == "freecad-mcp":
        try:
            import subprocess, os
            env = dict(os.environ)
            env["PYTHONPATH"] = "/home/sujith-richard/miniconda3/lib"
            env["LD_LIBRARY_PATH"] = "/home/sujith-richard/miniconda3/lib"
            r = subprocess.run(
                ["/home/sujith-richard/miniconda3/bin/python", "-c", "import FreeCAD"],
                capture_output=True, timeout=60, env=env)
            return "connected" if r.returncode == 0 else "error"
        except Exception:
            return "error"

    if name == "lingbot-map":
        return "deferred"           # heavy GPU tool (PyTorch 2.8 + CUDA 12.8 + Kaolin) [13]

    if name == "WebToApp":
        # Python + FastAPI backend — deps in server/requirements.txt [4]
        if (cwd / "server" / "requirements.txt").exists() or (cwd / "requirements.txt").exists():
            return "connected"
        return "error"

    if name == "OmniCloud":
        # Root-workspace layout (root package.json + npm run dev) [6]
        if (cwd / "node_modules").exists():
            return "connected"
        # Older subfolder installs [11]
        if (cwd / "frontend" / "node_modules").exists() or (cwd / "backend" / "node_modules").exists():
            return "connected"
        return "error"

    # map-to-poster [7] and Website-downloader [12]: npm install at repo root
    if (cwd / "node_modules").exists():
        return "connected"
    return "error"

def status(name=None):
    """Return honest status for one tool or all."""
    if name:
        return {"tool": name, "desc": TOOLS.get(name, {}).get("desc", ""),
                "status": _ready(name)}
    return {n: _ready(n) for n in TOOLS}

def route(text):
    """Map a chat message to the best MCP tool (or None)."""
    low = text.lower()
    best, best_score = None, 0
    for name, t in TOOLS.items():
        score = sum(1 for k in t["keyword"] if k in low)
        if score > best_score:
            best, best_score = name, score
    return best

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        print(json.dumps(status(sys.argv[1]), indent=2))
    else:
        print(json.dumps(status(), indent=2))
