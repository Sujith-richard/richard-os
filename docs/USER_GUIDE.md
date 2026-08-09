# 🧠 RICHARD OS

## Official User Guide

### Install · Configure · Connect · Create · Automate · Learn

Status legend: 🟢 **Available** · 🟡 **Partial** · 🔵 **Experimental** · 🟠 **Planned** · ⚪ **Optional** · 🔴 **Unavailable**

---

# PART I — GETTING STARTED

## 1. What Is Richard OS?

Richard OS is a self-hosted **AI operating environment**. It is not just a chatbot or a model wrapper: it coordinates the layers a task needs, and learns so the next task is better.

You interact with it through **conversation** (chat, voice, vision, document chat, terminal, API, desktop). Behind the conversation, Richard OS organizes five capability layers:

| Layer | Answers |
|---|---|
| **Models** | Who thinks? |
| **Skills** | How should the task be performed? |
| **Tools** | What can take action? |
| **Knowledge** | What information is available? |
| **Departments** | Who owns the work? |

Example user request:

> *"Build a full-stack fitness application."*

Richard OS: sends it to the **Brain** → context assembly → web department → frontend/backend subdepartments → skills → tools → model → execution → validation → result.

## 2. Richard OS at a Glance

```text
                    USER
                      │
                      ▼
              CONVERSATION (chat·voice·vision·doc-chat·API)
                      │
                      ▼
                RICHARD BRAIN
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     MODELS        SKILLS        KNOWLEDGE
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                    TOOLS · MCP · PLUGINS
                      │
                      ▼
                  DEPARTMENTS
                      │
                      ▼
              PROJECT / WORKFLOW
                      │
                      ▼
                   RESULT
                      │
                      ▼
                LEARNING → LOCAL MODEL
```

## 3. System Requirements

| | Minimum | Recommended | Local AI / LoRA (optional) |
|---|---|---|---|
| OS | Linux · Windows 10/11 | Ubuntu 24.04 | Linux |
| CPU | 2-core | 4+ core | 6+ core |
| RAM | 4 GB | 8 GB | 16 GB |
| GPU | — | — | NVIDIA RTX 3050 4GB+ (CUDA) |
| Disk | 2 GB free | 5 GB | + 5–10 GB weights |
| Python | 3.10 | 3.12 | 3.12 |
| Docker | — | 24.x | — |
| Browser | Chrome/Edge/Firefox | same | same |

Optional components: Node 22 (only if you run the OmniRoute gateway), CUDA-capable NVIDIA GPU, `espeak-ng` (offline TTS, `sudo apt install espeak-ng`).

## 4. Windows Installation

🟢 Today: **Python + uvicorn** (run the server → open browser) and a **3-stage wizard** (`install/windows/setup.cmd`):

```text
Download/clone
 → prerequisites (Python + Git for Windows)
 → install/start (run setup.cmd, or clone + pip)
 → configure .env
 → configure models
 → start (uvicorn or desktop_launcher)
 → open UI (http://127.0.0.1:8000/ui/)
 → login
```

- Inno Setup users: open `install/windows/RichardOS_Setup.iss` in Inno Setup → Compile → `Richard_OS_Setup.exe`.
- CI-built `.msi/.exe`: GitHub Actions → **Windows Desktop Build** → download artifacts (⚪).
- 🟠 Native packaged install (updater / service manager / tray) is planned, not present.

## 5. Linux Installation

🟢 Complete path (verified end-to-end):

```bash
# prerequisites
sudo apt update && sudo apt install -y git python3 python3-venv

# clone
git clone https://github.com/Sujith-richard/richard-os.git
cd richard-os

# environment + deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# config
cp .env.example .env        # DATA_MODE=fake by default
.venv/bin/python3 scripts/auth.py --setup sujith "Richard-YourOwn"

# start
nohup .venv/bin/python3 -m uvicorn scripts.server:app --host 127.0.0.1 --port 8000 &

# open UI
.venv/bin/python3 scripts/desktop_launcher.py

# verify
curl -s http://127.0.0.1:8000/agent-status
```

One-command installer (🟢):

```bash
curl -fsSL https://raw.githubusercontent.com/Sujith-richard/richard-os/main/install/linux/install.sh | bash
```

After install: `cd ~/richard-os && .venv/bin/python3 scripts/desktop_launcher.py`

## 6. Docker Installation

