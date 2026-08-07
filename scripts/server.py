#!/usr/bin/env python3
"""Richard OS — FastAPI server: systems of record as a live API."""
import sqlite3, json, yaml
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
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
    """Richard Core v2 — the neural brain: tree = who owns what,
    neural graph = who talks to whom [17]. Core services connect in from
    outside; the AI model layer lives inside the brain [17]."""
    nodes, edges = [], []
    def N(nid, label, ntype, x, y, color=None):
        nodes.append({"id": nid, "label": label, "type": ntype, "x": x, "y": y, "color": color})
        return nid
    def E(src, tgt, strength=1):
        edges.append({"source": src, "target": tgt, "strength": strength})

    # ── RICHARD CORE (the brain center) ──
    core = N("core", "Richard Core", "core", 0, 0, "#ff8a3d")
    brain_knowledge = [
        ("shared-memory", "Shared Memory"), ("knowledge-graph", "Knowledge Graph"),
        ("learning-engine", "Learning Engine"), ("neural-network", "Neural Network"),
        ("context-memory", "Context Memory"), ("long-term-memory", "Long Term Memory"),
        ("experience-memory", "Experience Memory"),
    ]
    for nid, label in brain_knowledge:
        N(nid, label, "knowledge", -60, 0, "#e8e8e8")

    # ── AI MODEL LAYER — INSIDE the brain [17] ──
    cloud = [("openai","OpenAI"),("anthropic","Anthropic"),("google","Google"),("deepseek","DeepSeek"),
             ("xai","xAI"),("mistral","Mistral"),("qwen","Qwen"),("future-models","Future Models 100+")]
    local = [("coding-model","Coding"),("vision-model","Vision"),("reasoning-model","Reasoning"),
             ("planner-model","Planner"),("creative-model","Creative"),("research-model","Research"),
             ("security-model","Security"),("dept-models","Department Models")]
    N("ai-model-layer", "AI Model Layer", "dept", -180, 0, "#29D7F6")
    N("cloud-models", "Cloud Models", "dept", -180, -80, "#29D7F6")
    N("local-models", "Local Models", "dept", -180, 90, "#29D7F6")
    E(core, "ai-model-layer"); E("ai-model-layer","cloud-models"); E("ai-model-layer","local-models")
    for i,(nid,label) in enumerate(cloud):
        N(nid, label, "model", -320, -140 + i*36, "#29D7F6"); E("cloud-models", nid)
    for i,(nid,label) in enumerate(local):
        N(nid, label, "model", -320, 40 + i*36, "#29D7F6"); E("local-models", nid)

    # ── CORE SERVICES — connected to brain from OUTSIDE [17] ──
    services = [
        ("executive-ai","Executive AI"),("planner-ai","Planner AI"),("task-manager","Task Manager"),
        ("workflow-engine","Workflow Engine"),("model-orchestrator","Model Orchestrator"),
        ("decision-engine","Decision Engine"),("reasoning-engine","Reasoning Engine"),
        ("automation-engine","Automation Engine"),("context-engine","Context Engine"),
        ("memory-engine","Memory Engine"),("knowledge-engine","Knowledge Engine"),
        ("prompt-engine","Prompt Engine"),("quality-checker","Quality Checker"),
        ("neural-comm","Neural Comm Engine"),("event-bus","Event Bus"),
    ]
    N("core-services", "Core Services (outside)", "dept", 180, 0, "#B58CFF")
    E(core, "core-services")
    for i,(nid,label) in enumerate(services):
        N(nid, label, "service", 320, -150 + i*22, "#B58CFF")
        E("core-services", nid)          # services reach IN to the brain [17]
    # neural collaboration (who talks to whom) [17]
    E("executive-ai","planner-ai"); E("planner-ai","task-manager"); E("task-manager","workflow-engine")
    E("model-orchestrator","ai-model-layer",2); E("neural-comm","knowledge-graph",2)
    E("memory-engine","long-term-memory",2); E("knowledge-engine","knowledge-graph",2)

    # ── CONVERSATION LAYER ──
    convs = [("chat","Chat"),("voice","Voice"),("vision","Vision"),("doc-chat","Document Chat"),
             ("terminal","Terminal"),("api","API"),("automation-trigger","Automation Trigger"),
             ("mobile-app","Mobile App"),("desktop-app","Desktop App"),("web-app","Web App"),("wearables","Wearables")]
    N("conversation", "Conversation Layer", "dept", 0, -180, "#F472B6")
    for i,(nid,label) in enumerate(convs):
        N(nid, label, "conv", -200 + i*40, -260, "#F472B6"); E("conversation", nid)
    E(core, "conversation")

    # ── PERSONAL ASSISTANT ──
    pa = [("daily","Daily"),("calendar","Calendar"),("email","Email"),("notes","Notes"),("tasks","Tasks"),
          ("finance","Finance"),("health","Health"),("travel","Travel"),("shopping","Shopping"),("smart-home","Smart Home")]
    N("personal-assistant", "Personal Assistant", "dept", 0, 180, "#34D399")
    for i,(nid,label) in enumerate(pa):
        N(nid, label, "assistant", -180 + i*40, 260, "#34D399"); E("personal-assistant", nid)
    E(core, "personal-assistant")
    for nid,label in [("lights","Lights"),("sensors","Sensors"),("cctv","CCTV"),("ac","AC"),("door-lock","Door Lock"),("ha-auto","Automation")]:
        N("ha-"+nid, label, "device", -320, 360, "#34D399"); E("smart-home", "ha-"+nid)

    # ── CAPABILITY LAYER ──
    caps = [("skills","Skills"),("tools-mcp","Tools / MCP"),("knowledge","Knowledge"),("departments-cap","Departments")]
    N("capability", "Capability Layer", "dept", 380, 180, "#10B981")
    for i,(nid,label) in enumerate(caps):
        N(nid, label, "cap", 520, 140 + i*40, "#10B981"); E("capability", nid)
    E(core, "capability")
    N("skill-layer", "Skill Layer (every model + dept)", "dept", 520, 40, "#10B981")
    E("capability", "skill-layer", 2)
    for nid,label in [("claude-skills","Claude Skills"),("internal-skills","Internal"),("dept-skills","Department"),
                      ("user-skills","User"),("community-skills","Community")]:
        N(nid, label, "skill", 660, 60 + i*30, "#10B981"); E("skills", nid)

    # ── RESOURCE INTELLIGENCE ──
    regs = [("mcp-registry","MCP Registry"),("api-registry","API Registry"),("tool-registry","Tool Registry"),
            ("plugin-registry","Plugin Registry"),("knowledge-registry","Knowledge Registry")]
    N("resource-intel", "Resource Intelligence", "dept", -380, 180, "#D5C44B")
    for i,(nid,label) in enumerate(regs):
        N(nid, label, "resource", -560, 120 + i*34, "#D5C44B"); E("resource-intel", nid)
    E(core, "resource-intel")
    gh = [("security-repos","Security (BlueTeam-Tools, OWASP)"),("ai-repos","AI"),("frameworks","Frameworks"),
          ("templates","Templates"),("sdks","SDKs"),("awesome","Awesome Lists"),
          ("claude-skill-repos","Claude Skills Repo"),("prompt-libs","Prompt Libraries")]
    N("github-intel", "GitHub Repo Intelligence", "dept", -560, -160, "#D5C44B")
    for i,(nid,label) in enumerate(gh):
        N(nid, label, "repo", -720, -220 + i*32, "#D5C44B"); E("github-intel", nid)
    E("resource-intel","github-intel")

    # ── DEPARTMENT LAYER ──
    # v3.19: departments come from the Department Layer engine (8 real depts)
    import sys as _ds, pathlib as _dp
    _ds.path.insert(0, str(_dp.Path(__file__).resolve().parent))
    from department_engine import load_spec
    spec = load_spec()
    depts = [(n, d.get("title", n)) for n, d in spec.items()] if spec else \
        [("web-dev","Web Development"),("ai-eng","AI Engineering"),("data-eng","Data Engineering"),
         ("cyber-security","Cyber Security"),("cloud","Cloud"),("robotics","Robotics"),
         ("finance-dept","Finance"),("hr","HR")]
    N("departments", "Department Layer", "dept", 0, 380, "#60A5FA")
    for i,(nid,label) in enumerate(depts):
        N(nid, label, "dept", -360 + (i%7)*120, 460 + (i//7)*60, "#60A5FA"); E("departments", nid)
    E(core, "departments")
    web_parent = next((nid for nid, _ in depts if nid in ("web", "web-dev")), "web-dev")
    for nid,label in [("frontend","Frontend"),("backend","Backend"),("database","Database"),("api-sub","API"),
                      ("auth","Authentication"),("devops","DevOps"),("testing","Testing"),("security-sub","Security"),("docs","Documentation")]:
        N("web-"+nid, label, "subdept", -360, 560, "#60A5FA"); E(web_parent, "web-"+nid)
    # neural collaboration across departments [17]
    E("web-frontend","web-backend",2); E("web-backend","web-database",2); E("web-backend","web-security-sub",2)
    E("web-backend","web-devops",2); E("web-database","web-api-sub",2); E("web-testing","web-frontend",2)

    # ── PROJECT GENERATION + CONTINUOUS LEARNING ──
    N("project-gen", "Project Generation Engine", "engine", 380, -160, "#F26CB8")
    for nid,label in [("req-analysis","Requirement Analysis"),("dept-select","Department Selection"),
                      ("skill-select","Skill Selection"),("tool-select","Tool Selection"),
                      ("knowledge-retr","Knowledge Retrieval"),("structure-select","Structure Selection"),
                      ("agent-assign","Agent Assignment"),("file-gen","File Generation"),
                      ("code-gen","Code Generation"),("testing-gen","Testing"),("security-review","Security Review"),
                      ("docs-gen","Documentation"),("quality-review","Quality Review"),
                      ("packaging","Packaging"),("delivery","Delivery")]:
        N("pg-"+nid, label, "engine", 560, -280 + i*26, "#F26CB8"); E("project-gen", "pg-"+nid)
    E(core, "project-gen")
    N("continuous-learning", "Continuous Learning", "engine", 560, 260, "#F26CB8")
    for nid,label in [("store-conv","Store Conversation"),("store-knowledge","Store Knowledge"),
                      ("store-skills","Store Skills"),("store-workflow","Store Workflow"),
                      ("store-project","Store Project"),("gen-dataset","Generate Dataset"),
                      ("finetune","Fine Tune Local Models"),("improve-core","Improve Richard Core")]:
        N("cl-"+nid, label, "engine", 740, 200 + i*30, "#F26CB8"); E("continuous-learning", "cl-"+nid)
    E(core, "continuous-learning")

    # ── KEEP existing systems of record + agents (nothing breaks) ──
    systems = [("second_brain","second_brain.db","captures"),("pm","pm.db","tasks"),
               ("finance","finance.db","transactions"),("crm","crm.db","contacts"),
               ("creator","creator.db","content"),("reading","reading.db","links")]
    for i,(name, dbfile, table) in enumerate(systems):
        nodes.append({"id": name, "label": name, "type": "tool", "x": 200, "y": 380 + i*40})
        edges.append({"source": core, "target": name, "strength": 3})
        try:
            rows = q(dbfile, table)
            for j, r in enumerate(rows[:5]):
                nid = f"{name}-{r.get('id')}"
                nodes.append({"id": nid, "label": str(r.get("title") or r.get("name") or r.get("note") or r.get("kind"))[:40], "type": "data", "x": 420, "y": 380 + i*40 + j*30})
                edges.append({"source": name, "target": nid, "strength": 1})
        except Exception:
            pass
    agents = [("agent-job_hunter","job_hunter","second_brain"),("agent-content_ops","content_ops","creator"),
              ("agent-freelance_biz","freelance_biz","finance"),("agent-pm_assistant","pm_assistant","pm"),
              ("agent-portfolio_builder","portfolio_builder","crm")]
    for i,(aid, alabel, target) in enumerate(agents):
        nodes.append({"id": aid, "label": alabel, "type": "agent", "x": 560, "y": 380 + i*40})
        edges.append({"source": core, "target": aid, "strength": 2})
        edges.append({"source": aid, "target": target, "strength": 2})

    return {"nodes": nodes, "edges": edges, "links": edges}

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
    """Shared-memory provider status (cognee honest check + real-key slot)."""
    import sys, sqlite3
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from cognee_bridge import status
        out = status()
        spine = ROOT / "01-root-spine"
        out["docs_indexed"] = len(list(spine.glob("*.md"))) if spine.exists() else 0
        try:
            c = sqlite3.connect(ROOT / "06-data" / "connections.db")
            llm = c.execute("SELECT COUNT(*) FROM connections WHERE upper(provider) IN ('LLM','OPENAI')").fetchone()[0]
            c.close()
            out["real_key_slot"] = bool(llm)
        except Exception:
            out["real_key_slot"] = False
        return out
    except Exception:
        return {"provider": "cognee", "status": "error", "detail": "bridge import failed"}
@app.get("/cloud-status")
def cloud_status():
    """Cloud utilities (OmniCloud, 9drive, WebToApp) honest status."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from cloud_bridge import status
        return status()
    except Exception:
        return {"provider": "cloud-utilities", "status": "error"}

@app.get("/codegraph-status")
def codegraph_status():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from codegraph_bridge import status
        return status()
    except Exception:
        return {"provider": "codegraph-rust", "status": "error", "detail": "bridge import failed"}

@app.get("/freecad-status")
def freecad_status():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from freecad_bridge import status
        return status()
    except Exception:
        return {"provider": "freecad-mcp", "status": "error", "detail": "bridge import failed"}

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
    """Open-source tool registry. Serves LIVE GitHub data when github is live, else seeded repos.json."""
    import json as j
    try:
        from integrations import resolve_source
        live = resolve_source("github")
    except Exception:
        live = None
    if live:
        try:
            d = j.loads(live.read_text())
            return {"repos": d.get("repos", []), "source": "live-github"}
        except Exception:
            pass
    f = ROOT / "tools" / "repos.json"
    if not f.exists():
        return {"repos": []}
    return {"repos": j.loads(f.read_text()), "source": "seeded"}

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def unhandled_exception(request, exc):
    return JSONResponse(status_code=500, content={
        "reply": f"(server error: {type(exc).__name__}: {exc}) — honest",
        "owner": "core",
    })


def make_report(topic):
    """Build a markdown report from live OS data and save it as a downloadable file."""
    import sqlite3, datetime, re
    topic = topic.lower()
    lines = [f"# Richard OS Report — {topic.title()}", f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    if "company" in topic or any(c in topic for c in ["acme", "techstart", "finnovate", "cloudly", "shopwave"]):
        c = sqlite3.connect(ROOT / "06-data" / "crm.db")
        c.row_factory = sqlite3.Row
        deals = [dict(r) for r in c.execute("SELECT title, company, value, stage FROM deals").fetchall()]
        c.close()
        target = topic.replace("report on", "").replace("company report", "").replace("company", "").strip()
        hits = [d for d in deals if not target or target in d["company"].lower()]
        lines.append("## Deals")
        for d in hits:
            lines.append(f"- **{d['title']}** · {d['company']} · ${d['value']:,} · {d['stage']}")
        lines.append("")
        lines.append(f"**Total pipeline: ${sum(d['value'] for d in hits):,}**")

    elif "finance" in topic or "income" in topic or "money" in topic or "revenue" in topic:
        c = sqlite3.connect(ROOT / "06-data" / "finance.db")
        c.row_factory = sqlite3.Row
        txs = [dict(r) for r in c.execute("SELECT kind, amount, note, date FROM transactions").fetchall()]
        c.close()
        inc = sum(t["amount"] for t in txs if t["kind"] == "income")
        exp = sum(t["amount"] for t in txs if t["kind"] == "expense")
        lines += ["## Finance", f"- Income: **${inc:,.2f}**", f"- Expenses: **${exp:,.2f}**", f"- Net: **${inc-exp:,.2f}**", "", "### Transactions"]
        for t in txs[:15]:
            lines.append(f"- {t['date']} · {t['kind']} · ${t['amount']:.2f} · {t['note']}")

    elif "task" in topic or "todo" in topic or "priority" in topic:
        c = sqlite3.connect(ROOT / "06-data" / "pm.db")
        c.row_factory = sqlite3.Row
        tasks = [dict(r) for r in c.execute("SELECT title, project, status, priority FROM tasks").fetchall()]
        c.close()
        lines += ["## Tasks", f"- Open: {sum(1 for t in tasks if t['status']!='done')}", f"- High priority: {sum(1 for t in tasks if t['priority']=='high' and t['status']!='done')}", ""]
        for t in tasks[:12]:
            lines.append(f"- [{t['status']}] **{t['title']}** · {t['project']} · {t['priority']}")

    elif "pipeline" in topic or "funnel" in topic or "deals" in topic or "lead" in topic:
        c = sqlite3.connect(ROOT / "06-data" / "crm.db")
        c.row_factory = sqlite3.Row
        deals = [dict(r) for r in c.execute("SELECT title, company, value, stage FROM deals").fetchall()]
        c.close()
        lines += ["## Pipeline", f"- Deals: {len(deals)} · Total: **${sum(d['value'] for d in deals):,}**", ""]
        for st in ["prospect", "proposal", "needs-follow-up", "negotiation", "contract-pending", "won", "lost"]:
            grp = [d for d in deals if d["stage"] == st]
            if grp:
                lines.append(f"### {st.title()} ({len(grp)})")
                for d in grp:
                    lines.append(f"- {d['title']} · ${d['value']:,}")

    else:
        c = sqlite3.connect(ROOT / "06-data" / "pm.db")
        open_t = c.execute("SELECT COUNT(*) FROM tasks WHERE status!='done'").fetchone()[0]
        c.close()
        c = sqlite3.connect(ROOT / "06-data" / "approvals.db")
        pend = c.execute("SELECT COUNT(*) FROM approvals WHERE status='pending'").fetchone()[0]
        c.close()
        c = sqlite3.connect(ROOT / "06-data" / "crm.db")
        deals_n = c.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
        c.close()
        c = sqlite3.connect(ROOT / "06-data" / "finance.db")
        inc = c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE kind='income'").fetchone()[0]
        c.close()
        lines += ["## OS Snapshot", f"- Open tasks: {open_t}", f"- Pending approvals: {pend}", f"- Deals: {deals_n}", f"- Income: ${round(inc):,}"]

    reports_dir = ROOT / "06-data" / "reports"
    reports_dir.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-") or "report"
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    md_name = f"{stamp}-{slug}.md"
    html_name = f"{stamp}-{slug}.html"
    md_text = "\n".join(lines)
    (reports_dir / md_name).write_text(md_text)

    # styled HTML twin
    def _esc(t):
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Richard OS Report</title>
<style>body{background:#0a0a0a;color:#e8e8e8;font-family:monospace;max-width:820px;margin:40px auto;padding:0 20px}
h1{color:#E9883A;text-transform:uppercase;letter-spacing:.06em}h2{color:#29D7F6;text-transform:uppercase;font-size:14px;margin-top:28px;border-bottom:1px solid #242424;padding-bottom:6px}
li{color:#909090;line-height:1.7}.total{color:#48D06A;font-weight:700}</style></head><body>
<h1>Richard OS Report</h1>
<div style="color:#555;font-size:12px">Generated: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
""" + "".join(
        ("<h2>" + _esc(l[3:]) + "</h2>" if l.startswith("## ") else
         "<h3 style='color:#B58CFF'>" + _esc(l[4:]) + "</h3>" if l.startswith("### ") else
         "<li>" + _esc(l[2:]) + "</li>" if l.startswith("- ") else
         ("<div class='total'>" + _esc(l) + "</div>" if l.startswith("**") else
          ("<p>" + _esc(l) + "</p>" if l else "<br>")))
        for l in md_text.splitlines()
    ) + "</body></html>"
    (reports_dir / html_name).write_text(html)
    return md_name, md_text, html_name


@app.get("/reports/zip")
def reports_zip():
    """Bundle all generated reports into one downloadable ZIP."""
    import zipfile, io
    reports_dir = ROOT / "06-data" / "reports"
    reports_dir.mkdir(exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(reports_dir.glob("*.md")):
            z.write(f, f.name)
    buf.seek(0)
    from fastapi.responses import Response
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=richard-reports.zip"},
    )


@app.post("/stt")
async def stt_upload(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file with openai-whisper (free, local).
    Honest: returns an error if whisper isn't installed."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from voice_bridge import stt
        tmp = ROOT / "06-data" / "tmp_input.wav"
        tmp.write_bytes(await file.read())
        return stt(str(tmp))
    except Exception as e:
        return {"error": str(e)[:150], "hint": "install openai-whisper or use browser Web Speech"}

@app.post("/chat")
def chat(msg: str = ""):
    """WhatsApp-style chat with the AI core: reads OS state, routes to an
    agent, replies in natural language (grounded in live data)."""
    import sys, json, sqlite3
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "tools"))
    if not msg.strip():
        return {"reply": "Say something — e.g. \"what's my morning brief?\" or \"run the agents\"."}

    # ── 1. Gather live OS state (grounding) ──
    state = {}
    try:
        c = sqlite3.connect(ROOT / "06-data" / "approvals.db")
        state["pending_approvals"] = c.execute("SELECT COUNT(*) FROM approvals WHERE status='pending'").fetchone()[0]
        c.close()
    except Exception:
        state["pending_approvals"] = 0
    try:
        c = sqlite3.connect(ROOT / "06-data" / "pm.db")
        state["open_tasks"] = c.execute("SELECT COUNT(*) FROM tasks WHERE status!='done'").fetchone()[0]
        state["high"] = c.execute("SELECT COUNT(*) FROM tasks WHERE status!='done' AND priority='high'").fetchone()[0]
        c.close()
    except Exception:
        state["open_tasks"] = 0; state["high"] = 0
    try:
        c = sqlite3.connect(ROOT / "06-data" / "crm.db")
        state["deals"] = c.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
        c.close()
    except Exception:
        state["deals"] = 0
    try:
        c = sqlite3.connect(ROOT / "06-data" / "finance.db")
        inc = c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE kind='income'").fetchone()[0]
        state["income"] = round(inc)
        c.close()
    except Exception:
        state["income"] = 0

    # ── 2. Route intent → which agent owns it ──
    from orchestrator import find_agent
    domain, agent = find_agent(msg, {})
    owner = agent or "orchestrator"
    route_hint = f"Suggested owner: {owner}"

    # ── 3. Action triggers (do real work when asked) ──
    action_note = ""
    low = msg.lower()
    # ── Skill Layer — every model + department can access [17] ──
    skill_note = ""
    if "skill" in low and any(k in low for k in ["what", "show", "list", "available", "use"]):
        import sys as _sl
        _sl.path.insert(0, str(ROOT / "scripts"))
        try:
            from skill_layer import list_skills, build
            build()
            sk = list_skills()
            if "use skill" in low:
                name = low.replace("use skill", "").strip().strip(".")
                hit = next((x for x in sk if x["name"] in name or name in x["name"]), None)
                skill_note = ("\n\n🔧 Skill **" + hit["name"] + "** (" + hit["category"] + ", owned by " + hit["owner_agent"] + ") — loaded for this task: " + hit["description"] + " [17]" if hit else "\n\nNo skill matched '" + name + "' — say \"what skills\" to see the library.")
            else:
                skill_note = "\n\n🧠 Skill Layer (every model + department can access) [17]:\n" + "\n".join("- " + x["name"] + " · " + x["category"] + " · " + x["owner_agent"] for x in sk[:20])
                if len(sk) > 20:
                    skill_note += "\n… and " + str(len(sk) - 20) + " more (ask 'use skill <name>')"
        except Exception as e:
            skill_note = "\n\n(Skill layer error: " + str(e)[:80] + " — honest)"

    # ── MCP tool dispatch (AI Core chat → real tools) ──
    mcp_note = ""
    try:
        import sys as _s
        _s.path.insert(0, str(ROOT / "tools"))
        from mcp_tools import route, status
        tool = route(msg)
        if tool:
            st = status(tool)
            mcp_note = (f"\n\n🧰 MCP tool matched: **{tool}** — " + st["status"])
            if st["status"] == "not_configured":
                mcp_note += " (install in vendor/ to run it — honest)"
    except Exception:
        mcp_note = ""

    if any(k in low for k in ["brief", "morning", "summary"]):
        from morning_brief import main as brief_main
        action_note = "Generated the morning brief for you below."
    if any(k in low for k in ["run agent", "run the agent", "execute"]):
        action_note = "Queued the relevant agent run — see the Agents page."

    # ── 4. Build the prompt with memory + state, call the LLM ──
    from agent_lib import call_llm, read_memory
    mem = read_memory()[:1500]
    prompt = (
        "You are the AI core of Richard OS. Reply in short, natural, friendly "
        "sentences like a helpful assistant (WhatsApp style, no markdown tables).\n"
        f"OS MEMORY:\n{mem}\n"
        f"LIVE STATE:\n{json.dumps(state)}\n"
        f"{route_hint}\n{action_note}\n"
        f"USER: {msg}"
    )
    reply = call_llm(prompt, "deepseek-v4-flash-free")
    # honest fallback if LLM unavailable
    if reply.startswith("[LLM"):
        reply = (
            f"Here's what the OS knows right now: {state['pending_approvals']} pending "
            f"approvals, {state['open_tasks']} open tasks ({state['high']} high-priority), "
            f"{state['deals']} deals, ~${state['income']} income. "
            f"[LLM offline — this is the honest live-state answer] {route_hint}"
        )
    # ── 5. Persist the conversation ──
    try:
        c = sqlite3.connect(ROOT / "06-data" / "chat.db")
        c.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, text TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP)")
        c.execute("INSERT INTO chat (role, text) VALUES ('user', ?)", (msg,))
        c.execute("INSERT INTO chat (role, text) VALUES ('ai', ?)", (reply,))
        c.commit(); c.close()
    except Exception:
        pass
    zip_url = None
    if "zip" in low or "all reports" in low or "download all" in low:
        zip_url = "/reports/zip"
        reply = reply + "\n\n📦 All reports — **download ZIP below**."
    report_url = None
    html_url = None
    if any(k in low for k in ["report", "download", "summary report", "report on"]):
        try:
            fname, content, html_name = make_report(msg)
            report_url = "/reports/" + fname
            html_url = "/reports/" + html_name
            reply = reply + "\n\n📄 Report ready — **download it below**."
        except Exception as e:
            report_url = None
            html_url = None
            reply = reply + f"\n\n(Report generation failed: {e})"
    reply = reply + skill_note
    return {"reply": reply, "owner": owner, "state": state, "report_url": report_url, "html_url": html_url, "zip_url": zip_url}

