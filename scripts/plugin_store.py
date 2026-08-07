#!/usr/bin/env python3
"""
scripts/plugin_store.py - v4.0 #6 Plugin Store
Catalog: repo-intel repos (community) + tools + MCP + skills.
Install/uninstall lifecycle persisted to 06-data/plugins.db.
Tiers: local (built-in), community (ingested repo), premium (flagged).
"""
import json, sqlite3, pathlib, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "plugins.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS plugins (
        name TEXT PRIMARY KEY, kind TEXT, tier TEXT, desc TEXT, status TEXT DEFAULT 'available',
        installed_at TEXT, created_at TEXT);
    """)
    c.commit(); c.close()

def _catalog():
    """Build the catalog from live sources."""
    out = []
    # repo intel repos -> community
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from repo_intel import list_intel
        for r in list_intel():
            out.append({"name": r["name"], "kind": "repo-intel", "tier": "community",
                        "desc": f"{r['repo_type']} · {r['categories']} · dept {r['dept_mapping']}"})
    except Exception:
        pass
    # tools -> local
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from registry import _tools
        for t in _tools():
            out.append({"name": t["name"], "kind": "tool", "tier": "local", "desc": t.get("description", "")})
    except Exception:
        pass
    # MCP tools -> local
    try:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import mcp_tools
        for k, v in (mcp_tools.status() or {}).items():
            out.append({"name": k, "kind": "mcp", "tier": "local", "desc": f"status: {v}"})
    except Exception:
        pass
    # skills -> local
    for f in sorted((ROOT / "04-skills").glob("*.md")):
        out.append({"name": f.stem, "kind": "skill", "tier": "local", "desc": "promoted skill"})
    return out

def catalog():
    init_db()
    c = _conn()
    installed = {r["name"] for r in c.execute("SELECT name FROM plugins WHERE status='installed'").fetchall()}
    c.close()
    items = []
    for p in _catalog():
        items.append({**p, "status": "installed" if p["name"] in installed else "available"})
    # dedupe by name
    seen = {}
    for it in items:
        seen[it["name"]] = it
    return {"ok": True, "plugins": list(seen.values())}

def install(name):
    init_db()
    cat = {p["name"]: p for p in catalog()["plugins"]}
    if name not in cat:
        return {"ok": False, "error": f"plugin '{name}' not in catalog"}
    c = _conn()
    p = cat[name]
    c.execute("""INSERT OR REPLACE INTO plugins (name, kind, tier, desc, status, installed_at, created_at)
                 VALUES (?,?,?,?, 'installed', ?, ?)""",
              (p["name"], p["kind"], p["tier"], p["desc"], _now(), _now()))
    c.commit(); c.close()
    return {"ok": True, "name": name, "status": "installed"}

def uninstall(name):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM plugins WHERE name=?", (name,)).fetchone()
    if not row or row["status"] != "installed":
        c.close(); return {"ok": False, "error": "not installed"}
    c.execute("DELETE FROM plugins WHERE name=?", (name,))
    c.commit(); c.close()
    return {"ok": True, "name": name, "status": "uninstalled"}

def status():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM plugins WHERE status='installed' ORDER BY installed_at DESC").fetchall()
    c.close()
    return {"ok": True, "installed": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", action="store_true")
    ap.add_argument("--install", metavar="NAME")
    ap.add_argument("--uninstall", metavar="NAME")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.catalog:
        for p in catalog()["plugins"]:
            print(f"  {p['status']:10s} {p['tier']:10s} {p['kind']:12s} {p['name']}")
        return
    if args.install:
        print(json.dumps(install(args.install), indent=2)); return
    if args.uninstall:
        print(json.dumps(uninstall(args.uninstall), indent=2)); return
    if args.status:
        for p in status()["installed"]:
            print(f"  {p['name']:24s} {p['kind']:12s} {p['tier']:10s} {p['installed_at']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
