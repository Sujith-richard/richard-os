#!/usr/bin/env python3
"""scripts/package_manager.py - v5.3 Package Manager
The universal mechanism: everything is an installable package
(departments, skills, workflows, prompts, structures, plugins).
Manifest + registry + version + install/uninstall. Extends plugin_store."""
import json, sqlite3, pathlib, datetime, shutil, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "06-data" / "package_manager.db"
PACKAGE_DIRS = {
    "department": ROOT / "02-blocks" / "company",
    "skill": ROOT / "04-skills",
    "workflow": ROOT / "06-data",
    "structure": ROOT / "06-data" / "datasets",
}

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""CREATE TABLE IF NOT EXISTS packages (
        name TEXT PRIMARY KEY, kind TEXT, version TEXT, status TEXT DEFAULT 'installed',
        source TEXT, installed_at TEXT)""")
    c.commit(); c.close()

def _discover_local():
    """Discover all installable packages from the OS itself."""
    pkgs = []
    # departments
    for d in (ROOT / "02-blocks" / "company").glob("*.yaml"):
        pkgs.append({"name": d.stem, "kind": "department", "version": "1.0.0", "source": str(d)})
    # skills
    for f in (ROOT / "04-skills").glob("*.md"):
        pkgs.append({"name": f.stem, "kind": "skill", "version": "1.0.0", "source": str(f)})
    # workflows
    try:
        import sqlite3 as sq
        c = sq.connect(ROOT / "06-data" / "workflows.db"); c.row_factory = sq.Row
        for r in c.execute("SELECT name, title FROM workflows"):
            pkgs.append({"name": r["name"], "kind": "workflow", "version": "1.0.0", "source": r["title"]})
        c.close()
    except Exception: pass
    # structures
    for f in (ROOT / "06-data" / "datasets").glob("*.jsonl"):
        pkgs.append({"name": f.stem, "kind": "structure", "version": "1.0.0", "source": str(f)})
    return pkgs

def list_packages(kind=None):
    init_db()
    local = _discover_local()
    c = _conn()
    installed = {r["name"] for r in c.execute("SELECT name FROM packages WHERE status='installed'").fetchall()}
    c.close()
    out = [{**p, "status": "installed" if p["name"] in installed else "available"} for p in local]
    if kind:
        out = [p for p in out if p["kind"] == kind]
    return {"ok": True, "packages": out}

def install(name):
    """Mark a discovered package as installed (register it)."""
    init_db()
    pkgs = {p["name"]: p for p in _discover_local()}
    if name not in pkgs:
        return {"ok": False, "error": f"package '{name}' not found"}
    p = pkgs[name]
    c = _conn()
    c.execute("""INSERT OR REPLACE INTO packages (name, kind, version, status, source, installed_at)
                 VALUES (?,?,?, 'installed', ?, ?)""", (name, p["kind"], p["version"], p["source"], _now()))
    c.commit(); c.close()
    # publish event
    try:
        import sys; sys.path.insert(0, str(ROOT / "scripts"))
        from system_services import publish
        publish("package.installed", f"{name} ({p['kind']} v{p['version']})")
    except Exception: pass
    return {"ok": True, "installed": name, "kind": p["kind"], "version": p["version"]}

def uninstall(name):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM packages WHERE name=?", (name,)).fetchone()
    if not row:
        c.close(); return {"ok": False, "error": "not registered"}
    c.execute("UPDATE packages SET status='removed' WHERE name=?", (name,))
    c.commit(); c.close()
    return {"ok": True, "removed": name}

def installed():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM packages WHERE status='installed'").fetchall()
    c.close()
    return {"ok": True, "installed": [dict(r) for r in rows]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", nargs="?", const="")
    ap.add_argument("--install", metavar="NAME")
    ap.add_argument("--uninstall", metavar="NAME")
    ap.add_argument("--installed", action="store_true")
    args = ap.parse_args()
    if args.list is not None:
        kind = args.list or None
        for p in list_packages(kind)["packages"]:
            print(f"  {p['status']:10s} {p['kind']:12s} {p['name']}")
        return
    if args.install:
        print(json.dumps(install(args.install), indent=2)); return
    if args.uninstall:
        print(json.dumps(uninstall(args.uninstall), indent=2)); return
    if args.installed:
        for p in installed()["installed"]:
            print(f"  {p['name']:24s} {p['kind']:12s} v{p['version']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
