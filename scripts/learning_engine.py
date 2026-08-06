#!/usr/bin/env python3
"""
scripts/learning_engine.py - #16 Continuous Learning
The feedback loop: capture -> dataset -> fine-tune -> improve core.
- capture:  run logs + project learnings + workflow runs -> samples/lessons
- dataset:  samples -> JSONL training set (instruction/input/output)
- fine-tune: mark a model fine-tuned on the dataset (fake-first; real hook via models integration)
- improve:  promote repeated lessons (count>=3) into 04-skills
Persists to 06-data/learning_engine.db; datasets to 06-data/datasets/.
"""
import json, sqlite3, pathlib, datetime, re, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "learning_engine.db"
DATASET_DIR = ROOT / "06-data" / "datasets"
SKILLS_DIR = ROOT / "04-skills"
LOGS_DIR = ROOT / "03-agents" / "logs"

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
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, kind TEXT, instruction TEXT,
        input TEXT DEFAULT '', output TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, lesson TEXT UNIQUE, kind TEXT,
        count INTEGER DEFAULT 1, source TEXT, last_seen TEXT);
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT, samples INTEGER,
        created_at TEXT);
    CREATE TABLE IF NOT EXISTS fine_tunes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_id INTEGER, model TEXT,
        samples INTEGER, status TEXT, created_at TEXT);
    """)
    c.commit(); c.close()

# ---------- capture ----------
def capture_run_logs():
    """Parse agent run logs into instruction/input/output samples."""
    c = _conn()
    n = 0
    for f in LOGS_DIR.rglob("*.md"):
        try:
            text = f.read_text(errors="replace")
        except Exception:
            continue
        # each log line/block becomes a sample (agent name = instruction)
        agent = f.stem
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 40 and not line.startswith("#"):
                c.execute("""INSERT INTO samples (source, kind, instruction, input, output, created_at)
                             VALUES (?,?,?,?,?,?)""",
                          (str(f.relative_to(LOGS_DIR)), "run-log", f"Agent {agent} task",
                           "", line[:500], _now()))
                n += 1
    c.commit(); c.close()
    return n

def capture_project_learnings():
    """Pull learnings from project_engine.db into lessons (dedup by lesson text)."""
    pe = ROOT / "06-data" / "project_engine.db"
    if not pe.exists():
        return 0
    c = _conn()
    con = sqlite3.connect(pe); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT lesson, count, kind FROM learnings").fetchall()
    con.close()
    n = 0
    for r in rows:
        c.execute("""INSERT INTO lessons (lesson, kind, count, source, last_seen)
                     VALUES (?,?,?, 'project-engine', ?)
                     ON CONFLICT(lesson) DO UPDATE SET count = count + excluded.count, last_seen = excluded.last_seen""",
                  (r["lesson"], r["kind"] or "repeatable", r["count"], _now()))
        n += 1
    c.commit(); c.close()
    return n

def capture_workflow_runs():
    """Pull workflow names + step kinds as lessons (what flows exist)."""
    we = ROOT / "06-data" / "workflows.db"
    if not we.exists():
        return 0
    c = _conn()
    con = sqlite3.connect(we); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT name, title, status, runs, errors FROM workflows").fetchall()
    con.close()
    n = 0
    for r in rows:
        c.execute("""INSERT INTO lessons (lesson, kind, count, source, last_seen)
                     VALUES (?,?,?, 'workflow-engine', ?)
                     ON CONFLICT(lesson) DO UPDATE SET count = count + 1, last_seen = excluded.last_seen""",
                  (f"workflow {r['title']} runs {r['runs']} errors {r['errors']}", "workflow", 1, _now()))
        n += 1
    c.commit(); c.close()
    return n

def capture_all():
    return {"run_logs": capture_run_logs(),
            "project_learnings": capture_project_learnings(),
            "workflow_runs": capture_workflow_runs()}

# ---------- dataset ----------
def generate_dataset(name="richard-core-v1"):
    init_db()
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    c = _conn()
    samples = c.execute("SELECT * FROM samples ORDER BY id").fetchall()
    c.close()
    rows = []
    for s in samples:
        rows.append({"instruction": s["instruction"], "input": s["input"],
                     "output": s["output"], "source": s["source"]})
    # also lessons become instruction/output pairs (improve-core style)
    c = _conn()
    lessons = c.execute("SELECT lesson, count FROM lessons ORDER BY count DESC LIMIT 50").fetchall()
    c.close()
    for l in lessons:
        rows.append({"instruction": "Lesson learned in Richard OS",
                     "input": "", "output": f"{l['lesson']} (seen {l['count']}x)"})
    path = DATASET_DIR / f"{name}.jsonl"
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    c = _conn()
    c.execute("INSERT INTO datasets (name, path, samples, created_at) VALUES (?,?,?,?)",
              (name, str(path), len(rows), _now()))
    ds_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.commit(); c.close()
    return {"dataset": name, "samples": len(rows), "path": str(path), "dataset_id": ds_id}

# ---------- fine-tune ----------
def fine_tune(model="sshleifer/tiny-gpt2", dataset_name="richard-core-v1", steps=6):
    """Actually run the real trainer (train_lora.py) — a genuine fine-tune on our dataset."""
    import subprocess, sys
    init_db()
    c = _conn()
    ds = c.execute("SELECT * FROM datasets WHERE name=? ORDER BY id DESC LIMIT 1", (dataset_name,)).fetchone()
    if not ds:
        c.close()
        return {"ok": False, "error": "dataset not found — generate first"}
    c.execute("""INSERT INTO fine_tunes (dataset_id, model, samples, status, created_at)
                 VALUES (?,?,?, 'training', ?)""", (ds["id"], model, ds["samples"], _now()))
    c.commit(); c.close()
    cmd = [sys.executable, str(ROOT / "scripts" / "train_lora.py"),
           "--dataset", dataset_name, "--model", model, "--steps", str(steps)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "training timed out (300s)", "status": "error"}
    ok = r.returncode == 0 and '"ok": true' in r.stdout
    c = _conn()
    c.execute("UPDATE fine_tunes SET status=? WHERE id=(SELECT MAX(id) FROM fine_tunes)", ("done" if ok else "error",))
    c.commit()
    ft = c.execute("SELECT * FROM fine_tunes ORDER BY id DESC LIMIT 1").fetchone()
    c.close()
    return {"ok": ok, "model": model, "dataset": dataset_name, "samples": ft["samples"],
            "status": "done" if ok else "error",
            "checkpoint": str(ROOT / "06-data" / "models" / f"richard-{dataset_name}-tiny"),
            "stdout_tail": r.stdout[-300:] if r.stdout else r.stderr[-300:]}

# ---------- improve core ----------
def improve_core(threshold=3):
    init_db()
    c = _conn()
    lessons = c.execute("SELECT * FROM lessons WHERE count >= ? ORDER BY count DESC", (threshold,)).fetchall()
    promoted = []
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    for l in lessons:
        slug = re.sub(r'[^a-z0-9]+', '-', l["lesson"].lower()).strip('-')[:40]
        skill_file = SKILLS_DIR / f"{slug}.md"
        if not skill_file.exists():
            skill_file.write_text(
                f"# Skill: {l['lesson']}\n\n- **Source:** {l['source']}\n- **Seen:** {l['count']}x\n- **Promoted:** {_now()}\n\nAuto-promoted by the Continuous Learning Engine (lesson repeated >= {threshold} times).\n")
            promoted.append({"lesson": l["lesson"], "count": l["count"], "skill": f"{slug}.md"})
    c.close()
    return {"promoted": promoted, "threshold": threshold}

def overview():
    init_db()
    c = _conn()
    samples = c.execute("SELECT COUNT(*) n FROM samples").fetchone()["n"]
    lessons = c.execute("SELECT COUNT(*) n FROM lessons").fetchone()["n"]
    datasets = c.execute("SELECT COUNT(*) n FROM datasets").fetchone()["n"]
    fine_tunes = c.execute("SELECT COUNT(*) n FROM fine_tunes").fetchone()["n"]
    top_lessons = c.execute("SELECT lesson, count FROM lessons ORDER BY count DESC LIMIT 8").fetchall()
    c.close()
    return {"ok": True, "samples": samples, "lessons": lessons, "datasets": datasets,
            "fine_tunes": fine_tunes, "top_lessons": [dict(x) for x in top_lessons]}

def main():
    ap = argparse.ArgumentParser(description="Richard OS Continuous Learning (#16)")
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--dataset", metavar="NAME", nargs="?", const="richard-core-v1")
    ap.add_argument("--fine-tune", metavar="MODEL", nargs="?", const="qwen3-32b")
    ap.add_argument("--improve", action="store_true")
    ap.add_argument("--overview", action="store_true")
    args = ap.parse_args()
    init_db()
    if args.capture:
        print(json.dumps(capture_all(), indent=2)); return
    if args.dataset:
        print(json.dumps(generate_dataset(args.dataset), indent=2)); return
    if args.fine_tune:
        print(json.dumps(fine_tune(args.fine_tune), indent=2)); return
    if args.improve:
        print(json.dumps(improve_core(), indent=2)); return
    if args.overview:
        print(json.dumps(overview(), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