🟢 Containerized instance (verified on :8001 → host :8000):

```bash
docker build -t richard-os:latest .         # or use docker-compose
docker compose up -d                        # maps 8001:8000, volume 06-data, restart policy
docker logs -f richard-os
# UI at http://127.0.0.1:8001/ui/
```

Notes: the image installs deps at build; `06-data/` persists (volume); the `.dockerignore` keeps build context ~200 MB; GPU passthrough is 🟠 planned (use `--gpus all` with a custom compose when needed).

## 7. First Launch (kernel boot)

On start, `scripts/kernel.py` boots 10 subsystems in order:

```text
storage → memory → knowledge → skills → tools → departments
       → models → services → brain → conversation
```

Each step is logged to `06-data/kernel_boot.json` with retry-once on failure. You then see: **login** → **splash (black + logo)** → **Richard OS Studio** (sidebar + topbar).

---

# PART II — FIRST CONFIGURATION

## 8. First-Time Setup

| What | Where | Details |
|---|---|---|
| Create user | `scripts/auth.py --setup` (or POST /api/v1/auth/users) | pbkdf2-hashed, stored in `06-data/users.json` |
| Login | `/ui/login.html` | token in `richard_token` cookie |
| Fake vs real data | Settings → **Integration Mode** (toggle) | off = real connectors |
| Models | Chat/Models pages or `model_orchestrator` route table | local-first, then providers |
| Providers | `/api/v1/models/providers`, `-direct` gateway | DeepSeek on 127.0.0.1:1234 (Pool 2), OmniRoute on :20128 (Pool 3, optional) |
| Skills/Departments | `04-skills`, `02-blocks/*` | user-extensible |

## 9. Environment Variables

Only those actually used (example values — never real keys):

| Variable | Purpose | Required | Example |
|---|---|---|---|
| `DATA_MODE` | fake / real integration mode | yes | `fake` |
| `GMAIL_*` | gmail connector | no | `<you>@gmail.com`, `<app-password>` |
| `GITHUB_*` | repo intelligence | no | owner `Sujith-richard` |
| `OMNIROUTE_URL` / `OMNIROUTE_KEY` | optional gateway | no | `http://127.0.0.1:20128/v1` |
| `RICHARD_MASTER_KEY` | vault key | no | (base64) |
| `MODEL_DIR` | local model path | no | `06-data/models/` |

**Security:** never commit `.env`, `users.json`, `sessions.json`, `vault.json`, or API keys.

## 10. Security & Credentials

- 🟢 Login/logout/sessions (auth.py)
- 🟢 Vault (encrypted secrets, `vault.py` + `/api/v1/vault`)
- 🟢 Audit (audit.db), security scan (`security_scan.py`)
- 🟢 Change username/password (Settings → Credentials, requires current)

**Do not** commit secrets; use the vault; grant least privilege to connectors & MCP servers.


---

# PART III — USING RICHARD OS

## 11. Dashboard & Studio

Open `http://127.0.0.1:8000/ui/` (or `desktop_launcher.py`) and log in. You land on the **Richard OS Studio**: a sidebar of ~47 pages + a topbar (QUICK ADD, NOTIFY, THEME, scheduler LED, LISTENING/voice pill, CMD-K palette).

Key pages (all 🟢 exist):
Dashboard, Chat, Brain, Agents, Tasks, Skills, Approvals, Workflows, Execution, Validation, Lifecycle, Memory, Knowledge Graph, Plugins, Model Registry, Models, System, Settings, Automations, Collaboration, Organization, Departments, Personas, Life, Comms, Funnel, Finance, Social, Content, Integrations, Analytics, Roadmap, Repo Intel, Registry, Project Gen, Structures, Doc Chat, ML Box, Voice, Mobile, Home, Avatar, Hub, SDK …

Each is a real page; Dashboard shows the quick state, Chat is the primary conversation.

## 12. Chat

On Chat, type naturally:

> Build a full-stack fitness application.

The flow (server + brain):

```text
Chat → Brain → Context Assembly → Department (web) → Subdepartments
      → Skills → Knowledge → Model Orchestrator → Tool/Execution → Result
```

You don't need to pre-pick a department; the Brain routes.

## 13. Giving good instructions

Bad: `build app`  
Better: `Build a full-stack fitness application with user authentication, workout tracking, a dashboard, a REST API, and a SQLite database.`

