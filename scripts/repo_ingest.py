#!/usr/bin/env python3
"""Richard OS — Repository Ingestion Pipeline (the Agentic-OS flow [17]).
Instead of: Git Repo → Clone → Done
It becomes: Analyze → Extract → Build Knowledge → Register → Available to Departments.
"""
import re, sqlite3, subprocess, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"
VENDOR = ROOT / "vendor"

def _db():
    conn = sqlite3.connect(DATA / "resource_packages.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, url TEXT, category TEXT,
        types TEXT, departments TEXT, capabilities TEXT,
        status TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return conn

def _slug(url):
    return url.rstrip("/").split("/")[-1].replace(".git", "")

def analyze(url):
    """The full pipeline: clone → analyze → extract → build → register."""
    name = _slug(url)
    target = VENDOR / name
    # ── 1. Clone (or reuse existing) ──
    if not target.exists():
        r = subprocess.run(["git", "clone", url, str(target)], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            return {"error": "clone failed", "detail": r.stderr[:200]}
    # ── 2. Extract knowledge (README + docs) ──
    knowledge = ""
    readme = target / "README.md"
    if readme.exists():
        knowledge = readme.read_text(errors="ignore")[:4000]
    docs = [str(p.relative_to(target)) for p in target.rglob("docs/*.md")][:5]
    # ── 3. Extract tools / categories / capabilities ──
    tools = [p.name for p in (target / "tools").glob("*")] if (target / "tools").exists() else []
    if not tools:
        tools = [p.name for p in (target / "bin").glob("*")] if (target / "bin").exists() else []
    categories = _categorize(knowledge, name)
    capabilities = _capabilities(knowledge)
    workflows = _workflows(target)
    types = []
    if knowledge: types.append("Knowledge")
    if tools: types.append("Tool Library")
    if workflows: types.append("Workflow Library")
    types += ["Best Practices", "Documentation"]
    # ── 4. Build internal knowledge file ──
    kb = ROOT / "06-data" / "knowledge" / f"{name}.md"
    kb.parent.mkdir(exist_ok=True)
    kb.write_text(f"# {name}\n\nURL: {url}\nCategory: {categories}\nCapabilities: {', '.join(capabilities[:6])}\n\n## Summary\n{knowledge[:1500]}")
    # ── 5. Register the resource package ──
    conn = _db()
    conn.execute("INSERT OR REPLACE INTO packages (name, url, category, types, departments, capabilities, status) VALUES (?,?,?,?,?,?, 'registered')",
                 (name, url, categories, "|".join(types), _departments(categories), "|".join(capabilities[:8])))
    conn.commit(); conn.close()
    return {
        "name": name, "category": categories, "types": types,
        "capabilities": capabilities[:6], "workflows": len(workflows),
        "status": "registered — available to departments",
    }

def _categorize(text, name):
    low = (text + " " + name).lower()
    for cat, kw in [("Cyber Security", ["secur", "vulnerab", "pentest", "blue team", "red team"]),
                    ("DevOps", ["deploy", "ci", "docker", "kubernetes", "devops"]),
                    ("Web Development", ["web", "frontend", "react", "javascript", "css"]),
                    ("AI / Data", ["ai", "ml", "model", "data", "neural"]),
                    ("Finance", ["finance", "bank", "payment", "stock", "trade"]),
                    ("Voice / Media", ["voice", "audio", "tts", "asr", "video"]),
                    ("CAD / Design", ["cad", "3d", "design", "freecad", "mesh"])]:
        if any(k in low for k in kw):
            return cat
    return "General / Uncategorized"

def _capabilities(text):
    # pull bullet points from README as capabilities
    return [l.strip().lstrip("-* ")[:60] for l in text.splitlines() if l.strip().startswith(("-", "*"))][:8] or ["Analyze, extract, and register repository knowledge"]

def _workflows(target):
    return [p.name for p in target.rglob("*.yml") if "workflow" in p.name.lower()][:3]

def _departments(category):
    base = ["AI Research", "DevOps", "QA"]
    if category == "Cyber Security": return "Cyber Security|DevOps|QA|AI Research"
    if category == "CAD / Design": return "Web Development|AI Research|QA"
    return "|".join(base)

def list_packages():
    conn = _db(); conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM packages ORDER BY id DESC").fetchall()]
    conn.close(); return rows

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        print(json.dumps(analyze(sys.argv[1]), indent=2))
    else:
        print(json.dumps(list_packages(), indent=2))
