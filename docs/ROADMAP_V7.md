# v7 Roadmap — Distributed / Remote Richard OS

## Vision
Turn Richard from a single-machine assistant into a **coordinator of devices/fleets**:
Brain stays central; agents + tools execute on remote nodes; state syncs; voice works offline.

## Themes
### 1. Remote devices (multi-node)
- **Remote Mobile / Home / Desktop agents** over secure tunnels (ngrok/tailscale-ready)
- Each node runs a thin `richard-node` agent + registers to the Brain
- Commands like "open YouTube on my phone" already exist — extend to any registered device
- `RICHARD DEVICES` → node registry with status

### 2. Distributed knowledge + memory
- Sync `06-data/*.db` to a shared store (SQLite WAL / object store) across nodes
- Debated memory + knowledge graph converge; attention is `brain` zeroes on cluster of nodes

### 3. Remote Hub (marketplace 2.0)
- Hub already has a portable `index.json` — extend to **multi-repo registry + signatures + stars**
- `richard-hub publish/pull` from any GitHub repo (no single point)

### 4. Offline-first voice
- Local TTS + local STT (whisper.cpp / nerd-dictation) → "Hey Richard" works with NO internet
- Full pipeline in ONNX/web-rtc; wake stays local even when remote agents are off

### 5. Self-managing OS
- Autonomy daemon + scheduler already exist → add:
  - node health/standby (failover between local/remote agents)
  - cost guard on gateway (OmniRoute quota)
  - auto-learning from successful cloud calls (teacher loop already live)

## Milestones (v7.x)
- v7.1: remote node agent + command routing to LAN device
- v7.2: shared memory/knowledge sync
- v7.3: multi-repo hub + signatures
- v7.4: offline voice-first loop
- v7.5: cluster autonomy (health, failover, cost guard)

## Holding design rules
- Voice decides what user wants; Brain plans; Skills explain; Tools perform; device node executes; Brain verifies.
- Local/offline whenever possible (esp. voice wake + STT).
- Free-tier is dynamic — always refresh quotas before routing.
