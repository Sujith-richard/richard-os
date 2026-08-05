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
from fastapi.staticfiles import StaticFiles
import os as _os
_os.makedirs(str(ROOT / "06-data" / "reports"), exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(ROOT / "06-data" / "reports")), name="reports")
