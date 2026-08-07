#!/usr/bin/env python3
"""scripts/version_manager.py - v5.6 Version everything
Versions skills, knowledge, prompts, departments (and models via registry).
Snapshots content with a version number + history; rollback supported."""
import json, sqlite3, pathlib, datetime, hashlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "06-data" / "version_manager.db"

KINDS = {
    "skill": ROOT / "04-skills",
    "knowledge": ROOT / "02-blocks" / "company",
    "department": ROOT / "02-blocks" / "company",
}

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""CREATE TABLE IF NOT EXISTS versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, name TEXT, version INT,
        content_hash TEXT, content TEXT, created_at TEXT,
        UNIQUE(kind, name, version))""")
    c.commit(); c.close()

def _snapshot(kind, name):
    """Read current content of a skill/department file."""
    base = KINDS.get(kind)
    if not base: return None
    # skill: 04-skills/<name>.md ; department: 02-blocks/company/<name>.yaml
    if kind == "skill":
        p = base / f"{name}.md"
    else:
        p = base / f"{name}.yaml"
        if not p.exists() and kind == "knowledge":
            p = base / name / "knowledge" / f"{name}-overview.md"
    return p.read_text(errors="ignore") if p.exists() else None

def version(kind, name):
    """Snapshot current content as a new version."""
    init_db()
    content = _snapshot(kind, name)
    if content is None:
        return {"ok": False, "error": f"{kind}/{name} not found"}
    ch = hashlib.sha256(content.encode()).hexdigest()[:12]
    c = _conn()
    last = c.execute("SELECT MAX(version) v FROM versions WHERE kind=? AND name=?", (kind, name)).fetchone()["v"]
    v = (last or 0) + 1
    c.execute("INSERT INTO versions (kind, name, version, content_hash, content, created_at) VALUES (?,?,?,?,?,?)",
              (kind, name, v, ch, content[:2000], _now()))
    c.commit(); c.close()
    return {"ok": True, "kind": kind, "name": name, "version": v, "hash": ch}

def history(kind=None, name=None):
    init_db()
    c = _conn()
    q = "SELECT id, kind, name, version, content_hash, created_at FROM versions"
    args = []
    if kind:
        q += " WHERE kind=?"; args.append(kind)
        if name:
            q += " AND name=?"; args.append(name)
    q += " ORDER BY id DESC LIMIT 50"
    rows = c.execute(q, args).fetchall()
    c.close()
    return {"ok": True, "versions": [dict(r) for r in rows]}

def rollback(kind, name, version):
    """Restore content to a previous version (re-write file)."""
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM versions WHERE kind=? AND name=? AND version=?", (kind, name, version)).fetchone()
    c.close()
    if not row:
        return {"ok": False, "error": "version not found"}
    base = KINDS.get(kind)
    p = base / f"{name}.md" if kind == "skill" else base / f"{name}.yaml"
    if kind == "knowledge":
        p = base / name / "knowledge" / f"{name}-overview.md"
    if p and p.exists():
        p.write_text(row["content"])
    return {"ok": True, "restored": f"{kind}/{name} -> v{version}"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", nargs=2, metavar=("KIND", "NAME"))
    ap.add_argument("--history", nargs="*", metavar=("KIND", "NAME"))
    ap.add_argument("--rollback", nargs=3, metavar=("KIND", "NAME", "VERSION"))
    args = ap.parse_args()
    if args.version:
        print(json.dumps(version(*args.version), indent=2)); return
    if args.history:
        kind = args.history[0]; name = args.history[1] if len(args.history) > 1 else None
        for v in history(kind, name)["versions"]:
            print(f"  {v['kind']:12s} {v['name']:26s} v{v['version']} {v['content_hash']}")
        return
    if args.rollback:
        print(json.dumps(rollback(*args.rollback), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
