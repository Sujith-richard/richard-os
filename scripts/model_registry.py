#!/usr/bin/env python3
"""
scripts/model_registry.py - Phase E4 Model Registry
Versioned fine-tuned checkpoints: register, list, promote (active), rollback,
deploy (write active pointer for local_inference to load).
Persists to 06-data/model_registry.db + 06-data/models/ACTIVE.txt.
"""
import json, sqlite3, pathlib, datetime, argparse, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "model_registry.db"
MODELS_DIR = ROOT / "06-data" / "models"
ACTIVE_POINTER = MODELS_DIR / "ACTIVE.txt"

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
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, path TEXT,
        dataset TEXT, samples INTEGER, eval_score REAL DEFAULT 0,
        version INTEGER DEFAULT 1, status TEXT DEFAULT 'registered',
        created_at TEXT, updated_at TEXT);
    """)
    c.commit(); c.close()

def register(name, path, dataset="", samples=0, eval_score=0):
    init_db()
    c = _conn()
    # bump version if re-registering same name
    existing = c.execute("SELECT MAX(version) v FROM models WHERE name=?", (name,)).fetchone()["v"]
    version = (existing or 0) + 1
    c.execute("""INSERT INTO models (name, path, dataset, samples, eval_score, version, status, created_at, updated_at)
                 VALUES (?,?,?,?,?,?, 'registered', ?, ?)""",
              (name, str(path), dataset, samples, eval_score, version, _now(), _now()))
    c.commit(); c.close()
    return {"ok": True, "name": name, "version": version, "path": str(path)}

def list_models():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM models ORDER BY id DESC").fetchall()
    active = ACTIVE_POINTER.read_text().strip() if ACTIVE_POINTER.exists() else "none"
    c.close()
    return {"ok": True, "active": active, "models": [dict(r) for r in rows]}

def promote(model_id):
    """Mark a model as active + write the deploy pointer."""
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM models WHERE id=?", (model_id,)).fetchone()
    if not row:
        c.close(); return {"ok": False, "error": "model not found"}
    # archive previous active
    c.execute("UPDATE models SET status='archived', updated_at=? WHERE status='active'", (_now(),))
    c.execute("UPDATE models SET status='active', updated_at=? WHERE id=?", (_now(), model_id))
    c.commit()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_POINTER.write_text(row["path"])   # deploy: pointer -> checkpoint dir
    c.close()
    return {"ok": True, "active": row["name"], "version": row["version"], "deployed_to": str(ACTIVE_POINTER)}

def rollback(model_id):
    """Roll back to a previous version (set active + deploy)."""
    return promote(model_id)

def deploy(model_id=None):
    """Deploy the active model (or a specific id) — write the pointer."""
    init_db()
    c = _conn()
    if model_id:
        row = c.execute("SELECT * FROM models WHERE id=?", (model_id,)).fetchone()
    else:
        row = c.execute("SELECT * FROM models WHERE status='active' ORDER BY id DESC LIMIT 1").fetchone()
    c.close()
    if not row:
        return {"ok": False, "error": "no active model"}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_POINTER.write_text(row["path"])
    return {"ok": True, "deployed": row["name"], "path": row["path"]}

def active_model():
    """Path of the deployed active model (for local_inference to read)."""
    if ACTIVE_POINTER.exists():
        p = ACTIVE_POINTER.read_text().strip()
        if p and pathlib.Path(p).exists():
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", nargs=4, metavar=("NAME", "PATH", "DATASET", "SAMPLES"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--promote", metavar="ID")
    ap.add_argument("--rollback", metavar="ID")
    ap.add_argument("--deploy", metavar="ID", nargs="?", const="")
    args = ap.parse_args()
    if args.register:
        print(json.dumps(register(args.register[0], args.register[1], args.register[2], int(args.register[3])), indent=2)); return
    if args.list:
        d = list_models()
        print(f"active: {d['active']}")
        for m in d["models"]:
            print(f"  [{m['id']}] {m['name']:30s} v{m['version']} eval={m['eval_score']} {m['status']}")
        return
    if args.promote:
        print(json.dumps(promote(int(args.promote)), indent=2)); return
    if args.rollback:
        print(json.dumps(rollback(int(args.rollback)), indent=2)); return
    if args.deploy is not None:
        print(json.dumps(deploy(int(args.deploy)) if args.deploy else deploy(), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
