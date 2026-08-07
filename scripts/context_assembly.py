#!/usr/bin/env python3
"""
scripts/context_assembly.py - Phase F1 Context Assembly Engine
Packs all 14 resource types into ONE context envelope before any model call:
department knowledge, skills, user memory, long-term memory, knowledge graph,
git repo intelligence, plugins, MCP servers, project structures, templates,
standards, rules, previous projects, workflows.
"""
import json, sqlite3, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCKS = ROOT / "02-blocks" / "company"
SKILLS = ROOT / "04-skills"
DATA = ROOT / "06-data"

def _gather(queries):
    return "\n".join(f"- {q}" for q in queries[:8])

def _memory(mtype, limit=6):
    try:
        c = sqlite3.connect(DATA / "memory.db"); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT content FROM memories WHERE mtype=? ORDER BY id DESC LIMIT ?", (mtype, limit)).fetchall()
        c.close()
        return _gather([r["content"] for r in rows])
    except Exception:
        return "(none)"

def _dept_knowledge(dept="web", sub=None):
    try:
        if sub:
            p = BLOCKS / dept / "sub-departments" / sub / "knowledge" / "knowledge.md"
        else:
            p = BLOCKS / dept / "knowledge" / f"{dept}-overview.md"
        if p.exists():
            return p.read_text(errors="ignore")[:800]
    except Exception:
        pass
    return "(none)"

def _skills(limit=5):
    try:
        files = sorted(SKILLS.glob("*.md"))[:limit]
        return "\n".join(f"- {f.stem}" for f in files) or "(none)"
    except Exception:
        return "(none)"

def _repos(limit=4):
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from repo_intel import list_intel
        return _gather([f"{r['name']} ({r['repo_type']})" for r in list_intel()[:limit]])
    except Exception:
        return "(none)"

def _plugins(limit=4):
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from plugin_store import status
        return _gather([p["name"] for p in status()["installed"][:limit]]) or "(none installed)"
    except Exception:
        return "(none)"

def _mcp():
    try:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import mcp_tools
        st = mcp_tools.status() or {}
        return _gather([f"{k}:{v}" for k, v in st.items()][:6])
    except Exception:
        return "(none)"

def _workflows(limit=4):
    try:
        c = sqlite3.connect(DATA / "workflows.db"); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT title FROM workflows LIMIT ?", (limit,)).fetchall()
        c.close()
        return _gather([r["title"] for r in rows])
    except Exception:
        return "(none)"

def _projects(limit=4):
    try:
        c = sqlite3.connect(DATA / "project_engine.db"); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT title FROM projects ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        c.close()
        return _gather([r["title"] for r in rows])
    except Exception:
        return "(none)"

def _standards(dept="web"):
    try:
        p = BLOCKS / dept / "standards" / "standards.md"
        return p.read_text(errors="ignore")[:500] if p.exists() else "(none)"
    except Exception:
        return "(none)"

def _rules(dept="web"):
    try:
        p = BLOCKS / dept / "rules" / "rules.md"
        return p.read_text(errors="ignore")[:500] if p.exists() else "(none)"
    except Exception:
        return "(none)"

def _templates(dept="web"):
    try:
        p = BLOCKS / dept / "templates" / f"{dept}-scaffold.md"
        return p.read_text(errors="ignore")[:400] if p.exists() else "(none)"
    except Exception:
        return "(none)"

def _structures(dept="web"):
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from department_engine import load_spec
        spec = load_spec()
        sub = spec.get(dept, {}).get("sub_departments", {})
        return _gather(list(sub.keys()))
    except Exception:
        return "(none)"

def assemble(request, dept="web", sub=None, include_all=True):
    """Build the full context envelope (markdown block for the model)."""
    parts = [
        "=== RICHARD OS CONTEXT ENVELOPE ===",
        f"--- Department: {dept}" + (f"/{sub}" if sub else "") + " ---",
        f"Knowledge:\n{_dept_knowledge(dept, sub)}",
        f"Skills:\n{_skills()}",
        f"User Memory:\n{_memory('user')}",
        f"Long-Term Memory:\n{_memory('long-term')}",
        f"Knowledge Graph (repos):\n{_repos()}",
        f"Plugins:\n{_plugins()}",
        f"MCP Servers:\n{_mcp()}",
        f"Project Structures (sub-depts):\n{_structures(dept)}",
        f"Templates:\n{_templates(dept)}",
        f"Standards:\n{_standards(dept)}",
        f"Rules:\n{_rules(dept)}",
        f"Previous Projects:\n{_projects()}",
        f"Workflows:\n{_workflows()}",
        f"=== USER REQUEST ===\n{request}",
    ]
    return "\n\n".join(parts)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="Build a fitness app")
    ap.add_argument("--dept", default="web")
    ap.add_argument("--sub", default=None)
    args = ap.parse_args()
    print(assemble(args.request, args.dept, args.sub))

if __name__ == "__main__":
    main()
