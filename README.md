# Richard OS

![CI](https://github.com/Sujith-richard/richard-os/actions/workflows/ci.yml/badge.svg)

A personal AI operating system: memory, tools, agents, and skills in one folder your AI runs.
Built by Sujith Richard. Free. Files you own outright — no subscription.

## What it is
- 5 systems of record: second brain, PM, finance, CRM, creator (SQLite)
- Agents with honest run logs: job_hunter, content_ops, freelance_biz, pm_assistant, portfolio_builder
- 5 skills: outreach, resume_tailor, invoice, linkedin_post, job_screen
- Scheduler: agents run on a schedule while you sleep
- Knowledge-graph UI: a live map of everything your OS knows

## v2.0 — Domains, Approval & Live Graph
- **Super-Orchestrator**: routes plain-English requests to company/home/personal trees (`scripts/orchestrator.py`)
- **Company hierarchy**: HR (recruiter/payroll/onboarding), Dev (backend/frontend/tester), Finance (invoicing/expense), Ops (fulfillment/support) — `scripts/company_agents.py`
- **Home control**: room-wise device agents (simulated, Home Assistant-ready) — `scripts/home_agents.py`
- **Personal assistant**: email triage, calendar, reminders — `scripts/personal_agents.py`
- **MCP layer**: web, weather, GitHub, email tools — `tools/mcp_bridge.py`
- **Approval queue**: autonomy-2 drafts (email, invoices, outreach) queue for one-click approve — `scripts/approval_queue.py`
- **Fake-data-first**: `DATA_MODE=fake` in `.env`; seed with `python scripts/seed_data.py`
- **Knowledge graph v2**: zoom/pan, hover-glow of connections, click-to-drill with back button, live agent pulse

## Cross-platform CI
GitHub Actions verifies boot + DB init + seed + CLI smoke on Linux/Windows/macOS.

## Quickstart
```bash
git clone https://github.com/Sujith-richard/richard-os.git
cd richard-os
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 scripts/init_db.py
python3 scripts/seed_data.py
python3 run.py
## Approval queue
```bash
python3 scripts/approval_queue.py list
python3 scripts/approval_queue.py approve 1
## Knowledge-graph UI
```bash
python3 -m uvicorn scripts.server:app --reload --port 8000
# open http://localhost:8000/ui/
## Structure
01-root-spine/ system, encoding, invariants, config
02-blocks/ departments (company/home/personal trees)
03-agents/ named workers + logs
04-skills/ repeatable moves
05-systems-of-record/ CRM, finance, PM, content, second brain
06-data/ SQLite DBs
07-schedules/ scheduler + briefs
scripts/ CLI, agents, orchestrator, server
tools/ MCP bridge + home bridge
ui/ knowledge-graph front-end

## Autonomy levels
1 Lookup · 2 Recommend · 3 Act & spot-check · 4 Runs independently · 5 Self-monitoring
Set per agent in `01-root-spine/company.yaml`.
## Screenshots
![Console](docs/screenshots/01-console.png)
![Brain — Knowledge Graph](docs/screenshots/02-brain.png)
![Brain — Node Focus](docs/screenshots/03-brain-focus.png)
![Agents](docs/screenshots/04-agents.png)
![Finances](docs/screenshots/05-finances.png)
![Funnel](docs/screenshots/06-funnel.png)
![Comms](docs/screenshots/07-comms.png)
![Social](docs/screenshots/08-social.png)

## v3.0 — Full command center
- Sidebar v2 (18 views) + 8 themes + ⌘K palette
- Executive mission-control dashboard (stats + charts + AI feed)
- Communications (7 channel tabs, sentiment, AI summary, suggested replies)
- Funnel 7-stage kanban + KPIs + conversion chart
- Social + Content analytics (reach, likes, SEO score, reading time)
- Finance (MRR, ARR, runway, cash-flow chart)
- Agents roster v2 (confidence, memory, runs, Run/Logs)
- Integrations honest board (never fakes connectivity)
- Analytics suite (9 charts: revenue, funnel, radar, heatmap, sparklines)
- Tasks v2 + Skills library + Org tree + Workflows builder
- Roadmap + Reference + Personas roster pages

## Screenshots
![Dashboard](docs/screenshots/01-console.png)
![Brain](docs/screenshots/02-brain.png)
![Agents](docs/screenshots/03-agents.png)
![Finances](docs/screenshots/04-finances.png)
![Funnel](docs/screenshots/05-funnel.png)
![Comms](docs/screenshots/06-comms.png)
![Social](docs/screenshots/07-social.png)
![Content](docs/screenshots/08-content.png)

## v3.0 — Full command center
- Sidebar v2 (18 views) + 8 themes + ⌘K palette
- Executive mission-control dashboard (stats + charts + AI feed)
- Communications (7 channel tabs, sentiment, AI summary, suggested replies)
- Funnel 7-stage kanban + KPIs + conversion chart
- Social + Content analytics (reach, likes, SEO score, reading time)
- Finance (MRR, ARR, runway, cash-flow chart)
- Agents roster v2 (confidence, memory, runs, Run/Logs)
- Integrations honest board (never fakes connectivity)
- Analytics suite (9 charts: revenue, funnel, radar, heatmap, sparklines)
- Tasks v2 + Skills library + Org tree + Workflows builder
- Roadmap + Reference + Personas roster pages

## Screenshots
![Dashboard](docs/screenshots/01-console.png)
![Brain](docs/screenshots/02-brain.png)
![Agents](docs/screenshots/03-agents.png)
![Finances](docs/screenshots/04-finances.png)
![Funnel](docs/screenshots/05-funnel.png)
![Comms](docs/screenshots/06-comms.png)
![Social](docs/screenshots/07-social.png)
![Content](docs/screenshots/08-content.png)

## v3.0 — Full command center
- Sidebar v2 (18 views) + 8 themes + ⌘K palette
- Executive mission-control dashboard (stats + charts + AI feed)
- Communications (7 channel tabs, sentiment, AI summary, suggested replies)
- Funnel 7-stage kanban + KPIs + conversion chart
- Social + Content analytics (reach, likes, SEO score, reading time)
- Finance (MRR, ARR, runway, cash-flow chart)
- Agents roster v2 (confidence, memory, runs, Run/Logs)
- Integrations honest board (never fakes connectivity)
- Analytics suite (9 charts: revenue, funnel, radar, heatmap, sparklines)
- Tasks v2 + Skills library + Org tree + Workflows builder
- Roadmap + Reference + Personas roster pages

## Screenshots
![Dashboard](docs/screenshots/01-console.png)
![Brain](docs/screenshots/02-brain.png)
![Agents](docs/screenshots/03-agents.png)
![Finances](docs/screenshots/04-finances.png)
![Funnel](docs/screenshots/05-funnel.png)
![Comms](docs/screenshots/06-comms.png)
![Social](docs/screenshots/07-social.png)
![Content](docs/screenshots/08-content.png)

## v3.3.0 — Project Generation Engine (#15)
Turn a plain-English brief into a delivered, scored project scaffold.

- **Pipeline:** brief-intake → route → scaffold → review-fix → security → quality → package → deliver → learning
- **Routing:** word-boundary keyword match → frontend / backend / fullstack (web-dev.yaml)
- **Scaffolding:** React+Vite, FastAPI, or fullstack docker-compose trees in `06-data/generated_projects/`
- **Gates:** review-fix loop (max 3 iters) · security scan · quality score (≥80%)
- **Delivery:** `.zip` archive + `delivery_manifest.json` per project
- **Learning engine:** repeatable lessons auto-promote (count ≥3 → skill)
- **API:** `POST /api/v1/project/generate` · `GET /api/v1/project/status/{id}` · `GET /api/v1/project/list`
- **UI:** `ui/project-gen.html` — stage chips, file tree, learning log, history
- **Dept block:** `02-blocks/company/web-dev.yaml`
