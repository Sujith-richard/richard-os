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

## v3.5.0 — Live Integrations Hub (real-data swap, UI-driven)
Flip any data source from seeded FAKE to real LIVE — from the browser, no .env edits.

- **Sources:** GitHub (public API), Gmail (IMAP app-password), Weather (Open-Meteo), Home Assistant (REST), AI Models (AI-Workspace proxy)
- **Per-source status:** fake → unconfigured → live/error · LIVE/DEMO pill in every shell topbar
- **UI:** `ui/integrations.html` — cards with badges, config fields, Test / Sync / mode toggle
- **API:** `GET /api/v1/integrations` · `POST .../test|sync|mode|config`
- **Swap:** consumers read `live_*.json` when live, seeded DBs when fake (no logic rewrites)
- **Secrets:** config lives in `06-data/integrations.json` (gitignored, stays local)

## v3.19.0 — Department Layer (#14)
Every department is now a real, self-contained unit with a full 16-item spine.

- **Spec:** `02-blocks/company/departments-spec.yaml` — 8 depts (web, ai, data, cyber, cloud, robotics, finance, hr): lead, specialists, skills, stacks, autonomy, decision rules, workflows, datasets
- **Engine:** `scripts/department_engine.py` scaffolds each dept folder: knowledge/skills/agents/prompts/templates/standards/rules/workflows/docs/git/mcp/memory/datasets/training (15 files each)
- **API:** `GET /api/v1/departments` · `GET /api/v1/departments/{name}` · `GET .../{name}/file?path=` · `POST /api/v1/departments/generate`
- **UI:** `ui/departments.html` — dept cards → spine explorer → file viewer
- **Org tree** now reads the live spec (was 19 hardcoded, now spec-driven)

## v3.20.0 — Planner AI + Workflow Engine (#10)
Goals become runnable workflows — real state machines, not static cards.

- **Planner AI:** `scripts/planner.py` turns a goal into a step plan (trigger/agent/data/approve/action)
- **Workflow Engine:** `scripts/workflow_engine.py` executes workflows step-by-step, tracks status (idle/running/done/error), persists runs + step logs to `06-data/workflows.db`
- **API:** `GET /api/v1/workflows` · `GET /{name}` · `POST /plan` · `POST /{name}/run` · `POST /seed`
- **UI:** `ui/workflows.html` — live workflows with real status/runs, RUN button + step log, Planner AI input (goal → plan)
- **Honest status:** `/workflow-status` now reads the DB (was hardcoded fake)

## v3.21.0 — Continuous Learning (#16)
The feedback loop: capture → dataset → fine-tune → improve core.

- **Capture:** run logs + project learnings + workflow runs → samples/lessons (`scripts/learning_engine.py`)
- **Dataset:** generate JSONL training set (instruction/input/output) → `06-data/datasets/`
- **Fine-tune:** mark a model fine-tuned on the dataset (fake-first; real hook via models integration)
- **Improve core:** repeated lessons (count ≥ 3) auto-promoted into `04-skills/`
- **API:** `GET /api/v1/learning/overview` · `POST /capture` · `POST /dataset/generate` · `POST /fine-tune` · `POST /improve-core`
- **UI:** `ui/learning.html` — 4-stage loop with Run buttons + top lessons

## v3.22.0 — Neural Collaboration (#17)
Agents share through the graph, not point-to-point.

- **Shared bus:** `scripts/collab_engine.py` — 27 agents (core engines + company + personal + persona), send/read messages, validate each other, edge stats
- **Live edges:** `06-data/collab.db` edges table — message counts + last activity per sender→recipient
- **API:** `GET /api/v1/collab/graph` · `GET /agents` · `POST /message` · `GET /inbox/{agent}` · `POST /validate`
- **UI:** `ui/collab.html` — live collaboration edges, message composer, validation, agent inbox

## v3.22.0 — Neural Collaboration (#17)
Agents share through the graph, not point-to-point.

- **Shared bus:** `scripts/collab_engine.py` — 27 agents (core engines + company + personal + persona), send/read messages, validate each other, edge stats
- **Live edges:** `06-data/collab.db` edges table — message counts + last activity per sender→recipient
- **API:** `GET /api/v1/collab/graph` · `GET /agents` · `POST /message` · `GET /inbox/{agent}` · `POST /validate`
- **UI:** `ui/collab.html` — live collaboration edges, message composer, validation, agent inbox

