#!/usr/bin/env python3
"""Richard OS — codegraph-rust bridge (code/dependency graph visualizer).
Honest status: connected / not_configured / error. Never fakes."""
import shutil
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor" / "codegraph-rust"

def status():
    if VENDOR.exists() and (VENDOR / "Cargo.toml").exists() or shutil.which("codegraph"):
        return {"provider": "codegraph-rust", "status": "connected",
                "detail": "codegraph available — Dev agent can visualize code/dependency graphs"}
    return {"provider": "codegraph-rust", "status": "not_configured",
            "detail": "clone into vendor/codegraph-rust (cargo build) to enable code-graph rendering"}

def run(repo_path="."):
    """Analyze a repo and emit a dependency graph (if available)."""
    if status()["status"] != "connected":
        return {"error": "codegraph-rust not configured (honest)"}
    try:
        import subprocess
        r = subprocess.run(["cargo", "run", "--release", "--", str(repo_path)],
                           cwd=str(VENDOR), capture_output=True, text=True, timeout=180)
        return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[:300]}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
