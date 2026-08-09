
---

## 🧠 04 · Studio UI · Deployment · Runtime

### Studio (🟢, ~47 pages)
Chat · Brain · Agents · Tasks · Skills · Approvals · Workflows · Execution · Validation · Lifecycle · Memory · Knowledge Graph · Plugins · Model Registry · System · Settings · Automations · Integrations · Repo Intel · Registry · Structures · Project Gen · Doc Chat · ML · Voice · Mobile · Home · Avatar (3D) · Hub · SDK …

### Deployment (🟢)
- Host: `uvicorn scripts.server:app --port 8000`
- Docker: `docker compose up` (:8001→8000, volume 06-data)
- Desktop launcher: `scripts/desktop_launcher.py` (browser) · `native_launcher.py` (pywebview → Tauri)
- Tauri `.deb/.rpm/.AppImage` build (linux) · Windows .msi/.exe via Actions
- Installers: `install/linux/install.sh` (one-command) · `install/windows/setup.cmd` (3-stage) · Inno `.iss`

### Runtime instances
- Host :8000 (FastAPI + uvicorn)
- Container :8001
- Autonomy daemon (`autonomy.py`) health checks + self-heal (NOT unsupervised decision-making)
- kernel_boot.json for boot state

---
