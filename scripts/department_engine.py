#!/usr/bin/env python3
"""
scripts/department_engine.py - #14 Department Layer
Reads 02-blocks/company/departments-spec.yaml -> scaffolds the full 16-item
spine per department under 02-blocks/company/<name>/ + persists manifest to
06-data/departments.db. Fake-data-first; content is starter/template.
"""
import json, sqlite3, pathlib, datetime, argparse, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "02-blocks" / "company" / "departments-spec.yaml"
DEPT_ROOT = ROOT / "02-blocks" / "company"
DB_PATH = ROOT / "06-data" / "departments.db"

# The 16-item spine per the FounderOS PDF (#14)
SPINE = [
    "knowledge",   # dept knowledge base / docs
    "skills",      # composio-style skill registry
    "agents",      # agent configs (name -> autonomy/model/tools)
    "prompts",     # reusable system prompts
    "templates",   # file/code templates
    "standards",   # coding/dept standards
    "rules",       # decision rules
    "workflows",   # runnable workflow definitions
    "docs",        # dept documentation
    "git",         # git conventions / branch rules
    "mcp",         # MCP tool wiring for the dept
    "memory",      # shared memory notes
    "datasets",    # dataset samples
    "training",    # training samples for fine-tuning
    "project-structures",  # project blueprints
    "examples",    # worked examples
    "evaluation",  # eval criteria
    "output-formats",  # deliverable output formats
    "plugins",     # dept plugin registry
    "tools",       # dept tool registry
]

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
    CREATE TABLE IF NOT EXISTS departments (
        name TEXT PRIMARY KEY, title TEXT, icon TEXT, lead TEXT, stacks TEXT,
        specialists TEXT, skills TEXT, autonomy INTEGER, status TEXT DEFAULT 'scaffolded',
        files INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT);
    CREATE TABLE IF NOT EXISTS dept_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dept TEXT, path TEXT, kind TEXT);
    """)
    c.commit(); c.close()

def load_spec():
    import yaml
    with open(SPEC) as f:
        d = yaml.safe_load(f)
    return d.get("departments", {})

def _write(rel, content):
    p = DEPT_ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return str(p.relative_to(DEPT_ROOT))

def build_content(name, dep):
    """Return {relpath: content} for every spine item of a department."""
    lead = dep.get("lead", name + "-lead")
    title = dep.get("title", name.title())
    icon = dep.get("icon", "📁")
    stacks = ", ".join(dep.get("stacks", []))
    specs = ", ".join(dep.get("specialists", []))
    skills = ", ".join(dep.get("skills", []))
    rules = dep.get("decision_rules", [])
    workflows = dep.get("workflows", [])
    datasets = dep.get("datasets", [])
    auto = dep.get("autonomy", 3)
    out = {}

    out[f"{name}/README.md"] = f"# {icon} {title} (Department Layer)\n\nLead: **{lead}** · Autonomy: **{auto}**\n\nStacks: {stacks}\nSpecialists: {specs}\nSkills: {skills}\n"

    out[f"{name}/knowledge/{name}-overview.md"] = f"# {title} — Knowledge Base\n\nWhat this department owns, its systems of record, and how work flows through it.\n\n- Core responsibilities\n- Key systems & tools ({stacks})\n- Common pitfalls\n- Handoff points to other departments\n"

    out[f"{name}/skills/{name}-skills.yaml"] = f"# {title} skills (Composio-style registry)\nskills:\n" + "".join(f"  - name: {s}\n    dept: {name}\n    desc: \"{s.replace('-',' ')} capability\"\n" for s in dep.get("skills", []))

    out[f"{name}/agents/agents.yaml"] = f"# {title} agent roster\ndept: {name}\nlead: {lead}\nautonomy: {auto}\nagents:\n" + "".join(f"  {a}:\n    role: \"{a.replace('-',' ')}\"\n    model: deepseek-v4-flash-free\n    autonomy: {auto}\n" for a in dep.get("specialists", []))

    out[f"{name}/prompts/{name}-system.md"] = f"# {title} — Department System Prompt\n\nYou are the {title} department of Richard OS. Route requests to your specialists, follow the decision rules, and escalate human-judgment items as decisions (not to-dos).\n\nStacks: {stacks}\nAutonomy: {auto}\n"

    out[f"{name}/templates/{name}-scaffold.md"] = f"# {title} — Starter Template\n\nUse this template when generating {name} deliverables. Fill the placeholders, keep the structure.\n"

    out[f"{name}/standards/standards.md"] = f"# {title} — Standards\n\n- Code is reviewed before merge\n- Tests ship with every feature\n- Secrets live in vault, never in code\n- Docs updated in the same PR\n"

    out[f"{name}/rules/rules.md"] = "# Decision Rules\n" + "".join(f"- {r}\n" for r in rules)

    out[f"{name}/workflows/workflows.yaml"] = f"# {title} — Workflows\nworkflows:\n" + "".join(f"  - name: \"{w.split(':')[0].strip()}\"\n    steps: \"{w.split(':',1)[1].strip() if ':' in w else w}\"\n" for w in workflows)

    out[f"{name}/docs/{name}-docs.md"] = f"# {title} — Documentation\n\nHow to work inside this department: onboarding notes, runbooks, and references.\n"

    out[f"{name}/git/git-conventions.md"] = f"# {title} — Git Conventions\n\n- Branch: `{name}/<feature>`\n- Commits: conventional (feat/fix/chore/docs)\n- PR: description + screenshots + test evidence\n"

    out[f"{name}/mcp/mcp-tools.yaml"] = f"# {title} — MCP wiring\nmcp:\n  dept: {name}\n  tools: []\n  notes: \"Connect dept-specific tools here\"\n"

    out[f"{name}/memory/shared-memory.md"] = f"# {title} — Shared Memory\n\nNotes other departments and agents read. Keep it current.\n"

    out[f"{name}/datasets/sample.json"] = json.dumps({"dept": name, "samples": datasets, "note": "starter dataset"}, indent=2)

    out[f"{name}/training/training-samples.json"] = json.dumps({"dept": name, "examples": [], "note": "fine-tuning samples collected over time"}, indent=2)

    return out

def scaffold_subdepartments(dept_name, sub_depts):
    """Scaffold each sub-department folder with the standardized template."""
    created = []
    for sub, data in (sub_depts or {}).items():
        base = f"{dept_name}/sub-departments/{sub}"
        files = {
            f"{base}/README.md": f"# {sub.title()} (Sub-Department)\n\nPart of {dept_name}. Standardized sub-dept template.\n",
            f"{base}/knowledge/knowledge.md": "# Knowledge\n" + "\n".join(f"- {k}" for k in data.get("knowledge", [])),
            f"{base}/skills/skills.md": "# Skills\n" + "\n".join(f"- {s}" for s in data.get("skills", [])),
            f"{base}/agents/agents.yaml": "# Agents\n" + "\n".join(f"  {a}: {{role: '{a.replace('-',' ')}'}}" for a in data.get("agents", [])),
            f"{base}/project-structures/structures.md": "# Project Structures\n" + "\n".join(f"- {ps}" for ps in data.get("project_structures", [])),
            f"{base}/templates/template.md": f"# {sub.title()} Template\nStandardized scaffold.\n",
            f"{base}/rules/rules.md": "# Rules\n- follow department standards\n",
            f"{base}/standards/standards.md": "# Standards\n- reviewed before merge\n",
            f"{base}/prompts/system.md": f"# {sub.title()} System Prompt\nYou are the {sub} sub-department.\n",
            f"{base}/workflows/workflows.yaml": "# Workflows\nworkflows: []\n",
            f"{base}/git/git.md": f"# Git\n- branch: `{sub}/<feature>`\n",
            f"{base}/mcp/mcp.md": "# MCP\ntools: []\n",
            f"{base}/docs/docs.md": f"# {sub.title()} Docs\n",
            f"{base}/memory/memory.md": "# Shared Memory\n",
            f"{base}/datasets/dataset.json": '{"samples": []}',
            f"{base}/training/training.json": '{"examples": []}',
            f"{base}/examples/examples.md": "# Examples\n",
            f"{base}/evaluation/eval.md": "# Evaluation\ncriteria: []\n",
            f"{base}/output-formats/formats.md": "# Output Formats\n",
            f"{base}/plugins/plugins.md": "# Plugins\n",
            f"{base}/tools/tools.md": "# Tools\n",
        }
        for rel, content in files.items():
            _write(rel, content)
        created.append({"sub": sub, "files": len(files)})
    return created

def generate(name=None):
    init_db()
    deps = load_spec()
    targets = [name] if name else list(deps.keys())
    c = _conn()
    results = []
    for dname in targets:
        if dname not in deps:
            results.append({"name": dname, "ok": False, "error": "unknown dept"})
            continue
        dep = deps[dname]
        files = build_content(dname, dep)
        n = 0
        for rel, content in files.items():
            _write(rel, content); n += 1
        sub_created = scaffold_subdepartments(dname, dep.get("sub_departments"))
        n += sum(sc["files"] for sc in sub_created)
        c.execute("""INSERT OR REPLACE INTO departments
            (name,title,icon,lead,stacks,specialists,skills,autonomy,status,files,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?, 'scaffolded', ?, ?, ?)""",
            (dname, dep.get("title"), dep.get("icon"), dep.get("lead"),
             json.dumps(dep.get("stacks", [])), json.dumps(dep.get("specialists", [])),
             json.dumps(dep.get("skills", [])), dep.get("autonomy", 3),
             n, _now(), _now()))
        c.execute("DELETE FROM dept_files WHERE dept=?", (dname,))
        for rel in files:
            c.execute("INSERT INTO dept_files (dept, path, kind) VALUES (?,?,?)",
                      (dname, rel, rel.split("/")[1] if "/" in rel else "root"))
        c.commit()
        results.append({"name": dname, "ok": True, "files": n})
    c.close()
    return {"ok": True, "generated": results}

def list_depts():
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM departments ORDER BY name").fetchall()
    c.close()
    return {"ok": True, "departments": [dict(r) for r in rows]}

def dept_detail(name):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM departments WHERE name=?", (name,)).fetchone()
    files = c.execute("SELECT path, kind FROM dept_files WHERE dept=? ORDER BY path", (name,)).fetchall()
    c.close()
    if not row:
        return {"ok": False, "error": "not found"}
    return {"ok": True, "department": dict(row), "files": [dict(f) for f in files]}

def main():
    ap = argparse.ArgumentParser(description="Richard OS Department Layer (#14)")
    ap.add_argument("--generate", metavar="DEPT", nargs="?", const="__all__", help="scaffold all (or one) departments")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--detail", metavar="DEPT")
    args = ap.parse_args()
    if args.generate:
        name = None if args.generate == "__all__" else args.generate
        print(json.dumps(generate(name), indent=2)); return
    if args.list:
        d = list_depts()
        for x in d["departments"]:
            print(f"{x['icon']} {x['name']:10s} {x['status']:12s} {x['files']:4d} files  autonomy={x['autonomy']}")
        return
    if args.detail:
        print(json.dumps(dept_detail(args.detail), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()

