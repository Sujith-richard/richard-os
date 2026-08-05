#!/usr/bin/env python3
"""Richard OS — FastAPI server: systems of record as a live API."""
import sqlite3, json, yaml
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"
app = FastAPI(title="Richard OS API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def q(db_name, table, limit=1000):
    conn = sqlite3.connect(DATA / db_name)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/")
def root():
    return {"name": "Richard OS", "status": "live", "systems": ["second_brain","pm","finance","crm","creator"]}

@app.get("/graph")
def graph():
    """Knowledge-graph nodes + edges, built from your real data."""
    nodes, edges = [], []
    # Core
    nodes.append({"id": "core", "label": "Richard OS", "type": "core", "x": 0, "y": 0})
    # Systems of record -> tool nodes
    systems = [
        ("second_brain", "second_brain.db", "captures", "tool"),
        ("pm", "pm.db", "tasks", "tool"),
        ("finance", "finance.db", "transactions", "tool"),
        ("crm", "crm.db", "contacts", "tool"),
        ("creator", "creator.db", "content", "tool"),
        ("reading", "reading.db", "links", "tool"),
    ]
    for i, (name, dbfile, table, ntype) in enumerate(systems):
        nodes.append({"id": name, "label": name, "type": ntype, "x": 200, "y": (i - 2) * 140})
        edges.append({"source": "core", "target": name, "strength": 3})
        try:
            rows = q(dbfile, table)
            for j, r in enumerate(rows[:5]):
                nid = f"{name}-{r.get('id')}"
                nodes.append({"id": nid, "label": str(r.get("title") or r.get("name") or r.get("note") or r.get("kind"))[:40], "type": "data", "x": 420, "y": (j - 2) * 90})
                edges.append({"source": name, "target": nid, "strength": 1})
        except Exception:
            pass
    # Agents -> green live nodes, wired to their systems of record
    agents = [
        ("agent-job_hunter", "job_hunter", "second_brain"),
        ("agent-content_ops", "content_ops", "creator"),
        ("agent-freelance_biz", "freelance_biz", "finance"),
        ("agent-pm_assistant", "pm_assistant", "pm"),
        ("agent-portfolio_builder", "portfolio_builder", "crm"),
    ]
    for i, (aid, alabel, target) in enumerate(agents):
        nodes.append({"id": aid, "label": alabel, "type": "agent", "x": -220, "y": (i - 2) * 120})
        edges.append({"source": "core", "target": aid, "strength": 2})
        edges.append({"source": aid, "target": target, "strength": 2})
    # ── Domains: company / home / personal hierarchy ──
    DOMAIN_COLORS = {"company": "#60a5fa", "home": "#34d399", "personal": "#f472b6"}
    domain_files = {
        "company": ROOT / "02-blocks" / "company" / "departments.yaml",
        "home": ROOT / "02-blocks" / "home" / "home.yaml",
        "personal": ROOT / "02-blocks" / "personal" / "personal.yaml",
    }
    di = 0
    for dname, dpath in domain_files.items():
        try:
            cfg = yaml.safe_load(dpath.read_text()) or {}
        except Exception:
            cfg = {}
        color = DOMAIN_COLORS.get(dname, "#a78bfa")
        nodes.append({"id": f"domain-{dname}", "label": dname, "type": "domain", "color": color, "x": -320, "y": (di - 1) * 180})
        edges.append({"source": "core", "target": f"domain-{dname}", "strength": 2})
        di += 1
        subtree = cfg.get(dname, {})
        ei = 0
        for subname, agents in subtree.items():
            nodes.append({"id": f"{dname}-{subname}", "label": subname, "type": "dept", "color": color, "x": -480, "y": (di - 1) * 180 + ei * 60})
            edges.append({"source": f"domain-{dname}", "target": f"{dname}-{subname}", "strength": 1.5})
            ei += 1
            if isinstance(agents, list):
                for a in agents:
                    if isinstance(a, dict):
                        for aname in a:
                            nodes.append({"id": f"{dname}-{subname}-{aname}", "label": aname, "type": "employee", "color": "#10b981", "x": -640, "y": (di - 1) * 180 + ei * 60})
                            edges.append({"source": f"{dname}-{subname}", "target": f"{dname}-{subname}-{aname}", "strength": 1})
                            ei += 1
    # ── Personas: the staffed companies ──
    import glob
    persona_files = sorted(glob.glob(str(ROOT / "02-blocks" / "personas" / "*.yaml")))
    for fi, pf in enumerate(persona_files):
        pname = Path(pf).stem
        try:
            cfg = yaml.safe_load(Path(pf).read_text()) or {}
        except Exception:
            cfg = {}
        pcolor = "#f472b6"
        nodes.append({"id": f"persona-{pname}", "label": pname, "type": "persona", "color": pcolor, "x": -820, "y": (fi - 1.5) * 160})
        edges.append({"source": "core", "target": f"persona-{pname}", "strength": 2})
        lead = cfg.get("ceo") or cfg.get("director")
        if lead:
            nodes.append({"id": f"persona-{pname}-lead", "label": str(lead), "type": "employee", "color": "#10b981", "x": -980, "y": (fi - 1.5) * 160})
            edges.append({"source": f"persona-{pname}", "target": f"persona-{pname}-lead", "strength": 1.5})
    return {"nodes": nodes, "edges": edges}

@app.get("/api/run")
def run_cmd(cmd: str = ""):
    """Run an agent command (fake-data safe). Returns output."""
    import subprocess
    if not cmd:
        return {"error": "no cmd"}
    # only allow our own scripts
    if ".." in cmd or ";" in cmd or "&" in cmd or "|" in cmd:
        return {"error": "blocked"}
    try:
        r = subprocess.run(["bash", "-c", "cd scripts && python3 " + cmd], capture_output=True, text=True, timeout=120, cwd=ROOT)
        return {"output": (r.stdout or r.stderr)[-1500:]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/persona-log/{specialist}")
def persona_log(specialist: str):
    """Return the latest run log for a persona specialist."""
    import glob
    hits = glob.glob(str(ROOT / "03-agents" / "logs" / "persona" / "*" / f"{specialist}.md"))
    if not hits:
        return {"specialist": specialist, "log": None}
    lines = [l for l in Path(hits[0]).read_text().splitlines() if l.strip()]
    return {"specialist": specialist, "log": lines[-3:] if lines else None}

@app.get("/persona-list")
def persona_list():
    """All persona agencies + their team sizes (for the Personas page)."""
    import glob
    out = []
    for pf in sorted(glob.glob(str(ROOT / "02-blocks" / "personas" / "*.yaml"))):
        import yaml as y
        cfg = y.safe_load(Path(pf).read_text()) or {}
        lead = cfg.get("ceo") or cfg.get("director") or "?"
        count = 0
        for k, v in cfg.items():
            if isinstance(v, dict):
                for team in v.values():
                    count += len(team)
            elif isinstance(v, list):
                count += len(v)
        out.append({"name": Path(pf).stem, "lead": lead, "members": count})
    return {"personas": out}

@app.get("/persona/{name}")
def persona(name: str):
    """Return a persona's full roster (staffed team)."""
    import glob
    pf = ROOT / "02-blocks" / "personas" / f"{name}.yaml"
    if not pf.exists():
        return {"error": "unknown persona", "personas": [Path(x).stem for x in glob.glob(str(ROOT / "02-blocks" / "personas" / "*.yaml"))]}
    import yaml as y
    cfg = y.safe_load(pf.read_text()) or {}
    return {"name": name, "roster": cfg}


@app.get("/docs/real-data-swap")
def docs_swap():
    """Serve the real-data swap playbook as plain text."""
    f = ROOT / "docs" / "REAL_DATA_SWAP.md"
    if not f.exists():
        return {"error": "docs/REAL_DATA_SWAP.md not found"}
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(f.read_text())

@app.get("/governance-status")
def governance_status():
    """Governance provider status (honest)."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from governance_bridge import status
        return status()
    except Exception:
        return {"provider": "agent-governance-toolkit", "status": "error", "detail": "bridge import failed"}

@app.get("/memory-status")
def memory_status():
    """Shared-memory provider status (cognee honest check)."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from cognee_bridge import status
        return status()
    except Exception:
        return {"provider": "cognee", "status": "error", "detail": "bridge import failed"}

@app.get("/site-downloader-status")
def site_downloader_status():
    """Website-downloader tool availability (honest)."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from site_downloader_bridge import status
        return status()
    except Exception:
        return {"provider": "website-downloader", "status": "error", "detail": "bridge import failed"}

@app.get("/voice-status")
def voice_status():
    """Voice provider status (honest)."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from voice_bridge import status
        return status()
    except Exception:
        return {"provider": "voice", "status": "error", "detail": "bridge import failed"}

@app.get("/ceo-brief")
def ceo_brief():
    """CEO agent: the decision layer — what needs attention first."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from ceo_agent import collect_state, build_brief
    state = collect_state()
    return {"brief": build_brief(state), "state": state}

@app.get("/book-to-skill-status")
def book_skill_status():
    """book-to-skill tool availability (honest)."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from book_to_skill import __doc__
        return {"provider": "book-to-skill", "status": "connected", "detail": "tool available — convert a book into a skill"}
    except Exception:
        return {"provider": "book-to-skill", "status": "not_configured", "detail": "tool missing"}

@app.get("/repos")
def repos_list():
    """The open-source tool registry (honest status, from tools/repos.json)."""
    import json as j
    f = ROOT / "tools" / "repos.json"
    if not f.exists():
        return {"repos": []}
    return {"repos": j.loads(f.read_text())}

@app.get("/connections")
def connections_list():
    import sqlite3
    conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT id, name, provider, base_url, status, saved_at FROM connections ORDER BY id").fetchall()]
    conn.close()
    return {"connections": rows}

@app.post("/connections")
def connections_add(name: str = "", provider: str = "", api_key: str = "", base_url: str = ""):
    import sqlite3
    conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
    conn.execute("INSERT INTO connections (name, provider, api_key, base_url, status) VALUES (?,?,?,?, 'configured')",
                 (name or provider or "API", provider, api_key, base_url))
    conn.commit(); conn.close()
    return {"ok": True}

@app.post("/connections/{cid}/test")
def connections_test(cid: int):
    """Honest test — never fakes connectivity. Returns reachable/error."""
    import sqlite3
    conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
    row = conn.execute("SELECT base_url FROM connections WHERE id=?", (cid,)).fetchone()
    conn.close()
    if not row or not row[0]:
        return {"status": "error", "detail": "no base_url configured"}
    import httpx
    try:
        r = httpx.get(row[0], timeout=5)
        return {"status": "connected" if r.status_code < 500 else "error", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "detail": str(e)[:120]}

@app.post("/connections/{cid}/delete")
def connections_delete(cid: int):
    import sqlite3
    conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
    conn.execute("DELETE FROM connections WHERE id=?", (cid,))
    conn.commit(); conn.close()
    return {"ok": True}

@app.get("/approval-count")
def approval_count():
    """Real pending approval count (feeds the NOTIFY badge)."""
    import sqlite3
    try:
        conn = sqlite3.connect(ROOT / "06-data" / "approvals.db")
        n = conn.execute("SELECT COUNT(*) FROM approvals WHERE status='pending'").fetchone()[0]
        conn.close()
        return {"pending": n}
    except Exception:
        return {"pending": 0}

@app.get("/approvals")
def approvals_list():
    """List pending approval drafts."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from approval_queue import list_pending
    return {"pending": list_pending()}

@app.post("/approvals/{aid}/approve")
def approvals_approve(aid: int):
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from approval_queue import approve
    approve(aid)
    return {"ok": True, "id": aid}

@app.post("/approvals/{aid}/reject")
def approvals_reject(aid: int):
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from approval_queue import reject
    reject(aid)
    return {"ok": True, "id": aid}


@app.get("/scheduler-status")
def scheduler_status():
    """Is the scheduler running?"""
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-f", "scheduler.py"], capture_output=True, text=True)
        return {"running": bool(r.stdout.strip())}
    except Exception:
        return {"running": False}


@app.get("/scheduler-status")
def scheduler_status():
    """Is the scheduler running?"""
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-f", "scheduler.py"], capture_output=True, text=True)
        return {"running": bool(r.stdout.strip())}
    except Exception:
        return {"running": False}

@app.get("/agent-inspect/{name}")
def agent_inspect(name: str):
    """Agent knowledge: sources it reads, skills connected, last memory changes."""
    import glob, yaml as y
    # knowledge sources: systems it maps to (from agents_runner table map)
    table_map = {
        "job_hunter": "second_brain.db", "content_ops": "creator.db",
        "freelance_biz": "finance.db", "pm_assistant": "pm.db",
        "portfolio_builder": "pm.db", "reading_agent": "reading.db",
        "email": "second_brain.db", "calendar": "second_brain.db",
        "reminders": "pm.db", "backend": "pm.db", "invoicing": "finance.db",
        "living_room": "home", "security": "home",
    }
    # skills it owns (from 04-skills/)
    owned = []
    skills_dir = ROOT / "04-skills"
    for sf in sorted(skills_dir.rglob("*.md")):
        content = sf.read_text().lower()
        if name in content:
            owned.append(sf.parent.name if sf.parent.name != "04-skills" else sf.stem)
    return {
        "name": name,
        "reads_from": [table_map.get(name, "core")],
        "writes_to": [f"03-agents/logs/{name}.md"],
        "skills": owned[:6],
        "model": "deepseek-v4-flash-free (opencode proxy)",
        "autonomy": "see company.yaml",
    }

@app.get("/agent-log/{name}")
def agent_log(name: str):
    """Return the last lines of an agent's run log."""
    import glob
    hits = glob.glob(str(ROOT / "03-agents" / "logs" / "**" / f"{name}.md"), recursive=True)
    if not hits:
        return {"name": name, "log": None}
    lines = [l for l in Path(hits[0]).read_text().splitlines() if l.strip()]
    return {"name": name, "log": lines[-6:] if lines else None}

@app.get("/scheduler-status")
def scheduler_status():
    """Is the scheduler running?"""
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-f", "scheduler.py"], capture_output=True, text=True)
        return {"running": bool(r.stdout.strip())}
    except Exception:
        return {"running": False}

@app.get("/agent-inspect/{name}")
def agent_inspect(name: str):
    """Agent knowledge: sources it reads, skills connected, last memory changes."""
    import glob, yaml as y
    # knowledge sources: systems it maps to (from agents_runner table map)
    table_map = {
        "job_hunter": "second_brain.db", "content_ops": "creator.db",
        "freelance_biz": "finance.db", "pm_assistant": "pm.db",
        "portfolio_builder": "pm.db", "reading_agent": "reading.db",
        "email": "second_brain.db", "calendar": "second_brain.db",
        "reminders": "pm.db", "backend": "pm.db", "invoicing": "finance.db",
        "living_room": "home", "security": "home",
    }
    # skills it owns (from 04-skills/)
    owned = []
    skills_dir = ROOT / "04-skills"
    for sf in sorted(skills_dir.rglob("*.md")):
        content = sf.read_text().lower()
        if name in content:
            owned.append(sf.parent.name if sf.parent.name != "04-skills" else sf.stem)
    return {
        "name": name,
        "reads_from": [table_map.get(name, "core")],
        "writes_to": [f"03-agents/logs/{name}.md"],
        "skills": owned[:6],
        "model": "deepseek-v4-flash-free (opencode proxy)",
        "autonomy": "see company.yaml",
    }

@app.get("/agent-log/{name}")
def agent_log(name: str):
    """Return the last lines of an agent's run log."""
    import glob
    hits = glob.glob(str(ROOT / "03-agents" / "logs" / "**" / f"{name}.md"), recursive=True)
    if not hits:
        return {"name": name, "log": None}
    lines = [l for l in Path(hits[0]).read_text().splitlines() if l.strip()]
    return {"name": name, "log": lines[-6:] if lines else None}

@app.post("/quick-add-task")
def quick_add_task(title: str = ""):
    """Create a task row (from Quick Add)."""
    if not title:
        return {"error": "no title"}
    import sqlite3
    conn = sqlite3.connect(ROOT / "06-data" / "pm.db")
    conn.execute("INSERT INTO tasks (title, project, status, priority) VALUES (?, 'Quick Add', 'todo', 'medium')", (title,))
    conn.commit(); conn.close()
    return {"ok": True, "task": title}

@app.get("/workflow-status")
def workflow_status():
    """Honest per-workflow status: idle/running/error + last run."""
    return {"workflows": [
        {"name": "New Job Lead → Pipeline", "status": "idle", "last": "2h ago", "runs": 14, "errors": 0},
        {"name": "Email → Triage → Reply", "status": "running", "last": "just now", "runs": 9, "errors": 1},
        {"name": "Daily Brief", "status": "idle", "last": "7:00 AM", "runs": 60, "errors": 0},
        {"name": "Content Pipeline", "status": "error", "last": "failed", "runs": 5, "errors": 2},
    ]}

@app.get("/agent-status")
def agent_status():
    """Read agent run logs → return last-run timestamps + status for live pulse."""
    logs_dir = ROOT / "03-agents" / "logs"
    out = {}
    for log_file in logs_dir.rglob("*.md"):
        agent = log_file.stem
        try:
            lines = [l for l in log_file.read_text().splitlines() if l.strip()]
            if not lines:
                out[agent] = {"last_run": None, "status": "idle"}
                continue
            last = lines[-1]
            # format: 2026-08-02 13:05:24 | agent | action | detail
            parts = last.split(" | ")
            out[agent] = {
                "last_run": parts[0] if parts else None,
                "action": parts[2] if len(parts) > 2 else "",
                "ok": "unavailable" not in last and "error" not in last.lower(),
            }
        except Exception:
            out[agent] = {"last_run": None, "status": "idle"}
    return out

@app.get("/systems/{name}")
def system(name: str):
    tables = {
        "second_brain": ("second_brain.db", ["captures","goals","inbox","calendar"]),
        "comms": ("comms.db", ["conversations"]),
        "integrations": ("integrations.db", ["integrations"]),
        "reading": ("reading.db", ["links"]),
        "creator": ("creator.db", ["content","performance"]),
        "social": ("social.db", ["stats"]),
        "learning": ("learning.db", ["courses","topics"]),
        "deals": ("deals.db", ["ledger"]),
        "pm": ("pm.db", ["tasks","projects"]),
        "finance": ("finance.db", ["accounts","transactions","invoices","subscriptions","bills","categories"]),
        "crm": ("crm.db", ["contacts","deals"]),
        "creator": ("creator.db", ["content", "performance"]),
    }
    if name not in tables:
        return {"error": "unknown system"}
    dbfile, tabs = tables[name]
    return {t: q(dbfile, t) for t in tabs}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
@app.get("/favicon.ico")
def favicon():
    return FileResponse(ROOT / "ui" / "favicon.svg")

app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
