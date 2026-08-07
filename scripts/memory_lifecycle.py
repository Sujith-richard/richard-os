#!/usr/bin/env python3
"""
scripts/memory_lifecycle.py - Phase D4 Memory auto-promotion + decay
Temporary memories promote to long-term by importance/recency; stale
temporary memories decay (get removed after a TTL unless promoted).
"""
import json, sqlite3, pathlib, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "memory.db"
PROMOTE_THRESHOLD_IMPORTANCE = 2   # temp with importance >= 2 -> promote
PROMOTE_AFTER_HOURS = 24           # temp older than 24h -> promote
TEMP_TTL_DAYS = 7                  # temp older than 7d (not promoted) -> delete

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def _hours_ago(dt_str):
    try:
        dt = datetime.datetime.fromisoformat(dt_str)
        return (datetime.datetime.now() - dt).total_seconds() / 3600
    except Exception:
        return 0

def run_lifecycle(dry_run=False):
    """Scan temporary memories: promote important/old ones, delete stale ones."""
    c = _conn()
    temps = c.execute("SELECT * FROM memories WHERE mtype='temporary'").fetchall()
    promoted, deleted = [], []
    for m in temps:
        age_h = _hours_ago(m["created_at"] or _now())
        if m["importance"] >= PROMOTE_THRESHOLD_IMPORTANCE or age_h >= PROMOTE_AFTER_HOURS:
            if not dry_run:
                c.execute("UPDATE memories SET mtype='long-term', updated_at=? WHERE id=?", (_now(), m["id"]))
            promoted.append({"id": m["id"], "content": m["content"][:50], "importance": m["importance"], "age_h": round(age_h, 1)})
        elif age_h >= TEMP_TTL_DAYS * 24:
            if not dry_run:
                c.execute("DELETE FROM memories WHERE id=?", (m["id"],))
            deleted.append({"id": m["id"], "content": m["content"][:50]})
    c.commit(); c.close()
    return {"ok": True, "dry_run": dry_run, "promoted": promoted, "deleted": deleted,
            "promoted_count": len(promoted), "deleted_count": len(deleted)}

def stats():
    c = _conn()
    temp = c.execute("SELECT COUNT(*) n FROM memories WHERE mtype='temporary'").fetchone()["n"]
    long = c.execute("SELECT COUNT(*) n FROM memories WHERE mtype='long-term'").fetchone()["n"]
    c.close()
    return {"ok": True, "temporary": temp, "long_term": long}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    if args.stats:
        print(json.dumps(stats(), indent=2)); return
    if args.run or args.dry_run:
        print(json.dumps(run_lifecycle(dry_run=args.dry_run), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
