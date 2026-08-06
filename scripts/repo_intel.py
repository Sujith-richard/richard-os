#!/usr/bin/env python3
"""scripts/repo_intel.py — v4.0 Repository Intelligence (flagship).
Superset of repo_ingest: clone → README/docs → detect lang/framework/type →
extract skills/knowledge/workflows/templates/folder-structure/MCP/APIs →
persist → register → dept-available. Writes to the same resource_packages.db
so /resource-packages stays compatible, plus a searchable intel table.
"""
import re, sqlite3, subprocess, shutil, json, pathlib
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"
VENDOR = ROOT / "vendor"
INTEL_DIR = DATA / "repo_intel"

def _db():
    conn = sqlite3.connect(DATA / "resource_packages.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, url TEXT, category TEXT,
        types TEXT, departments TEXT, capabilities TEXT,
        status TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS repo_intel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, url TEXT, language TEXT, framework TEXT, repo_type TEXT,
        categories TEXT, skills TEXT, knowledge TEXT, workflows TEXT,
        templates TEXT, folder_structure TEXT, mcp TEXT, apis TEXT,
        dept_mapping TEXT, search_index TEXT, status TEXT, created_at TEXT)""")
    return conn

def _slug(url):
    return url.rstrip("/").split("/")[-1].replace(".git", "")

def _detect_language(root):
    ext = {}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix:
            ext[p.suffix] = ext.get(p.suffix, 0) + 1
    lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript/React",
                ".jsx": "JavaScript/React", ".go": "Go", ".rs": "Rust", ".java": "Java",
                ".cpp": "C++", ".c": "C", ".rb": "Ruby", ".php": "PHP", ".sh": "Shell",
                ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".html": "HTML", ".css": "CSS"}
    best = None; best_n = 0
    for extc, n in ext.items():
        lang = lang_map.get(extc)
        if lang and n > best_n:
            best_n = n; best = lang
    return best or "Unknown"

def _detect_framework(root):
    # package manifests
    if (root / "package.json").exists():
        try:
            d = json.loads((root / "package.json").read_text())
            deps = {**(d.get("dependencies") or {}), **(d.get("devDependencies") or {})}
            for fw in ["next", "vue", "react", "angular", "svelte", "express", "nest", "fastify"]:
                if any(fw in k for k in deps): return fw.capitalize()
        except Exception: pass
    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        txt = (root / "requirements.txt").read_text(errors="ignore") if (root / "requirements.txt").exists() else (root / "pyproject.toml").read_text(errors="ignore")
        for fw in ["django", "flask", "fastapi", "torch", "tensorflow", "langchain", "transformers"]:
            if fw in txt.lower(): return fw.capitalize()
    if (root / "go.mod").exists(): return "Go modules"
    if (root / "Cargo.toml").exists(): return "Rust/Cargo"
    return "None detected"

def _detect_type(root, knowledge, name):
    low = (knowledge + " " + name).lower()
    if any(k in low for k in ["skill", "claude skill", "agent skill"]): return "Skill Library"
    if any(k in low for k in ["tool", "utility", "cli", "blue team", "pentest", "security"]): return "Tool Collection"
    if (root / "workflows").exists() or (root / ".github/workflows").exists(): return "Workflow Library"
    if any(k in low for k in ["documentation", "awesome-", "curated", "list of"]): return "Knowledge / Documentation"
    if (root / "package.json").exists() or (root / "requirements.txt").exists(): return "Framework / Application"
    return "Repository"

def _extract_skills(root, repo_type):
    skills = []
    # markdown skill files / skill folders
    for pat in ["skills", "skills/*", "claude-skills", "src/skills"]:
        d = root / pat
        if d.exists():
            for f in list(d.glob("*.md"))[:8] if d.is_dir() else []:
                skills.append(f.stem)
    # from README headings that look like skills/capabilities
    readme = root / "README.md"
    if readme.exists():
        for line in readme.read_text(errors="ignore").splitlines():
            m = re.match(r"^[-*]\s*(?:\[)?([A-Za-z][A-Za-z0-9 -]{2,40})(?:\])?$", line.strip())
            if m and not any(x in m.group(1).lower() for x in ["badge", "star", "fork", "install", "license", "contribut", "screenshot"]):
                skills.append(m.group(1).strip())
            if len(skills) >= 12: break
    return list(dict.fromkeys(skills))

def _extract_mcp(root):
    mcp = []
    for pat in [".mcp.json", "mcp.json", "mcp/", "MCP/", ".mcp/"]:
        p = root / pat
        if p.exists():
            if p.is_dir():
                mcp += [str(x.relative_to(root)) for x in list(p.rglob("*"))[:8]]
            else:
                try:
                    d = json.loads(p.read_text())
                    mcp += list(d.keys())[:8] if isinstance(d, dict) else []
                except Exception:
                    mcp.append(str(p))
    return mcp

def _extract_apis(root, language):
    apis = []
    for pat in ["routes", "api", "controllers", "endpoints"]:
        d = root / pat
        if d.is_dir():
            for f in list(d.rglob("*.py"))[:6] + list(d.rglob("*.js"))[:6] + list(d.rglob("*.ts"))[:6]:
                txt = f.read_text(errors="ignore")
                for m in re.findall(r'@(?:app|router)\.(?:get|post|put|delete)\("([^"]+)"', txt):
                    apis.append(m)
    return list(dict.fromkeys(apis))[:20]

def _workflows(root):
    wfs = []
    for pat in ["workflows", ".github/workflows"]:
        d = root / pat
        if d.is_dir():
            for f in list(d.rglob("*.yml")) + list(d.rglob("*.yaml")) + list(d.rglob("*.json")):
                wfs.append(f.name)
    return wfs[:10]

def _templates(root):
    tmpl = []
    for pat in ["templates", "scaffolds", "blueprints"]:
        d = root / pat
        if d.is_dir():
            tmpl += [str(x.relative_to(root)) for x in list(d.rglob("*"))[:8]]
    return tmpl

def _folder_structure(root, limit=30):
    out = []
    for i, p in enumerate(root.rglob("*")):
        if i >= limit: break
        if ".git" in p.parts: continue
        out.append(str(p.relative_to(root)))
    return out

def _dept_mapping(repo_type, categories, name):
    low = (categories + " " + name).lower()
    if "cyber" in low or "secur" in low: return "cyber"
    if "skill" in low or "ai" in low: return "ai"
    if "web" in low or "frontend" in low or "backend" in low: return "web"
    if "devops" in low or "cloud" in low: return "cloud"
    if "data" in low: return "data"
    return "general"

def ingest(url):
    """Full pipeline: clone → deep extract → persist → register."""
    name = _slug(url)
    target = VENDOR / name
    if not target.exists():
        r = subprocess.run(["git", "clone", "--depth", "1", url, str(target)],
                           capture_output=True, text=True, timeout=240)
        if r.returncode != 0:
            return {"error": "clone failed", "detail": r.stderr[:200]}
    readme = target / "README.md"
    knowledge = readme.read_text(errors="ignore")[:6000] if readme.exists() else ""
    language = _detect_language(target)
    framework = _detect_framework(target)
    repo_type = _detect_type(target, knowledge, name)
    skills = _extract_skills(target, repo_type)
    mcp = _extract_mcp(target)
    apis = _extract_apis(target, language)
    workflows = _workflows(target)
    templates = _templates(target)
    structure = _folder_structure(target)
    categories = _categorize(knowledge, name)
    dept = _dept_mapping(repo_type, categories, name)
    search = " ".join([name, repo_type, categories] + skills[:10] + workflows).lower()
    INTEL_DIR.mkdir(exist_ok=True)
    (INTEL_DIR / f"{name}.json").write_text(json.dumps({
        "name": name, "url": url, "language": language, "framework": framework,
        "repo_type": repo_type, "categories": categories, "dept": dept,
        "skills": skills[:12], "workflows": workflows, "templates": templates,
        "mcp": mcp, "apis": apis[:12], "folder_structure": structure,
    }, indent=2))
    conn = _db()
    conn.execute("""INSERT OR REPLACE INTO repo_intel
        (name, url, language, framework, repo_type, categories, skills, knowledge, workflows,
         templates, folder_structure, mcp, apis, dept_mapping, search_index, status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'intel-ready', ?)""",
        (name, url, language, framework, repo_type, categories,
         json.dumps(skills[:12]), knowledge[:3000], json.dumps(workflows),
         json.dumps(templates), json.dumps(structure), json.dumps(mcp), json.dumps(apis[:12]),
         dept, search, datetime.now().isoformat(timespec="seconds")))
    conn.execute("INSERT OR REPLACE INTO packages (name, url, category, types, departments, capabilities, status) VALUES (?,?,?,?,?,?, 'intel-ready')",
                 (name, url, categories, repo_type, dept, "|".join(skills[:8])))
    conn.commit(); conn.close()
    return {"name": name, "repo_type": repo_type, "language": language, "framework": framework,
            "categories": categories, "dept": dept, "skills": len(skills), "workflows": len(workflows),
            "mcp": len(mcp), "apis": len(apis), "templates": len(templates),
            "status": "intel-ready — available to departments"}

def _categorize(text, name):
    low = (text + " " + name).lower()
    for cat, kw in [("Cyber Security", ["secur", "vulnerab", "pentest", "blue team", "red team"]),
                    ("DevOps", ["deploy", "ci", "docker", "kubernetes", "devops"]),
                    ("Web Development", ["web", "frontend", "react", "javascript", "css"]),
                    ("AI / Data", ["ai", "ml", "model", "data", "neural", "skill"]),
                    ("Finance", ["finance", "bank", "payment", "stock", "trade"]),
                    ("Voice / Media", ["voice", "audio", "tts", "asr", "video"]),
                    ("CAD / Design", ["cad", "3d", "design", "freecad", "mesh"])]:
        if any(k in low for k in kw): return cat
    return "General / Uncategorized"

def list_intel():
    conn = _db(); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, name, url, language, framework, repo_type, categories, dept_mapping, status FROM repo_intel ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def intel_detail(name):
    conn = _db(); conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM repo_intel WHERE name=?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", metavar="URL")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--detail", metavar="NAME")
    args = ap.parse_args()
    if args.ingest:
        print(json.dumps(ingest(args.ingest), indent=2)); return
    if args.list:
        for r in list_intel():
            print(f"  {r['name']:28s} {r['repo_type']:22s} {r['language']:14s} dept={r['dept_mapping']}")
        return
    if args.detail:
        print(json.dumps(intel_detail(args.detail), indent=2, default=str)); return
    ap.print_help()

if __name__ == "__main__":
    main()


