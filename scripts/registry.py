#!/usr/bin/env python3
"""
scripts/registry.py - #13 Resource Intelligence registry aggregator
Unifies: tools (tools_config.json), MCP tools (mcp_tools.status),
repos (repos.json / live-github), resource packages, plugins.
Honest per-category counts + statuses.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS_CFG = ROOT / "tools" / "tools_config.json"
REPOS_JSON = ROOT / "tools" / "repos.json"

def _tools():
    if TOOLS_CFG.exists():
        try:
            d = json.loads(TOOLS_CFG.read_text())
            return [{"name": k, **v} for k, v in d.items()]
        except Exception:
            pass
    return []

def _mcp():
    try:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import mcp_tools
        st = mcp_tools.status()
        return [{"name": k, "status": v} for k, v in (st or {}).items()]
    except Exception as e:
        return [{"error": str(e)}]

def _repos():
    import json as _j
    out, seen = [], set()
    def add(n, st):
        if n and n not in seen:
            out.append({"name": n, "status": st}); seen.add(n)
    try:
        live = ROOT / "06-data" / "live_github.json"
        if live.exists():
            for r in _j.loads(live.read_text()).get("repos", []):
                add(r, "live")
    except Exception: pass
    try:
        idir = ROOT / "06-data" / "repo_intel"
        if idir.exists():
            for f in sorted(idir.glob("*.json")):
                d = _j.loads(f.read_text())
                add(d.get("name") or f.stem, "intel")
    except Exception: pass
    try:
        if REPOS_JSON.exists():
            for k, v in _j.loads(REPOS_JSON.read_text()).items():
                add(v.get("name", k) if isinstance(v, dict) else k, "static")
    except Exception: pass
    return out

def _packages():
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8000/resource-packages", timeout=5) as r:
            d = json.loads(r.read().decode())
            return d.get("packages", [])
    except Exception:
        return []

def _plugins():
    # plugin registry: look for a plugins dir/config; honest empty if none
    cfg = ROOT / "06-data" / "plugins.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text()).get("plugins", [])
        except Exception:
            pass
    return []

def registry(category=None):
    data = {
        "tools": _tools(), "mcp": _mcp(), "repos": _repos(),
        "packages": _packages(), "plugins": _plugins(),
    }
    if category:
        return {"ok": True, "category": category, "items": data.get(category, [])}
    return {"ok": True, "categories": {
        "tools": {"count": len(data["tools"]), "items": data["tools"]},
        "mcp": {"count": len(data["mcp"]), "items": data["mcp"]},
        "repos": {"count": len(data["repos"]), "items": data["repos"]},
        "packages": {"count": len(data["packages"]), "items": data["packages"]},
        "plugins": {"count": len(data["plugins"]), "items": data["plugins"]},
    }}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", metavar="CAT")
    args = ap.parse_args()
    print(json.dumps(registry(args.category), indent=2))

if __name__ == "__main__":
    main()
