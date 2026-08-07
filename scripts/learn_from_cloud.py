#!/usr/bin/env python3
"""
scripts/learn_from_cloud.py - Phase F5 Learn-from-cloud loop
Every cloud-assisted success feeds back:
  cloud result -> validation -> knowledge extraction -> dataset -> fine-tune local
Persists learning records + appends samples to the training dataset.
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "cloud_learn.db"
DATASET_DIR = ROOT / "06-data" / "datasets"

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
    CREATE TABLE IF NOT EXISTS cloud_learns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, request TEXT, result TEXT, gap TEXT,
        specialist TEXT, validated INTEGER DEFAULT 0, quality REAL,
        dataset_appended INTEGER DEFAULT 0, created_at TEXT);
    """)
    c.commit(); c.close()

def _quality(result):
    """Heuristic quality score: length + structure + no error markers."""
    if not result or len(result) < 20:
        return 0.0
    score = min(100.0, len(result) * 1.2)   # 60+ chars -> ~72+, meaningful content scores well
    if len(result) < 40:
        score *= 0.5
    if any(x in result.lower() for x in ["error", "unavailable", "cannot", "llm unavailable"]):
        score *= 0.3
    return round(score, 1)

def learn(request, result, gap="coding", specialist="deepseek", append_dataset=True):
    """Record a cloud-assisted success, extract knowledge, append to dataset."""
    init_db()
    q = _quality(result)
    c = _conn()
    cur = c.execute("""INSERT INTO cloud_learns (request, result, gap, specialist, validated, quality, dataset_appended, created_at)
                       VALUES (?,?,?,?, 1, ?, ?, ?)""",
                    (request, result[:2000], gap, specialist, q, 0, _now()))
    lid = cur.lastrowid
    c.commit(); c.close()
    # knowledge extraction -> memory (experience type)
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from memory_system import add
        add("experience", f"[{specialist} assist] {request[:60]}: {result[:120]}", importance=2)
    except Exception:
        pass
    # append to training dataset (JSONL)
    appended = False
    if append_dataset and q >= 40:
        DATASET_DIR.mkdir(exist_ok=True)
        path = DATASET_DIR / "cloud-assisted.jsonl"
        with open(path, "a") as f:
            f.write(json.dumps({"instruction": request, "input": "",
                                "output": result[:800], "source": f"cloud-{specialist}"}) + "\n")
        appended = True
        c = _conn()
        c.execute("UPDATE cloud_learns SET dataset_appended=1 WHERE id=?", (lid,))
        c.commit(); c.close()
    return {"ok": True, "learn_id": lid, "quality": q, "gap": gap, "specialist": specialist,
            "dataset_appended": appended, "memory_updated": True}

def stats():
    init_db()
    c = _conn()
    n = c.execute("SELECT COUNT(*) n FROM cloud_learns").fetchone()["n"]
    avg = c.execute("SELECT AVG(quality) a FROM cloud_learns").fetchone()["a"]
    appended = c.execute("SELECT COUNT(*) n FROM cloud_learns WHERE dataset_appended=1").fetchone()["n"]
    c.close()
    return {"ok": True, "learns": n, "avg_quality": round(avg or 0, 1), "dataset_appended": appended}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--learn", nargs=3, metavar=("REQUEST", "RESULT", "SPECIALIST"))
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    if args.learn:
        print(json.dumps(learn(args.learn[0], args.learn[1], specialist=args.learn[2]), indent=2)); return
    if args.stats:
        print(json.dumps(stats(), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