Include: goal · requirements · technology · constraints · reference output · acceptance criteria.

## 14. Chat modes

| Mode | How | What it's for |
|---|---|---|
| Chat | text | general tasks |
| Voice | wake word + STT | hands-free commands |
| Vision | image path/prompt | image understanding (RAG + vision models) |
| Doc Chat | upload PDF/docs → RAG | ask your documents |
| Terminal | `desktop_launcher.py`/server | API & OS-level use |
| API | `/api/v1/*` | integrate other apps |

---

# PART IV — THE BRAIN

## 15. What the Brain is

The Brain is the coordinator. Engines in the repo (each 🟢): Planner, Task Assigner, Workflow, Context Assembly, Capability Gap, Escalation, Auto-Merge, Validation, Learning, Department Engine, Model Orchestrator, Security (auth/vault), Project Manager-oriented Project Engine, Knowledge Graph + Neural Communication (event bus + graph).

The local model lives in the **Model layer**, not the Brain; the Brain decides.

## 16. Context Assembly (14-source envelope)

Before a model replies, it gets a **context envelope**: department knowledge, skills, user memory, long-term memory, knowledge graph, repo intelligence, plugins, MCP, project structures, templates, standards, rules, previous projects, workflows.

```text
USER REQUEST
  ↓
CONTEXT ASSEMBLY (14 sources)
  ↓
UNIFIED CONTEXT ENVELOPE
  ↓
MODEL ORCHESTRATOR → MODEL
```

This prevents the model from "rediscovering" what the OS already knows.

---

# PART V — MODELS

## 17. Local vs cloud

- **Local**: Richard Local (LoRA-tuned/open weights), available offline (🟢 experimental quality from fine-tune, real GPU inference).
- **Cloud**: providers; each is an assistant, not a replacement.

## 18. Model Orchestrator (capability-aware)

```text
Task → Orchestrator → Local → can it? YES → go
             NO → capability gap → context → cloud (deepseek → gemini → groq → …) → merge → validate
```

Routable per domain: coding→deepseek · vision→gemini · speed→groq · reasoning→higher model · OmniRoute fallback (Pool 3).

## 19. Add/register a model

- Direct provider: write provider in `model_orchestrator` route table (or via `POST /api/v1/models/providers` if supported) with fields: provider · id · endpoint · key · context · vision · coding · reasoning · availability · priority.
- Registry page: promote/deploy/rollback local models (`model_registry.py` + `ui/models-registry.html`).
- OmniRoute (Pool 3, optional): point `omni_route.json` at the gateway; discovery returns live catalog.

## 20. Local model (running/training)

- Inference: `scripts/local_inference.py` (real CUDA; verify with `GET /api/v1/models/local/status`).
- Fine-tune: `training_pipeline.py` → `train_lora.py` → `model_registry` deploy → local model improves.
- **Important:** this improves the specialized behaviors in the training data; it does not magically match a frontier LLM.

## 21. OmniRoute (separate)

OmniRoute is an **optional external gateway** (Pool 3) — separate from your direct DeepSeek pool (Pool 2), which stays untouched. It aggregates many providers/free tiers for capability-awges routing when you need a wider pool.

---

# PART VI — SKILLS · KNOWLEDGE · TOOLS · MCP · PLUGINS

## 22. Skills

A skill = instructions for HOW to do something (≠ tool, ≠ model). Sources: internal `04-skills`, department skills `02-blocks/*/skills`, user skills (editable folders), external repos (Claude-style `awesome-claude-skills` real).

Install/enable: see `scripts/sdk.py new|validate|pack|publish` + `plugin_store.py` catalog; skills are markdown (e.g. `skill.md`, `examples.md`).

## 23. Knowledge

Teach Richard: PDF upload (Doc Chat + RAG → knowledge graph), GitHub repos (`repo_intel.py` → registry), notes, docs, prompts. Store: vector index (`vector_index.json`), memory db, knowledge graph db.

## 24. Tools & MCP

- Model decides · Skill explains · Tool acts (repo, git, docker, MCP, APIs, devices).
- MCP: bridge in `tools/mcp_bridge.py` + `mcp_tools.status()` (6 MCP servers: freecad-mcp, WebToApp, OmniCloud, map-to-poster, website-downloader …). Add your own MCP server → registry.

## 25. Plugins

Install/uninstall/tier from `plugins.db` + UI Plugin page; external repos appear as Community plugins after repo intel. Permissions = least privilege (review before enable).