## v3.23.0 — Doc Chat + Vision (#18)
Upload a document — then ask questions grounded in it.

- **Doc-chat:** `scripts/doc_chat.py` — PDF text extraction (pypdf), text upload, chunking + lexical search, grounded Q&A via `agent_lib.call_llm`
- **Vision:** image upload → base64 → Model Orchestrator routing (gemini-3.5-flash → gpt-oss-120b → default), honest fallback if no vision-capable model
- **API:** `POST /api/v1/docchat/upload` (multipart) · `POST /ask` · `GET /docs` · `GET /messages/{id}`
- **UI:** `ui/docchat.html` — upload zone, doc picker, chat thread with source chunks

## v3.24.0 — Personal Life Trackers (#19) — FINAL LAYER
Health · Travel · Shopping systems of record, alongside email/tasks/calendar/smart-home.

- **Life agents:** `scripts/life_agents.py` — health (workout/steps/sleep), trips (planned with budget), shopping (open/bought), seeded fake-first
- **API:** `GET /api/v1/life/overview` · `GET /health|trips|shopping` · `POST /health/add|trip/add|shopping/add|shopping/toggle`
- **UI:** `ui/life.html` — 3 tracker cards with add-forms + lists
- **Collab:** health-agent / travel-agent / shopping-agent added to the Neural Collaboration roster (30 agents)

## v3.25.0 — Model Orchestrator (#11/#10)
Routes every task to the best model — real per-task selection, not a hardcoded default.

- **Orchestrator:** `scripts/model_orchestrator.py` — 11 task types (chat/plan/code/analysis/creative/reasoning/vision/research/summarize/quick/default) → tier (fast/balanced/power) → model + fallback chain
- **Wired everywhere:** `agent_lib.call_llm(prompt, task_type=..., agent=...)` routes through the orchestrator by default; per-agent overrides supported
- **API:** `GET /api/v1/models/status` · `GET /available` · `GET /route/{task_type}?agent=` · `POST /route` (set)
- **UI:** `ui/models.html` — routing table with live availability + per-task route editor

## v3.26.0 — PWA + Mobile Drawer (#18 mobile)
Richard OS is now installable and phone-navigable.

