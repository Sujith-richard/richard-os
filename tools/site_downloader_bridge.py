#!/usr/bin/env python3
"""Richard OS — Website-downloader bridge.
Honest status: connected / not_configured / error. Never fakes."""
import shutil, subprocess
from pathlib import Path

REPO = "https://github.com/AhmadIbrahiim/Website-downloader"
LOCAL = Path(__file__).resolve().parent.parent / "vendor" / "Website-downloader"

def status():
    if LOCAL.exists():
        return {"provider": "website-downloader", "status": "connected",
                "detail": "local clone present — download a site with: python tools/site_downloader_bridge.py <url> <outdir>"}
    if shutil.which("wget"):
        return {"provider": "website-downloader", "status": "partial",
                "detail": "using wget fallback — install the repo for the full tool"}
    return {"provider": "website-downloader", "status": "not_configured",
            "detail": f"clone {REPO} into vendor/ (or use wget fallback)"}

def download(url, outdir="06-data/downloads"):
    """Download a site: prefer the repo tool, fall back to wget (honest)."""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    if LOCAL.exists():
        try:
            r = subprocess.run(["node", str(LOCAL / "index.js"), url, str(out)], capture_output=True, text=True, timeout=120)
            return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[:200]}
        except Exception as e:
            return {"error": str(e)[:150]}
    if shutil.which("wget"):
        try:
            r = subprocess.run(["wget", "-r", "-P", str(out), url], capture_output=True, text=True, timeout=120)
            return {"ok": r.returncode == 0, "detail": f"wget fallback used (exit {r.returncode})"}
        except Exception as e:
            return {"error": str(e)[:150]}
    return {"error": "no downloader available — clone the repo or install wget (honest)"}

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        print(json.dumps(download(sys.argv[1]), indent=2))
    else:
        print(json.dumps(status(), indent=2))