---

# PART VII — DEPARTMENTS & PROJECTS

## 26. Departments

Departments are **ownership boundaries** (each with knowledge, skills, agents, prompts, templates, project-structures, rules, standards, git, mcp, plugins, tools, workflows, docs, examples, datasets, memory, training, evaluation, output-formats). Current: **web · ai · data · cyber · cloud · robotics · finance · hr** (+ subdepts: web→frontend/backend/db/api/auth/devops/testing/security/docs; ai→ml/llm/vision; data→engineering/analytics; cyber→offense/defense; cloud→infra/devops; robotics→embedded/autonomy; finance→accounting/treasury; hr→recruiting/people-ops). All spec-driven in `02-blocks/*.yaml`.

## 27. Project generation

```text
Requirement → department → subdepartments → structure → skills → knowledge
→ agents → models → files → test → security → validation → docs → package → deliver → learn
```

Use the **Project Generator** page (or `project_engine.py` API): pick blueprint (React/Next/Vue/FastAPI/Django/Express/… ) and it scaffolds the tree (e.g. frontend/ `public src components pages hooks context services utils routes store App.jsx main.jsx`; backend/ `config controllers models routes middleware services utils app.js server.js`).

Projects are **iterative**: plan → generate → test → observe gap → assign agent → fix → test → security → validate → repeat until pass.

## 28. Tasks & Workflows

- **Tasks**: `task_assigner.py` — assign me a task by keyword/role; status, retry, completion.
- **Workflows**: `workflow_engine.py` + `workflows.db` — trigger → tasks → agents → tools → validation → next.
- **Execution**: `execution_engine.py` — queue, dependencies, parallel groups, retries, progress %, done/error.

## 29. Memory

11-type system (`memory_system.py`): user / conversation / project / department / agent / tool / workflow / knowledge / experience / long-term / temporary. Lifecycle: memory_lifecycle promote temp→long-term by importance/age, TTL cleanup; view/search/manage on Memory page.

## 30. Knowledge Graph

`knowledge_graph.py` + UI (`kg.html`): nodes (user, department, agent, model, skill, tool, repos, project, task, workflow, memory, doc, dataset, device) and relations (USES, KNOWS, DEPENDS_ON, BELONGS_TO, EXECUTES, CREATED_BY, LEARNS_FROM, VALIDATES, ASSISTS, CONNECTED_TO). The **Brain graph** (avatar, 3D) renders these connections live.

---

# PART VIII — PERSONAL & EDGE ASSISTANTS

## 31. Personal Assistant node

`personal_agents.py` (+ calendar/email/tasks/notes hooks), live via Chat/voice. Enabled capabilities are those with connectors (Gmail etc.); others are ⚪ until configured.

## 32. Voice Assistant

- Mic → wake word ("hey richard") → STT (openai-whisper, local) → Brain → route (mobile/home/computer) → TTS (espeak-ng local, or cloud) → reply.
- Settings (Voice page): **Active Mic ON/OFF**, wake word, sensitivity, language, voice reply, target device, privacy.
- Examples (commands that work today): "hey richard turn on the bedroom light", "hey richard open youtube on my phone", "hey richard create a website".
- Respond by persona (jarvis/professional/…) via `persona_engine.py` (e.g. "The process has started, Sir.").

## 33. Mobile Assistant (as implemented)

- The repo has a real device registry + remote proxy (`device_registry.py`, `voice_engine._device_call`) — a registered phone URL receives the command (POST `<url>/api/v1/mobile/command`); if unreachable, falls back to local `mobile_agent.py`.
- Android AccessibilityService app (`android/`) is the on-device side; it taps/swipes/types; APK via GitHub Actions.
- You must unlock/aoothenticate on the phone for sensitive ops — **never bypass the lock screen**.

## 34. Home Assistant

`home_bridge.py` (simulated lights/ac/tv/camera/speaker/plug) + `home_agent.py` intents + `/api/v1/home/*`. Real-world home: connect a HomeAssistant/MQTT integration 🟠 PLANNED.

---

# PART IX — LEARNING, OFFLINE, SECURITY

## 35. Continuous learning

Cloud assist → capture useful interaction → clean/label/vectorize/evaluate → dataset → LoRA → registry → deploy → next local attempt is better. **Not automatic**: training is gated (quality, dedup, privacy review) and must be enabled.