- **PWA:** `ui/manifest.json` (standalone, theme #0A101F) + `ui/sw.js` service worker (cache shell, offline fallback) + icons 192/512
- **Mobile drawer:** at ≤600px the sidebar becomes a slide-in drawer with ☰ hamburger in the topbar + backdrop tap-to-close
- **Registration:** shell.js injects the manifest link + registers the SW on every shell page

## v3.27.0 — Real Fine-Tune Hook (#16)
The learning loop's fine-tune stage now actually trains.

- **Real trainer:** `scripts/train_lora.py` — trains a tiny causal LM (sshleifer/tiny-gpt2) on our JSONL dataset (instruction/input/output) with real loss/gradients, checkpoints to `06-data/models/`, logs to `06-data/train_logs/`
- **Wired:** `learning_engine.fine_tune()` runs the trainer via subprocess (status training → done/error, real checkpoint path)
- **Auto-device:** uses CUDA automatically when the NVIDIA driver is present (RTX 3050 in this laptop — driver pending), CPU otherwise
- **Honest:** tiny model + small steps = real but modest (fits CPU/15GB); scale model+steps when GPU is live

## v3.28.0 — Resource Registry (#13)
Unified view of every resource the OS can reach.

- **Aggregator:** `scripts/registry.py` — tools (tools_config.json), MCP tools (mcp_tools.status), repos (live-github/repos.json), resource packages, plugins
- **API:** `GET /api/v1/registry` · `GET /api/v1/registry/{category}`
- **UI:** `ui/registry.html` — 5 category cards (Tools/MCP/Repos/Packages/Plugins) with counts + statuses

## v3.29.0 — Task Manager Assign Service (#10)
Real assignment: a task title → the best agent from the 30-agent roster.

- **Assigner:** `scripts/task_assigner.py` — keyword/skill matching (email→email-agent, code→backend, frontend→frontend, strategy→planner-ai, shopping→shopping-agent…) + explicit dept override + word-overlap fallback
- **API:** `POST /api/v1/tasks/assign` (title, dept?) · `GET /api/v1/tasks/assignments`
- **UI:** Assign bar on `ui/tasks.html` — type a task, see who owns it + why

## v3.30.0 — Local Inference (#11 final)
The Model Orchestrator now has a real LOCAL tier — the RTX 3050 serves completions.

- **Local engine:** `scripts/local_inference.py` — loads the fine-tuned checkpoint on CUDA (model cached once), `generate(prompt)` → real completion
- **API:** `GET /api/v1/models/local/status` · `POST /api/v1/models/local/generate`
- **UI:** Local Inference panel on `ui/models.html` — status + prompt box + output
- **Honest:** tiny model (fine-tuned on our dataset) = real local GPU inference, modest quality; swap in a bigger checkpoint anytime

## v3.31.0 — Repository Intelligence (v4.0 flagship)
GitHub repos become part of Richard OS — not external references.

- **Pipeline:** `scripts/repo_intel.py` — shallow clone → README/docs → detect language/framework/type → extract skills/knowledge/workflows/templates/folder-structure/MCP/APIs → persist → register → dept-available
- **Ingested for real:** awesome-claude-skills (Skill Library, 10 skills) · BlueTeam-Tools (Tool Collection, 11 skills) · superpowers (Skill Library)
- **API:** `POST /api/v1/repo/ingest` · `GET /api/v1/repo/intel` · `GET /api/v1/repo/intel/{name}`
- **UI:** `ui/repo-intel.html` — ingest box + repo cards with extraction tree + dept mapping

## v3.32.0 — Execution Engine (v4.0 #2)
Workflow says WHAT. Execution does it — queue, retry, parallel, dependencies, progress.

- **Engine:** `scripts/execution_engine.py` — job queue (execution.db), background threads, dependency resolution (steps wait for deps), parallel step groups, auto-retry (max_retries), progress %, completion
- **API:** `POST /api/v1/execution/run` · `GET /status/{job_id}` · `GET /queue` · `POST /retry/{job_id}`
- **UI:** `ui/execution.html` — live queue with progress bars, step diagrams (parallel + deps), retry buttons

## v3.33.0 — Validation Engine (v4.0 #3)
Everything generated must pass validation — 10 dimensions, composite score, gate.

- **Validator:** `scripts/validation_engine.py` — code_review, security, performance, accessibility, UI, testing, linting, documentation, standards → weighted composite (0-100) + pass/fail gate + report history
- **API:** `POST /api/v1/validation/run` (path, name, threshold) · `GET /report/{id}` · `GET /history`
- **UI:** `ui/validation.html` — dimension bars, gate badge, history
- **Works on:** Project Engine output, repo intel, any generated deliverable

## v3.34.0 — Agent Lifecycle (v4.0 #4)
Every agent now has a full lifecycle state machine.

- **Lifecycle:** `scripts/agent_lifecycle.py` — created → assigned → thinking → uses_models → uses_skills → uses_tools → uses_knowledge → returns_result → reviewer_checks → memory_updated → sleeps (then wraps to a new cycle)
- **API:** `POST /api/v1/lifecycle/start/{agent}` · `POST /advance/{agent}` · `GET /{agent}` · `GET /`
- **UI:** `ui/lifecycle.html` — per-agent timeline dots, current state badge, advance/restart buttons

## v3.35.0 — Memory System (v4.0 #5)
The 11-type memory hierarchy — every memory has a home.

- **Store:** `scripts/memory_system.py` — user, conversation, project, department, agent, tool, workflow, knowledge, experience, long-term, temporary (memory.db) · add/get/search per type · promote temporary → long-term · seeds from second_brain
- **API:** `GET /api/v1/memory` · `GET /{type}` · `POST /{type}` (add) · `POST /search` · `POST /promote/{id}`
- **UI:** `ui/memory.html` — 11-type cards with counts, add bar, search, promote

## v3.36.0 — Plugin Store (v4.0 #6)
Every resource is an installable plugin — catalog + lifecycle.

- **Store:** `scripts/plugin_store.py` — catalog from repo-intel repos (community) + tools + MCP + skills (local), install/uninstall persisted to plugins.db
- **API:** `GET /api/v1/plugins` · `POST /install/{name}` · `POST /uninstall/{name}` · `GET /status`
- **UI:** `ui/plugins.html` — storefront with All/Installed/Community/Local tabs + install buttons

## v3.37.0 — Infrastructure + System Services (v4.0 #7)
Health · Metrics · Event Bus — the layer that keeps Richard OS alive.

- **Services:** `scripts/system_services.py` — live health monitor (database, integrations, GPU, model-proxy, scheduler, queue-manager, event-bus), GPU/CPU metrics, event bus (emit/feed)
- **API:** `GET /api/v1/system/health` · `GET /metrics` · `POST /event` · `GET /events`
- **UI:** `ui/system.html` — service grid with green/amber/red, metrics row, event feed (auto-refresh)

## v3.38.0 — Department 2.0 (v4.0 #8) — v4.0 CAPSTONE
Sub-department standardization — every sub-dept owns its full operating manual.

- **20-item spine:** added project-structures, examples, evaluation, output-formats, plugins, tools to the department template
- **Sub-departments:** web → frontend/backend/database/api/auth/devops/testing/security/docs, each scaffolded with the 21-item standardized template (knowledge/skills/agents/project-structures/templates/rules/standards/prompts/workflows/git/mcp/docs/memory/datasets/training/examples/evaluation/output-formats/plugins/tools)
- **Scale:** web went 15 → 204 files; the same template standardizes every department + sub-department

## v3.39.0 — Intelligent Escalation (Phase F) — Local First, Cloud Assisted, Continuous Learning
The architecture's core loop, running end-to-end.

- **F1 Context Assembly:** `context_assembly.py` packs all 14 resources (dept knowledge, skills, user+long-term memory, repo intel, plugins, MCP, structures, templates, standards, rules, projects, workflows) into ONE envelope before any model call — wired into `call_llm(context=True)`
- **F2 Capability-gap:** `capability_gap.py` classifies why local can't complete (coding/vision/reasoning/knowledge/speed) → specialist (DeepSeek/Gemini/Claude/GPT/Groq)
- **F3 Escalation:** `escalation_engine.py` — local first → gap detect → escalate to specialist via 8-provider chain → auto-learn
- **F4 Auto-merge:** `auto_merge.py` merges local + cloud outputs (cloud fills the gap, local kept when cloud empty)
- **F5 Learn-from-cloud:** `learn_from_cloud.py` — every cloud success → quality check → experience memory → training dataset (cloud-assisted.jsonl) → future fine-tunes
- **F6 Provider chain:** 8 providers (local, DeepSeek, Gemini, Groq, Claude, GPT, Qwen, Mistral) with live availability
- **API:** `GET /api/v1/models/providers` · `POST /api/v1/escalation/execute` · `GET /api/v1/context`

## v3.40.0 — Vector DB (Phase G1)
Semantic retrieval across memory, repo intel, and skills.

- **Vector DB:** `scripts/vector_db.py` — sklearn TF-IDF cosine index over 54 docs (memory/repo-intel/skills), build + search by similarity (pluggable to sentence-transformers later)
- **API:** `POST /api/v1/vector/build` · `POST /api/v1/vector/search`
- **UI:** semantic vector search added to Memory page (rebuild + results)

## v3.41.0 — Knowledge Graph (Phase G2)
Entities + relations — semantic depth over the structural brain graph.

- **Graph:** `scripts/knowledge_graph.py` — subject-relation-object triple extraction (heuristic patterns: is-a/uses/builds/runs-on/contains/depends-on/belongs-to), node+edge store (knowledge_graph.db), neighbor/relation queries
- **API:** `GET /api/v1/knowledge-graph` · `GET /neighbors/{node}` · `POST /triple` · `POST /extract`
- **UI:** `ui/kg.html` — node cards, click-to-query neighbors, extract button

## v3.42.0 — RAG Doc-Chat (Phase G3)
Doc-chat now retrieves via vectors, not just keywords.

- **RAG:** `doc_chat._search_chunks` upgraded from keyword-overlap to TF-IDF cosine over the doc's chunks (sklearn, same technique as vector_db) with lexical fallback
- **Verified:** "What hardware for ML?" → retrieved the RTX chunk → grounded answer "NVIDIA RTX 3050"

## v3.43.0 — Vision Feedback Pipeline (Phase G4) — Phase G COMPLETE
Image → vision analyze → structured UI spec → knowledge → local retry.

- **Pipeline:** `scripts/vision_pipeline.py` — analyze image (vision-capable models) → extract spec (layout/components/colors/nav) → store experience memory + knowledge-graph triples (image →represents→ component, →uses-layout→) → return retry_prompt for the local model

## v3.44.0 — Settings (Phase H4)
User preferences, persisted + consumed by agents.

- **Store:** `scripts/settings.py` — name/city/timezone/preferred_dept/default_model/theme/notifications/morning_brief/voice_enabled/autonomy_level → 06-data/settings.json (gitignored), type-coerced
- **API:** `GET /api/v1/settings` · `POST /api/v1/settings` · `POST /reset`
- **UI:** `ui/settings.html` — profile + AI preferences + system toggles

## v3.45.0 — Automation Center (Phase H5)
Manage every scheduled job from the UI.

- **Center:** `scripts/automation_center.py` — registry of scheduler agents (8) + execution jobs + user automations (automations.json); enable/disable, run-now (launches agent), create scheduled jobs
- **API:** `GET /api/v1/automations` · `POST /` (create) · `POST /{id}/toggle` · `POST /{id}/run`
- **UI:** `ui/automations.html` — job list with run + enable/disable, create form

## v3.46.0 — Model Registry (Phase E4)
Versioned fine-tuned checkpoints — register, promote, deploy, rollback.

- **Registry:** `scripts/model_registry.py` — model_registry.db (name/path/dataset/samples/eval_score/version/status), register (auto version bump), promote→active, deploy (writes ACTIVE.txt pointer), rollback; `active_model()` feeds local_inference (deploy actually takes effect)
- **API:** `GET /api/v1/model-registry` · `POST /register` · `POST /promote/{id}` · `POST /rollback/{id}` · `POST /deploy`
- **UI:** `ui/models-registry.html` — model cards with version/eval/status, promote + deploy buttons

## v3.47.0 — Basic Auth (Phase I1)
The server now requires sign-in.

- **Auth:** `scripts/auth.py` — pbkdf2-hashed users (users.json), token sessions (sessions.json), login/logout/verify
- **API:** `POST /api/v1/auth/login` · `POST /logout` · `GET /me` · `GET /verify`
- **UI:** `ui/login.html` — sign-in form (sets token cookie) · shell redirects to login without a token
- **Setup:** `python3 scripts/auth.py --setup <user> <pass>`

## v3.48.0 — Secret Vault (Phase I3)
API keys and tokens encrypted at rest (Fernet), decrypt-on-use.

- **Vault:** `scripts/vault.py` — Fernet (AES-128-CBC + HMAC), key derived from PBKDF2/200k, key file or RICHARD_MASTER_KEY env; save/get/list/delete; integrations connectors read gmail/github secrets from the vault
- **API:** `GET /api/v1/vault` · `POST /` (store) · `GET /{name}` · `POST /{name}/delete`

## v3.49.0 — Memory Lifecycle (Phase D4)
Temporary memories auto-promote to long-term; stale ones decay.

- **Lifecycle:** `scripts/memory_lifecycle.py` — promote temp → long-term by importance (≥2) or age (≥24h), delete stale temps (TTL 7d)
- **API:** `POST /api/v1/memory/lifecycle/run` (dry_run opt) · `GET /stats`

## v3.50.0 — Project Structure Repository (Phase B6)
Blueprint catalog — 12 structures (react/nextjs/vue/fastapi/django/express/postgres/mongodb/rest/graphql/docker/jwt) with alias + keyword resolution; project_engine routing is blueprint-aware.
- **API:** `GET /api/v1/structures` · `GET /{name}` · `POST /scaffold` · **UI:** `ui/structures.html`

## v3.51.0 — Audit Logs (Phase I4)
Every API action logged (method, path, user, status) to audit.db + middleware + viewer endpoint.

- **Audit:** `scripts/audit.py` · **Middleware:** all requests logged automatically · **API:** `GET /api/v1/audit`

## v3.52.0 — User Management (Phase I2)
Add/list/remove users.

- **Auth:** `auth.py` list_users/remove_user · **API:** `GET /api/v1/auth/users` · `POST /` (add) · `POST /{user}/remove`

## v3.52.0 — User Management (Phase I2)
Add/list/remove users.

- **Auth:** `auth.py` list_users/remove_user · **API:** `GET /api/v1/auth/users` · `POST /` (add) · `POST /{user}/remove`

## v3.52.0 — User Management (Phase I2)
Add/list/remove users. **API:** `GET /api/v1/auth/users` · `POST /` · `POST /{user}/remove`

## v3.53.0 — Deep Security Scan (Phase I5)
Severity-ranked vuln scan of any project dir (secrets, unsafe eval/exec, SQLi/XSS, CORS/CSRF, debug mode).

- **Scanner:** `scripts/security_scan.py` — OWASP-style patterns, BlueTeam-aware · **API:** `POST /api/v1/security/scan`

## 🏆 v4.0.0 — The Complete AI Operating System (CAPSTONE)
All phases shipped. Richard OS is a self-hosted, GPU-powered personal AI operating system.

**Phases delivered:** 19 core layers (v3.3–v3.30) · Real-data swap (v3.18) · 8 v4.0 architecture items (v3.31–v3.38) · Phase F Intelligent Escalation (v3.39) · Phase G Knowledge (v3.40–v3.43) · Phase H UX (H1/H4/H5) · E4 Model Registry (v3.46) · Phase I Security complete (I1 auth, I2 users, I3 vault, I4 audit, I5 deep scan) · D4/B6 quick wins · **B5 sub-dept rollout · H2 desktop launcher · H3 voice/video depth · J3 Docker · J2 autonomy · J1 offline model**

**Run:** `python3 scripts/desktop_launcher.py` → sign in (sujith / Richard-OS-2026) → the OS.
**Container:** `docker compose up`
**Autonomy:** `python3 scripts/autonomy.py`
**Offline:** `python3 scripts/offline_model.py --train` then serve local-first.

## v4.1.0 — 100% COMPLETE (52/52 ToDo items)
The plan is fully shipped. Final four: **A8 kernel boot** (10-subsystem init + retry, kernel_boot.json) · **C5 repo sync** (git pull lifecycle, 20 repos) · **E6 training pipeline 2.0** (clean→label→vectorize→eval split, 396 samples → 317 train/79 eval) · **E5 LoRA on RTX** (peft r=4 adapters, GPU fine-tune in 2s).

---

## 📋 RICHARD OS — COMPLETE FEATURE INDEX (52/52)

### Phases A–J
| Phase | Items | Status |
|---|---|---|
| A. Kernel + Brain | System services, model orchestrator, planner, task manager, workflow, execution, collab, **kernel boot** | ✅ 8/8 |
| B. Departments + Skills + Projects | 20-item dept spine, sub-dept standardization + rollout, skill layer, project engine, **structures repo** | ✅ 6/6 |
| C. Resource Intel + Validation | Repo intel pipeline, ingested repos (BlueTeam-Tools, awesome-claude-skills), validation 10-dim, vector search, **repo sync** | ✅ 5/5 |
| D. Memory + Lifecycle + Plugins | Memory 11-type, agent lifecycle, plugin store, **memory auto-promotion** | ✅ 4/4 |
| E. Continuous Learning | Learning loop, GPU fine-tune, local inference, **model registry, LoRA, training pipeline 2.0** | ✅ 6/6 |
| F. Intelligent Escalation | Context assembly, capability-gap, escalation, auto-merge, learn-from-cloud, provider chain | ✅ 6/6 |
| G. Knowledge Depth | Vector DB, knowledge graph, RAG doc-chat, vision feedback | ✅ 4/4 |
| H. UX + Apps | PWA, settings, automation center, desktop launcher, voice/video | ✅ 5/5 |
| I. Security | Auth, user mgmt, secret vault, audit, deep security scan | ✅ 5/5 |
| J. Independence | Offline model, autonomy, Docker | ✅ 3/3 |

**TOTAL: 52/52 · ~35 releases · 500+ files · $0**

**Run:** `python3 scripts/desktop_launcher.py` → `sujith / Richard-OS-2026`
**Container:** `docker compose up` (port 8001) · **Autonomy:** `python3 scripts/autonomy.py`
**Offline:** `python3 scripts/offline_model.py --train`
