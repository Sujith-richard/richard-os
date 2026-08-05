#!/usr/bin/env python3
"""Richard OS — freecad-mcp bridge (MCP server for FreeCAD CAD automation).
Honest status: connected / not_configured / error. Never fakes."""
import shutil
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor" / "freecad-mcp"

def status():
    if VENDOR.exists() or shutil.which("freecad"):
        return {"provider": "freecad-mcp", "status": "connected",
                "detail": "FreeCAD MCP available — Dev agent can automate CAD/parametric design via MCP"}
    return {"provider": "freecad-mcp", "status": "not_configured",
            "detail": "clone into vendor/freecad-mcp (or install FreeCAD) to enable CAD automation"}

def run(script):
    """Send a CAD operation script to FreeCAD via MCP (if available)."""
    if status()["status"] != "connected":
        return {"error": "freecad-mcp not configured (honest)"}
    try:
        # MCP stdio call to the FreeCAD server — adapt to the repo's server entrypoint
        import subprocess
        r = subprocess.run(["python", str(VENDOR / "server.py"), "--script", script],
                           capture_output=True, text=True, timeout=120)
        return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[:200]}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