## 36. Offline mode

Offline-available: local model (LoRA), local memory/knowledge/skills/tools (repo intel, vector), offline STT (whisper) + TTS (espeak-ng). Cloud-only (providers, OmniRoute, live integrations) require internet.

## 37. Security & monitoring

- Auth (users/sessions), vault (encrypted), audit, security scan (OWASP-patterns: secrets/unsafe code/injection/CORS…), permissions.
- Monitoring: `/api/v1/system/health`, `/metrics`, AI Runtime telemetry (`/api/v1/runtime/calls`), observability (`/api/v1/observability`), event bus (`/api/v1/events`), model registry, tasks, workflows.

---

# PART X — BACKUP, UPDATE, TROUBLESHOOTING

## 38. Backup

Copy `06-data/*.db`, `06-data/*.json`, `04-skills`, `02-blocks`, `docs/`, `repo_intel/`, model registry pointer — never secrets. Restore = stop, replace, restart, verify.

## 39. Update

`git pull` (backup first), `pip install -r requirements.txt`, restart server, verify (`verify_install.py`).

## 40. Troubleshooting

| Problem | Cause → Solution |
|---|---|
| won't start | missing uvicorn/deps → `.venv/bin/pip install -r requirements.txt` |
| port used | `ss -ltnp | grep 8000` → kill PID, restart |
| model unavailable | provider down/key → fallback; check `/api/v1/models/providers` |
| mic/TTS | `libportaudio` / espeak-ng / device select |
| mobile offline | device url unreachable → local fallback; enable accessibility app |
| home offline | device unavailable → "needs connection" |
| validation/security fail | open report → fix → re-run |

---

# PART XI — FAQ · GLOSSARY · QUICK REFERENCE

## 41. FAQ (selections)

- **What is Richard OS?** A self-hosted AI operating environment (models+skills+tools+knowledge+departments).
- **Works offline?** Partially — local model, memory, knowledge, TTS/STT work offline; cloud providers don't.
- **Can I use DeepSeek/Gemini/GPT?** Yes; configure providers; local-first orchestration.
- **100+ models?** Use OmniRoute gateway (Pool 3) for a large dynamic catalog (optional).
- **Can I run a local model?** Yes (`local_inference.py` + LoRA training pipeline).
- **Can it control my phone/home?** Phone: app + device-proxy (auth-bound). Home: simulated bridge + planned real MQTT.
- **Reads PDFs?** Yes — Doc Chat + RAG.
- **Learns from projects?** Yes (gated LoRA loop).
- **Where are projects?** `06-data/projects/` + project_engine.db.

## 41·2 Glossary

Agent · AI Runtime · Brain · Capability Gap · Context · Department · Knowledge · Knowledge Graph · Kernel · LLM · MCP · Memory · Model · Orchestrator · Plugin · Project · Skill · Tool · Workflow · LoRA · RAG · Repo Intel · STT · TTS · Wake Word · Local/Cloud model.

## 42. Quick Reference

```text
INSTALL   git clone; venv; pip install; cp .env; auth --setup
START     uvicorn scripts.server:app --port 8000  (or desktop_launcher)
LOGIN     http://127.0.0.1:8000/ui/ → user/pass
CHAT      Chat page, natural language
VOICE     Voice page → Active Mic ON → "hey richard …"
MODELS    Model Registry / models providers / OmniRoute option
SKILLS    04-skills + sdk publish
TOOLS     tools_config + MCP bridge + registry
KNOWLEDGE doc chat + repo_intel + memory
MEMORY    Memory page (11 types)
DEPARTMENTS 02-blocks/*.yaml
PROJECTS  Project Generator page
AGENTS    agent_runtime registry
WORKFLOWS workflows + execution engine
VALIDATION validation page
SECURITY  auth/vault/scan
LEARNING  learn_from_cloud → pipeline → LoRA → registry → deploy
OFFLINE    local inference + local TTS/STT
BACKUP    06-data + skills + docs
UPDATE     git pull + pip + restart + verify
```

---

*This guide is maintained to match the repository at v7.6.x. Anything not present in the code is marked 🟠/🔴 and never implied as working. For architecture see README; for deep developer flows see docs/ (TAURI_BUILD.md, WINDOWS_BUILD.md, ANDROID_BUILD.md, PORTFOLIO.md, ROADMAP_V7.md).*
