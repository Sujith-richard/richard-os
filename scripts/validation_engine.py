#!/usr/bin/env python3
"""
scripts/validation_engine.py - v4.0 #3 Validation Engine
10-dimension validator over a directory of files (project output, repo intel,
any generated deliverable). Each dim 0-100, composite weighted score, gate.
Persists reports to 06-data/validation.db.
"""
import re, sqlite3, pathlib, json, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "validation.db"

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
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, composite REAL, gate TEXT,
        dims TEXT, created_at TEXT);
    """)
    c.commit(); c.close()

def _files(target):
    p = pathlib.Path(target)
    if p.is_file():
        return [p]
    return [f for f in p.rglob("*") if f.is_file() and ".git" not in f.parts]

def _text(files):
    out = []
    for f in files:
        try:
            out.append(f.read_text(errors="ignore"))
        except Exception:
            pass
    return out

# ---------- 10 dimensions ----------
def dim_code_review(texts, files):
    score = 100
    for t in texts:
        if re.search(r"TODO|FIXME|HACK|XXX", t): score -= 5
        if re.search(r"print\(", t) and re.search(r"def ", t): score -= 2   # debug prints in code
    return max(0, score)

def dim_security(texts, files):
    findings = 0
    pats = [r"sk-[A-Za-z0-9]{16,}", r"AKIA[0-9A-Z]{16}", r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)secret\s*=\s*['\"][^'\"]+['\"]", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"]
    for t in texts:
        for pat in pats:
            findings += len(re.findall(pat, t))
    return max(0, 100 - findings * 15)

def dim_performance(texts):
    score = 100
    for t in texts:
        if re.search(r"while\s+True", t): score -= 10
        if re.search(r"\.\.\.", t): score -= 5
        if re.search(r"time\.sleep\(\s*[0-9]+\)", t): score -= 3
    return max(0, score)

def dim_accessibility(texts, files):
    html = [t for f, t in zip(files, texts) if f.suffix in (".html", ".jsx", ".tsx")]
    if not html: return 80   # no UI = N/A-ish, neutral
    score = 100
    for t in html:
        if "<img" in t and "alt=" not in t: score -= 10
        if "<button" in t and "aria-" not in t: score -= 5
    return max(0, score)

def dim_ui(texts, files):
    css = [t for f, t in zip(files, texts) if f.suffix in (".css", ".scss")]
    if not css: return 80
    score = 100
    for t in css:
        if "color:" not in t and "background:" not in t: score -= 10
        if "var(--" not in t: score -= 5
    return max(0, score)

def dim_testing(texts, files):
    n_test = sum(1 for f in files if "test" in f.name.lower() or "spec" in f.name.lower())
    has_pytest = any("pytest" in t for t in texts)
    score = min(100, n_test * 25 + (20 if has_pytest else 0))
    return score

def dim_linting(texts, files):
    score = 100
    for f in files:
        if f.suffix == ".py":
            try:
                import ast; ast.parse(f.read_text(errors="ignore")); 
            except Exception:
                score -= 40
        if f.suffix == ".json":
            try: json.loads(f.read_text(errors="ignore"))
            except Exception: score -= 20
    return max(0, score)

def dim_documentation(texts, files):
    has_readme = any(f.name.lower() in ("readme.md", "readme") for f in files)
    has_docstrings = sum(1 for t in texts if '"""' in t or "'''" in t)
    has_docs_dir = any("docs" in f.parts for f in files)
    score = (40 if has_readme else 0) + min(40, has_docstrings * 4) + (20 if has_docs_dir else 0)
    return min(100, score)

def dim_standards(texts, files):
    score = 100
    for f in files:
        if f.suffix == ".py":
            t = f.read_text(errors="ignore")
            if not t.strip().endswith("\n"): score -= 5
            if re.search(r"\t", t): score -= 10   # tabs instead of spaces
    has_env = any(".env" in f.name for f in files)
    return max(0, score)

DIMS = [("code_review", dim_code_review, 0.15), ("security", dim_security, 0.15),
        ("performance", dim_performance, 0.10), ("accessibility", dim_accessibility, 0.08),
        ("ui", dim_ui, 0.08), ("testing", dim_testing, 0.12), ("linting", dim_linting, 0.12),
        ("documentation", dim_documentation, 0.10), ("standards", dim_standards, 0.10)]

def validate(target, name=None, threshold=70):
    init_db()
    files = _files(target)
    texts = _text(files)
    results = {}
    for dim, fn, w in DIMS:
        try:
            results[dim] = fn(texts, files)
        except Exception as e:
            results[dim] = 50
    composite = round(sum(results[d] * w for d, _, w in DIMS), 1)
    gate = "pass" if composite >= threshold else "fail"
    c = _conn()
    cur = c.execute("INSERT INTO reports (target, composite, gate, dims, created_at) VALUES (?,?,?,?,?)",
                    (name or str(target), composite, gate, json.dumps(results), _now()))
    rid = cur.lastrowid
    c.commit(); c.close()
    return {"ok": True, "report_id": rid, "target": name or str(target),
            "composite": composite, "gate": gate, "threshold": threshold, "dims": results,
            "files": len(files)}

def history(limit=10):
    init_db()
    c = _conn()
    rows = c.execute("SELECT id, target, composite, gate, created_at FROM reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "reports": [dict(r) for r in rows]}

def report(report_id):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    c.close()
    return dict(row) if row else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", nargs="+", metavar="PATH")
    ap.add_argument("--threshold", type=int, default=70)
    ap.add_argument("--history", action="store_true")
    args = ap.parse_args()
    if args.run:
        print(json.dumps(validate(args.run[0], name=args.run[1] if len(args.run) > 1 else None,
                                  threshold=args.threshold), indent=2)); return
    if args.history:
        for r in history()["reports"]:
            print(f"  [{r['id']}] {r['target'][:30]:32s} {r['composite']:6.1f} {r['gate']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
