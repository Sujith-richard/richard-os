#!/usr/bin/env python3
"""Richard OS — Skill Layer: a separate skills registry every model and
every department can access [17]. Aggregates 04-skills/, SOPs, persona
specialist jobs, resource packages, and book-to-skill outputs into one
searchable catalog (Composio-style: SKILL.md + supporting assets) [17]."""
import sqlite3, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "06-data" / "skills_library.db"

def _conn():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, category TEXT, source TEXT, description TEXT,
        owner_agent TEXT, department TEXT, status TEXT, path TEXT)""")
    return c

def _scan_dir(directory, source, category):
    """Index every skill.md AND standalone .md file in a directory tree."""
    out = []
    if not directory.exists():
        return out
    for skill_md in sorted(directory.rglob("skill.md")):
        name = skill_md.parent.name
        desc = ""
        try:
            txt = skill_md.read_text(errors="ignore")
            for line in txt.splitlines():
                if line.lower().startswith("## ") and len(line) > 4:
                    desc = line[3:].strip()
                    break
        except Exception:
            pass
        out.append({"name": name, "category": category, "source": source,
                    "description": desc[:120], "path": str(skill_md.relative_to(ROOT))})
    # also index standalone .md files (e.g., sops/email-triage.md)
    for md in sorted(directory.rglob("*.md")):
        if md.name == "skill.md":
            continue
        out.append({"name": md.stem, "category": category, "source": source,
                    "description": md.read_text(errors="ignore")[:120].splitlines()[0][:120],
                    "path": str(md.relative_to(ROOT))})
    return out

def _persona_jobs():
    """Pull specialist JOBS from persona_agents.py into the library."""
    out = []
    pa = ROOT / "scripts" / "persona_agents.py"
    if pa.exists():
        txt = pa.read_text(errors="ignore")
        for m in re.finditer(r'"([a-z0-9-]+)":\s*"([^"]{10,})"', txt):
            out.append({"name": m.group(1), "category": "Persona Specialist",
                        "source": "persona-agents", "description": m.group(2)[:120],
                        "path": "scripts/persona_agents.py"})
    return out

def build():
    c = _conn()
    c.execute("DELETE FROM skills")
    entries = []
    entries += _scan_dir(ROOT / "04-skills", "internal", "Skill")
    entries += _scan_dir(ROOT / "04-skills" / "sops", "sop", "Department SOP")
    entries += _scan_dir(ROOT / "04-skills", "book-to-skill", "User Skill")
    entries += _persona_jobs()
    try:
        conn = sqlite3.connect(ROOT / "06-data" / "resource_packages.db")
        conn.row_factory = sqlite3.Row
        pkgs = [dict(r) for r in conn.execute("SELECT name, category, capabilities FROM packages").fetchall()]
        conn.close()
        for p in pkgs:
            entries.append({"name": p["name"], "category": "Resource Package",
                            "source": "repo-ingest", "description": (p["capabilities"] or "")[:120],
                            "path": f"vendor/{p['name']}"})
    except Exception:
        pass
    seen = set()
    for e in entries:
        if e["name"] in seen:
            continue
        seen.add(e["name"])
        c.execute("INSERT INTO skills (name, category, source, description, owner_agent, department, status, path) VALUES (?,?,?,?,?,?, 'available', ?)",
                  (e["name"], e["category"], e["source"], e["description"],
                   _owner(e["name"]), _department(e["category"]), e["path"]))
    c.commit(); c.close()
    return len(seen)

def _owner(name):
    try:
        cfg = yaml.safe_load((ROOT / "01-root-spine" / "company.yaml").read_text())
        for aid, a in (cfg.get("agents") or {}).items():
            if name in (a.get("role") or "").lower() or name in aid:
                return aid
    except Exception:
        pass
    return "orchestrator"

def _department(category):
    dep = {"Skill": "General", "Department SOP": "All Departments", "User Skill": "General",
           "Persona Specialist": "Persona Teams", "Resource Package": "All Departments"}
    return dep.get(category, "General")

def list_skills(filters=None):
    c = _conn(); c.row_factory = sqlite3.Row
    sql = "SELECT * FROM skills"
    args = []
    if filters and filters.get("department"):
        sql += " WHERE department LIKE ?"; args.append("%" + filters["department"] + "%")
    sql += " ORDER BY category, name"
    rows = [dict(r) for r in c.execute(sql, args).fetchall()]
    c.close(); return rows

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1 and sys.argv[1] == "rebuild":
        print(json.dumps({"skills_indexed": build()}, indent=2))
    else:
        print(json.dumps(list_skills(), indent=2)[:2000])
