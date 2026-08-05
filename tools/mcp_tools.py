#!/usr/bin/env python3
"""Richard OS — MCP tool dispatcher: the AI Core chat calls these.
Each tool reports honest status; dispatch only runs if connected."""
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
        "desc": "Turn a website URL into installable apps (iPhone/Android/Windows/macOS/Linux)",
        "cmd": ["python", "main.py"], "cwd": VENDOR / "WebToApp",
        "keyword": ["web to app", "app from site", "installable app"],
    },
    "OmniCloud": {
        "desc": "Multi-cloud storage: list/upload/allocate across Google/OneDrive/Dropbox/MEGA/pCloud/Yandex/S3",
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

def status(name=None):
    if name:
        t = TOOLS.get(name)
        if not t: return {"tool": name, "status": "unknown"}
        ready = (t["cwd"]).exists()
        return {"tool": name, "desc": t["desc"], "status": "connected" if ready else "not_configured"}
    return {n: status(n)["status"] for n in TOOLS}

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