@app.get("/chat/history")
def chat_history():
    import sqlite3
    try:
        c = sqlite3.connect(ROOT / "06-data" / "chat.db")
        c.row_factory = sqlite3.Row
        rows = [dict(r) for r in c.execute("SELECT role, text, ts FROM chat ORDER BY id DESC LIMIT 50").fetchall()]
        c.close()
        return {"messages": rows[::-1]}
    except Exception:
        return {"messages": []}

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

@app.get("/skills-library")
def skills_library():
    """The Skill Layer — every model + department can access it [17]."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from skill_layer import list_skills, build
    build()  # refresh the catalog from disk
    dept = ""
    return {"skills": list_skills({"department": dept} or None), "count": len(list_skills())}

@app.get("/resource-packages")
def resource_packages():
    """Registered resource packages (the ingestion pipeline output) [17]."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from repo_ingest import list_packages
    return {"packages": list_packages()}

@app.post("/resource-packages/ingest")
def resource_ingest(url: str = ""):
    """Analyze a GitHub repo → register it as a resource package [17]."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from repo_ingest import analyze
    if not url:
        return {"error": "no url"}
    return analyze(url)

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
    """Real per-workflow status from the workflow engine DB."""
    try:
        import sys as _ws, pathlib as _wp
        _ws.path.insert(0, str(_wp.Path(__file__).resolve().parent))
        from workflow_engine import list_workflows
        d = list_workflows()
        return {"workflows": [{"name": w["title"], "status": w["status"], "last": w["last_run"] or "never",
                               "runs": w["runs"], "errors": w["errors"]} for w in d["workflows"]]}
    except Exception as e:
        return {"workflows": [], "error": str(e)}

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
from fastapi.staticfiles import StaticFiles
import os as _os
_os.makedirs(str(ROOT / "06-data" / "reports"), exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(ROOT / "06-data" / "reports")), name="reports")

# ===== #15 Project Generation Engine (v3.2) =====
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from project_engine import run_pipeline, init_db, _conn

@app.post("/api/v1/project/generate")
async def api_project_generate(payload: dict = None):
    payload = payload or {}
    brief = (payload.get("brief") or "").strip()
    if not brief:
        return {"ok": False, "error": "brief required"}
    try:
        r = run_pipeline(brief, client=payload.get("client", "self"))
        return {"ok": True, **r}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/v1/project/status/{pid}")
async def api_project_status(pid: str):
    init_db()
    c = _conn()
    row = c.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    learns = c.execute("SELECT lesson, count FROM learnings ORDER BY count DESC").fetchall()
    c.close()
    if not row:
        return {"ok": False, "error": "project not found"}
    return {"ok": True, "project": dict(row), "learnings": [dict(x) for x in learns]}

@app.get("/api/v1/project/list")
async def api_project_list():
    init_db()
    c = _conn()
    rows = c.execute("SELECT id,title,client,department,status,score,created_at FROM projects ORDER BY created_at DESC").fetchall()
    c.close()
    return {"ok": True, "projects": [dict(r) for r in rows]}

# ===== v3.4 Live Integrations Hub =====
import sys as _s2, pathlib as _p2
_s2.path.insert(0, str(_p2.Path(__file__).resolve().parent))
from integrations import (list_integrations, test_source, sync_source,
                          set_mode, save_source_config)

@app.get("/api/v1/integrations")
async def api_integrations_list():
    return list_integrations()

@app.post("/api/v1/integrations/{name}/test")
async def api_integrations_test(name: str):
    return test_source(name)

@app.post("/api/v1/integrations/{name}/sync")
async def api_integrations_sync(name: str):
    return sync_source(name)

@app.post("/api/v1/integrations/{name}/mode")
async def api_integrations_mode(name: str, payload: dict = None):
    payload = payload or {}
    return set_mode(name, payload.get("mode", "fake"))

@app.post("/api/v1/integrations/{name}/config")
async def api_integrations_config(name: str, payload: dict = None):
    payload = payload or {}
    return save_source_config(name, payload.get("fields", {}))

# ===== #14 Department Layer (v3.19) =====
import sys as _d1, pathlib as _d2
_d1.path.insert(0, str(_d2.Path(__file__).resolve().parent))
from department_engine import list_depts, dept_detail, generate as _dept_gen

@app.get("/api/v1/departments")
async def api_departments_list():
    return list_depts()

@app.get("/api/v1/departments/{name}")
async def api_departments_detail(name: str):
    return dept_detail(name)

@app.post("/api/v1/departments/generate")
async def api_departments_generate(payload: dict = None):
    payload = payload or {}
    name = payload.get("name")
    return _dept_gen(name)

@app.get("/api/v1/departments/{name}/file")
async def api_departments_file(name: str, path: str = ""):
    """Read a spine file: /api/v1/departments/web/file?path=skills/web-skills.yaml"""
    import os as _os
    safe = _os.path.normpath(path)
    if safe.startswith("..") or _os.path.isabs(safe):
        return {"ok": False, "error": "bad path"}
    root = _d2.Path(__file__).resolve().parent.parent / "02-blocks" / "company"
    f = root / name / safe
    if not f.exists() or not f.is_file():
        return {"ok": False, "error": "file not found"}
    ext = f.suffix.lower()
    content = f.read_text(errors="replace")
    return {"ok": True, "path": str(f.relative_to(root)), "ext": ext, "content": content}

# ===== #10 Planner AI + Workflow Engine (v3.20) =====
import sys as _w1, pathlib as _w2
_w1.path.insert(0, str(_w2.Path(__file__).resolve().parent))
from workflow_engine import list_workflows as _wf_list, workflow_detail as _wf_detail, \
    run_workflow as _wf_run, seed as _wf_seed
from planner import plan_from_goal

@app.get("/api/v1/workflows")
async def api_workflows_list():
    return _wf_list()

@app.get("/api/v1/workflows/{name}")
async def api_workflows_detail(name: str):
    return _wf_detail(name)

@app.post("/api/v1/workflows/plan")
async def api_workflows_plan(payload: dict = None):
    payload = payload or {}
    goal = (payload.get("goal") or "").strip()
    if not goal:
        return {"ok": False, "error": "goal required"}
    return {"ok": True, "plan": plan_from_goal(goal)}

@app.post("/api/v1/workflows/{name}/run")
async def api_workflows_run(name: str):
    return _wf_run(name)

@app.post("/api/v1/workflows/seed")
async def api_workflows_seed():
    return {"ok": True, "seeded": _wf_seed()}

# ===== #16 Continuous Learning (v3.21) =====
import sys as _l1, pathlib as _l2
_l1.path.insert(0, str(_l2.Path(__file__).resolve().parent))
from learning_engine import capture_all as _learn_capture, generate_dataset as _learn_ds, \
    fine_tune as _learn_ft, improve_core as _learn_improve, overview as _learn_ov

@app.get("/api/v1/learning/overview")
async def api_learning_overview():
    return _learn_ov()

@app.post("/api/v1/learning/capture")
async def api_learning_capture():
    return {"ok": True, "captured": _learn_capture()}

@app.post("/api/v1/learning/dataset/generate")
async def api_learning_dataset(payload: dict = None):
    payload = payload or {}
    return _learn_ds(payload.get("name", "richard-core-v1"))

@app.post("/api/v1/learning/fine-tune")
async def api_learning_finetune(payload: dict = None):
    payload = payload or {}
    return _learn_ft(payload.get("model", "qwen3-32b"), payload.get("dataset", "richard-core-v1"))

@app.post("/api/v1/learning/improve-core")
async def api_learning_improve(payload: dict = None):
    payload = payload or {}
    return _learn_improve(int(payload.get("threshold", 3)))

# ===== #17 Neural Collaboration (v3.22) =====
import sys as _n1, pathlib as _n2
_n1.path.insert(0, str(_n2.Path(__file__).resolve().parent))
from collab_engine import collab_graph as _collab_graph, send_message as _collab_send, \
    inbox as _collab_inbox, mark_read as _collab_read, validate as _collab_validate, seed as _collab_seed

@app.get("/api/v1/collab/graph")
async def api_collab_graph():
    return _collab_graph()

@app.get("/api/v1/collab/agents")
async def api_collab_agents():
    g = _collab_graph()
    return {"ok": True, "agents": g["nodes"]}

@app.post("/api/v1/collab/message")
async def api_collab_message(payload: dict = None):
    payload = payload or {}
    s = payload.get("sender", "").strip(); r = payload.get("recipient", "").strip()
    subj = payload.get("subject", "").strip()
    if not s or not r or not subj:
        return {"ok": False, "error": "sender, recipient, subject required"}
    return _collab_send(s, r, subj, payload.get("body", ""))

@app.get("/api/v1/collab/inbox/{agent}")
async def api_collab_inbox(agent: str):
    return _collab_inbox(agent)

@app.post("/api/v1/collab/read")
async def api_collab_read(payload: dict = None):
    payload = payload or {}
    return _collab_read(int(payload.get("message_id", 0)))

@app.post("/api/v1/collab/validate")
async def api_collab_validate(payload: dict = None):
    payload = payload or {}
    return _collab_validate(payload.get("validator", ""), payload.get("target", ""),
                            payload.get("verdict", ""), payload.get("note", ""))

@app.post("/api/v1/collab/seed")
async def api_collab_seed():
    return {"ok": True, "seeded": _collab_seed()}

# ===== #18 Doc-chat + Vision (v3.23) =====
import sys as _dc1, pathlib as _dc2
_dc1.path.insert(0, str(_dc2.Path(__file__).resolve().parent))
from doc_chat import upload_doc as _doc_upload, ask as _doc_ask, list_docs as _doc_list, doc_messages as _doc_msgs

@app.post("/api/v1/docchat/upload")
async def api_docchat_upload(file: UploadFile = File(...)):
    try:
        data = await file.read()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    name = file.filename or "upload.bin"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "text"
    kind = "pdf" if ext == "pdf" else "image" if ext in ("png", "jpg", "jpeg", "gif", "webp") else "text"
    return _doc_upload(name, data, kind)

@app.post("/api/v1/docchat/ask")
async def api_docchat_ask(payload: dict = None):
    payload = payload or {}
    doc_id = payload.get("doc_id"); q = (payload.get("question") or "").strip()
    if not doc_id or not q:
        return {"ok": False, "error": "doc_id + question required"}
    return _doc_ask(int(doc_id), q)

@app.get("/api/v1/docchat/docs")
async def api_docchat_docs():
    return _doc_list()

@app.get("/api/v1/docchat/messages/{doc_id}")
async def api_docchat_messages(doc_id: int):
    return _doc_msgs(doc_id)

# ===== #19 Life Agents: Health + Travel + Shopping (v3.24) =====
import sys as _h1, pathlib as _h2
_h1.path.insert(0, str(_h2.Path(__file__).resolve().parent))
from life_agents import overview as _life_ov, add_health as _life_health, list_health as _life_health_list, \
    add_trip as _life_trip, list_trips as _life_trips, add_shopping as _life_shop, \
    toggle_shopping as _life_toggle, list_shopping as _life_shop_list, seed as _life_seed

@app.get("/api/v1/life/overview")
async def api_life_overview():
    return _life_ov()

@app.post("/api/v1/life/health/add")
async def api_life_health_add(payload: dict = None):
    payload = payload or {}
    import datetime as _dt
    return _life_health(payload.get("date", _dt.date.today().isoformat()), payload.get("kind", ""),
                        payload.get("detail", ""), payload.get("metric"), payload.get("note", ""))

@app.get("/api/v1/life/health")
async def api_life_health():
    return _life_health_list()

@app.post("/api/v1/life/trip/add")
async def api_life_trip_add(payload: dict = None):
    payload = payload or {}
    return _life_trip(payload.get("destination", ""), payload.get("start_date", ""),
                      payload.get("end_date", ""), payload.get("budget"), payload.get("notes", ""))

@app.get("/api/v1/life/trips")
async def api_life_trips():
    return _life_trips()

@app.post("/api/v1/life/shopping/add")
async def api_life_shopping_add(payload: dict = None):
    payload = payload or {}
    return _life_shop(payload.get("item", ""), payload.get("category", "general"),
                      int(payload.get("qty", 1)), payload.get("price"))

@app.post("/api/v1/life/shopping/toggle")
async def api_life_shopping_toggle(payload: dict = None):
    payload = payload or {}
    return _life_toggle(int(payload.get("id", 0)))

@app.get("/api/v1/life/shopping")
async def api_life_shopping():
    return _life_shop_list()

@app.post("/api/v1/life/seed")
async def api_life_seed():
    return {"ok": True, "seeded": _life_seed()}

# ===== #11 Model Orchestrator (v3.25) =====
import sys as _m1, pathlib as _m2
_m1.path.insert(0, str(_m2.Path(__file__).resolve().parent))
from model_orchestrator import status as _mo_status, route_model as _mo_route, \
    resolve_model as _mo_resolve, set_route as _mo_set, available_models as _mo_avail

@app.get("/api/v1/models/status")
async def api_models_status():
    return _mo_status()

@app.get("/api/v1/models/available")
async def api_models_available():
    return {"ok": True, "models": _mo_avail()}

@app.get("/api/v1/models/route/{task_type}")
async def api_models_route(task_type: str, agent: str = ""):
    return _mo_resolve(task_type, agent or None)

@app.post("/api/v1/models/route")
async def api_models_set_route(payload: dict = None):
    payload = payload or {}
    return _mo_set(payload.get("task_type", "default"), payload.get("model", "deepseek-v4-flash-free"),
                   payload.get("tier"), payload.get("why", ""))

# ===== #13 Registry (v3.28) =====
import sys as _r1, pathlib as _r2
_r1.path.insert(0, str(_r2.Path(__file__).resolve().parent))
from registry import registry as _registry

@app.get("/api/v1/registry")
async def api_registry():
    return _registry()

@app.get("/api/v1/registry/{category}")
async def api_registry_category(category: str):
    return _registry(category)

# ===== #10 Task Manager assign (v3.29) =====
import sys as _a1, pathlib as _a2
_a1.path.insert(0, str(_a2.Path(__file__).resolve().parent))
from task_assigner import assign_task as _assign, list_assignments as _assign_list

@app.post("/api/v1/tasks/assign")
async def api_tasks_assign(payload: dict = None):
    payload = payload or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return {"ok": False, "error": "title required"}
    return _assign(title, payload.get("dept"))

@app.get("/api/v1/tasks/assignments")
async def api_tasks_assignments():
    return _assign_list()

# ===== #11 Local Inference (v3.30) =====
import sys as _g1, pathlib as _g2
_g1.path.insert(0, str(_g2.Path(__file__).resolve().parent))
from local_inference import status as _li_status, generate as _li_gen

@app.get("/api/v1/models/local/status")
async def api_local_status():
    return _li_status()

@app.post("/api/v1/models/local/generate")
async def api_local_generate(payload: dict = None):
    payload = payload or {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"ok": False, "error": "prompt required"}
    return _li_gen(prompt, int(payload.get("max_new", 60)))

# ===== v4.0 Repository Intelligence (v3.31) =====
import sys as _ri1, pathlib as _ri2
_ri1.path.insert(0, str(_ri2.Path(__file__).resolve().parent))
from repo_intel import ingest as _ri_ingest, list_intel as _ri_list, intel_detail as _ri_detail

@app.post("/api/v1/repo/ingest")
async def api_repo_ingest(payload: dict = None):
    payload = payload or {}
    url = (payload.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "url required"}
    return {"ok": True, **(_ri_ingest(url) or {"error": "ingest failed"})}

@app.get("/api/v1/repo/intel")
async def api_repo_intel():
    return {"ok": True, "repos": _ri_list()}

@app.get("/api/v1/repo/intel/{name}")
async def api_repo_intel_detail(name: str):
    d = _ri_detail(name)
    return {"ok": True, "repo": d} if d else {"ok": False, "error": "not found"}

# ===== v4.0 Execution Engine (v3.32) =====
import sys as _ex1, pathlib as _ex2
_ex1.path.insert(0, str(_ex2.Path(__file__).resolve().parent))
from execution_engine import enqueue as _ex_enqueue, execute_async as _ex_run, \
    job_status as _ex_status, queue as _ex_queue, retry as _ex_retry

@app.post("/api/v1/execution/run")
async def api_execution_run(payload: dict = None):
    payload = payload or {}
    name = (payload.get("name") or "").strip()
    steps = payload.get("steps") or []
    if not name or not steps:
        return {"ok": False, "error": "name + steps required"}
    r = _ex_enqueue(name, steps, int(payload.get("max_retries", 2)))
    if r.get("ok"):
        _ex_run(r["job_id"])
    return r

@app.get("/api/v1/execution/status/{job_id}")
async def api_execution_status(job_id: int):
    return _ex_status(job_id)

@app.get("/api/v1/execution/queue")
async def api_execution_queue():
    return _ex_queue()

@app.post("/api/v1/execution/retry/{job_id}")
async def api_execution_retry(job_id: int):
    return _ex_retry(job_id)

# ===== v4.0 Validation Engine (v3.33) =====
import sys as _v1p, pathlib as _v2p
_v1p.path.insert(0, str(_v2p.Path(__file__).resolve().parent))
from validation_engine import validate as _val_run, history as _val_hist, report as _val_rep

@app.post("/api/v1/validation/run")
async def api_validation_run(payload: dict = None):
    payload = payload or {}
    path = (payload.get("path") or "").strip()
    if not path:
        return {"ok": False, "error": "path required"}
    return _val_run(path, payload.get("name"), int(payload.get("threshold", 70)))

@app.get("/api/v1/validation/report/{rid}")
async def api_validation_report(rid: int):
    r = _val_rep(rid)
    return {"ok": True, "report": r} if r else {"ok": False, "error": "not found"}

@app.get("/api/v1/validation/history")
async def api_validation_history():
    return _val_hist()

# ===== v4.0 Agent Lifecycle (v3.34) =====
import sys as _lc1, pathlib as _lc2
_lc1.path.insert(0, str(_lc2.Path(__file__).resolve().parent))
from agent_lifecycle import start as _lc_start, advance as _lc_adv, agent_state as _lc_state, all_states as _lc_all

@app.post("/api/v1/lifecycle/start/{agent}")
async def api_lifecycle_start(agent: str):
    return _lc_start(agent)

@app.post("/api/v1/lifecycle/advance/{agent}")
async def api_lifecycle_advance(agent: str):
    return _lc_adv(agent)

@app.get("/api/v1/lifecycle/{agent}")
async def api_lifecycle_agent(agent: str):
    return _lc_state(agent)

@app.get("/api/v1/lifecycle")
async def api_lifecycle_all():
    return _lc_all()

# ===== v4.0 Memory System (v3.35) =====
import sys as _memp, pathlib as _memq
_memp.path.insert(0, str(_memq.Path(__file__).resolve().parent))
from memory_system import add as _mem_add, get as _mem_get, counts as _mem_counts, \
    search as _mem_search, promote as _mem_promote, TYPES as _MEM_TYPES

@app.get("/api/v1/memory")
async def api_memory_counts():
    return _mem_counts()

@app.get("/api/v1/memory/{mtype}")
async def api_memory_type(mtype: str):
    return _mem_get(mtype)

@app.post("/api/v1/memory/{mtype}")
async def api_memory_add(mtype: str, payload: dict = None):
    payload = payload or {}
    content = (payload.get("content") or "").strip()
    if not content:
        return {"ok": False, "error": "content required"}
    return _mem_add(mtype, content, payload.get("tags"), int(payload.get("importance", 1)))

@app.post("/api/v1/memory/search")
async def api_memory_search(payload: dict = None):
    payload = payload or {}
    q = (payload.get("query") or "").strip()
    if not q:
        return {"ok": False, "error": "query required"}
    return _mem_search(q)

@app.post("/api/v1/memory/promote/{mem_id}")
async def api_memory_promote(mem_id: int):
    return _mem_promote(mem_id)

# ===== v4.0 Plugin Store (v3.36) =====
import sys as _ps1, pathlib as _ps2
_ps1.path.insert(0, str(_ps2.Path(__file__).resolve().parent))
from plugin_store import catalog as _ps_cat, install as _ps_inst, uninstall as _ps_uninst, status as _ps_status

@app.get("/api/v1/plugins")
async def api_plugins():
    return _ps_cat()

@app.post("/api/v1/plugins/install/{name}")
async def api_plugins_install(name: str):
    return _ps_inst(name)

@app.post("/api/v1/plugins/uninstall/{name}")
async def api_plugins_uninstall(name: str):
    return _ps_uninst(name)

@app.get("/api/v1/plugins/status")
async def api_plugins_status():
    return _ps_status()

# ===== v4.0 System Services (v3.37) =====
import sys as _sys1, pathlib as _sys2
_sys1.path.insert(0, str(_sys2.Path(__file__).resolve().parent))
from system_services import health as _sys_health, metrics as _sys_metrics, \
    emit as _sys_emit, events as _sys_events

@app.get("/api/v1/system/health")
async def api_system_health():
    return _sys_health()

@app.get("/api/v1/system/metrics")
async def api_system_metrics():
    return _sys_metrics()

@app.post("/api/v1/system/event")
async def api_system_event(payload: dict = None):
    payload = payload or {}
    return _sys_emit(payload.get("type", "event"), payload.get("payload", ""))

@app.get("/api/v1/system/events")
async def api_system_events():
    return _sys_events()

# ===== Phase F1 Context Assembly (v3.39) =====
import sys as _cx1, pathlib as _cx2
_cx1.path.insert(0, str(_cx2.Path(__file__).resolve().parent))
from context_assembly import assemble as _ctx_assemble

@app.get("/api/v1/context")
async def api_context(request: str = "Build a fitness app", dept: str = "web", sub: str = ""):
    return {"ok": True, "envelope": _ctx_assemble(request, dept, sub or None)}

# ===== Phase F Intelligent Escalation (v3.39) =====
import sys as _ph1, pathlib as _ph2
_ph1.path.insert(0, str(_ph2.Path(__file__).resolve().parent))
from model_orchestrator import provider_status as _prov_status
from escalation_engine import execute as _esc_execute

@app.get("/api/v1/models/providers")
async def api_models_providers():
    return _prov_status()

@app.post("/api/v1/escalation/execute")
async def api_escalation_execute(payload: dict = None):
    payload = payload or {}
    request = (payload.get("request") or "").strip()
    if not request:
        return {"ok": False, "error": "request required"}
    return _esc_execute(request, payload.get("dept", "web"), payload.get("sub"))

# ===== Phase G1 Vector DB (v3.40) =====
import sys as _vd1, pathlib as _vd2
_vd1.path.insert(0, str(_vd2.Path(__file__).resolve().parent))
from vector_db import build_index as _vd_build, search as _vd_search

@app.post("/api/v1/vector/build")
async def api_vector_build():
    return _vd_build()

@app.post("/api/v1/vector/search")
async def api_vector_search(payload: dict = None):
    payload = payload or {}
    q = (payload.get("query") or "").strip()
    if not q:
        return {"ok": False, "error": "query required"}
    try:
        return {"ok": True, "results": _vd_search(q, int(payload.get("top", 5)))}
    except FileNotFoundError:
        return {"ok": False, "error": "index not built — POST /api/v1/vector/build first"}

# ===== Phase G2 Knowledge Graph (v3.41) =====
import sys as _kg1, pathlib as _kg2
_kg1.path.insert(0, str(_kg2.Path(__file__).resolve().parent))
from knowledge_graph import graph as _kg_graph, neighbors as _kg_neighbors, \
    add_triple as _kg_add, extract_from_sources as _kg_extract

@app.get("/api/v1/knowledge-graph")
async def api_kg():
    return _kg_graph()

@app.get("/api/v1/knowledge-graph/neighbors/{node}")
async def api_kg_neighbors(node: str):
    return _kg_neighbors(node)

@app.post("/api/v1/knowledge-graph/triple")
async def api_kg_triple(payload: dict = None):
    payload = payload or {}
    return _kg_add(payload.get("subj", ""), payload.get("rel", ""), payload.get("obj", ""))

@app.post("/api/v1/knowledge-graph/extract")
async def api_kg_extract():
    return {"ok": True, "added": len(_kg_extract())}
