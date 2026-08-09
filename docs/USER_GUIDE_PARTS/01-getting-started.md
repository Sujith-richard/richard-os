# 🧠 RICHARD OS

## Official User Guide

### Install · Configure · Connect · Create · Automate · Learn

Status legend used throughout: 🟢 Available · 🟡 Partial · 🔵 Experimental · 🟠 Planned · ⚪ Optional · 🔴 Unavailable.

---

## 3 · 5-Minute Quick Start

```bash
# 1. Prerequisites: Python 3.12, git (Linux); any modern browser.
git clone https://github.com/Sujith-richard/richard-os.git
cd richard-os

# 2. Environment + deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Configure .env (copy example if present)
cp .env.example .env   # set DATA_MODE=fake, add keys later

# 4. Start the OS server (FastAPI on :8000)
.venv/bin/python3 -m uvicorn scripts.server:app --host 127.0.0.1 --port 8000

# 5. Open the Studio
#    browser: http://127.0.0.1:8000/ui/
#    or desktop-style launcher:
.venv/bin/python3 scripts/desktop_launcher.py

# 6. Login (first-run user)
#    username/password set via  scripts/auth.py --setup
.venv/bin/python3 scripts/auth.py --setup sujith "Richard-OS-2026"

# 7. Send your first message: open Chat, type anything.
# 8. Create a first project from the Dashboard / Project generator.
```

One-command install (Linux) 🟢:

```bash
curl -fsSL https://raw.githubusercontent.com/Sujith-richard/richard-os/main/install/linux/install.sh | bash
```

---

## 4 · What Richard OS is (user view)

Richard OS is an **AI operating environment**: the Brain plans, models think, skills explain, tools act, knowledge informs, departments own, agents execute, and learning improves the local model over time.

```text
YOU → RICHARD OS → BRAIN → MODELS + SKILLS + TOOLS + KNOWLEDGE + DEPARTMENTS → RESULT
```

| Layer | Says |
|---|---|
| Models | who thinks |
| Skills | how the task is done |
| Tools | what can take real action |
| Knowledge | what we know |
| Departments | who owns the work |
| Agents | who executes |
| Memory | what we remember |
| Workflow/Execution | how steps run |
| Learning | how we get better |

---

## 5 · First launch

On boot, the Kernel initializes 10 subsystems in order (🟢 verified in `scripts/kernel.py`):

```text
storage → memory → knowledge → skills → tools → departments → models
        → services → brain → conversation
```

You will see: the login page, then the **Richard OS Studio** (shell with sidebar + topbar), then a **splash** (black + logo) once per session.

First-run configuration: create your user, set DATA_MODE (fake for demo / real later), optionally configure models (DeepSeek local gateway on 127.0.0.1:1234 or point to providers), and review Settings.

---

## 6 · System requirements (from the repo, not invented)

| | Minimum | Recommended | Local AI / GPU (optional) |
|---|---|---|---|
| CPU | 2-core | 4+ core | 6+ core |
| RAM | 4 GB | 8 GB | 16 GB |
| GPU | — | — | NVIDIA RTX 3050 4GB+ (works with train_lora.py + local_inference.py) |
| Disk | 2 GB | 5 GB | + 10 GB models/weights |
| Python | 3.10 | 3.12 | 3.12 |
| Docker | — | 24.x (for :8001 container, `docker compose up`) | — |
| Node | — | 22 (only for OmniRoute/UI tooling) | only if running that gateway |

---

## 7 · Supported OS (actual)

- 🟢 **Linux** (Ubuntu 24.04 used for dev) — full runtime, install.sh, systemd-style service concept, Tauri .deb/.rpm/.AppImage built.
- 🟢 **Windows** — Python + uvicorn runtime; `install/windows/setup.cmd` 3-stage installer; Inno Setup `.iss` for a single `Richard_OS_Setup.exe`; Tauri .msi/.exe via GitHub Actions.
- 🟢 **Docker** — Dockerfile + docker-compose map `8001:8000`; container instance verified.
- 🟠 Native packaged apps on mobile — Android accessibility app scaffold + APK CI exist (⚪) — control requires installing it on a phone.

---

## 8 · Install — Linux (detailed) 🟢

```bash
# 1) system prep (Ubuntu)
sudo apt update && sudo apt install -y git python3 python3-venv

# 2) clone
git clone https://github.com/Sujith-richard/richard-os.git && cd richard-os

# 3) venv
python3 -m venv .venv && source .venv/bin/activate

# 4) deps
pip install -r requirements.txt

# 5) env
cp .env.example .env   # DATA_MODE=fake by default

# 6) bootstrap admin user
.venv/bin/python3 scripts/auth.py --setup sujith "Richard-YourOwn"


# 7) start server
nohup .venv/bin/python3 -m uvicorn scripts.server:app --host 127.0.0.1 --port 8000 &

# 8) UI
.venv/bin/python3 scripts/desktop_launcher.py     # opens browser
open http://127.0.0.1:8000/ui/

# 9) verify: open the login, land on Dashboard; Chat works; ‘agent-status’ 200:
curl -s http://127.0.0.1:8000/agent-status
```

Troubleshooting (Linux): see §62.

---

## 9 · Install — Windows

🟢 Python way (today):
- Install Python 3.11+ (Add to PATH), then Git for Windows.
- Run `install/windows/setup.cmd` (it is a 3-stage: license agree → location + desktop/start-menu shortcuts + optional permissions → copies files, runs `scripts/verify_install.py`, and offers user guide).
- Open a terminal in the installed folder, create venv, `pip install -r requirements.txt`, then `.\\.venv\\Scripts\\python.exe scripts\\desktop_launcher.py`.

🟠 Future: native installer architecture (Installer → Core → Services → Models → DB → UI → Voice → Tools) — planned, not claimed.

---

## 9 · Install — Windows (packaged)

- Inno: open `install/windows/RichardOS_Setup.iss` in Inno Setup → Compile → `Richard_OS_Setup.exe`.
- Or GitHub Actions → “Windows Desktop Build” → download `.msi`/`.exe` (⚪ building that you want).
- Planned-only items (updater, service manager, tray, diagnostics) are 🟠.

---

## 10 · Docker

```bash
docker build -t richard-os:latest .
docker compose up -d     # maps 8001:8000, volume for 06-data, restart
docker logs -f richard-os
# UI at http://127.0.0.1:8001/ui/
```

Inside the container: python:3.12-slim, uvicorn on 0.0.0.0:8000. GPU not pass-through by default (see §50). Persist `06-data/` with the compose volume. 🟢 verified.

Note: `.dockerignore` excludes `.venv/vendor/data/git` → context ~200 MB, image small.

---

## 11 · Environment variables (actual, example values — never real keys)

| Variable | Purpose | Required | Example | Sensitive |
| DATA_MODE | fake/real integration mode | yes | fake | no |
| GMAIL_USER / GMAIL_APP_PASSWORD | Gmail connector | no | you@gmail.com | yes |
| GITHUB_OWNER / REPO / TOKEN | GitHub intelligence | no | Sujith-richard | token yes |
| OMNIROUTE_URL / API_KEY | OmniRoute gateway | no | http://127.0 | key yes |
| RICHARD_MASTER_KEY / SEC | Vault key | no | (base64) | yes |

Never commit secrets; use `06-data/vault.json` (encrypted) for app secrets.

(… continues §12–§97) …
