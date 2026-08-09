
---

## 🧺 05 · Status matrix (source-true at v8.1)

| Feature | Status | Implementation |
|---|---|---|
| Kernel boot | 🟢 | scripts/kernel.py |
| Departments + 20-spine | 🟢 | 02-blocks yaml |
| Agents (30) + lifecycle | 🟢 | agent_runtime.py |
| Skills | 🟢 | 04-skills |
| Memory 11-type | 🟢 | memory_system.py |
| Knowledge graph | 🟢 | knowledge_graph.py |
| Vector/RAG | 🟢 | docchat, vector_db |
| Tools/MCP | 🟢 | tools bridge |
| Plugins | 🟢 | plugins.db |
| Model orchestration | 🟢 | model_orchestrator |
| Local inference | 🟢 | local_inference.py |
| LoRA training | 🟢 | train_lora.py |
| Learning | 🟢 | learn_from_local.py / training_pipeline |
| Validation 10-dim | 🟢 | validation_engine.py |
| Security (auth/vault/audit/scan) | 🟢 | auth/vault/audit/security_scan |
| Project engine (+12 blueprints) | 🟢 | project_engine.py |
| Execution engine | 🟢 | execution_engine.py |
| Voice (active-listen + TTS/STT) | 🟢 | voice_engine.py |
| Mobile agent | 🟡 | device_registry + proxy; phone app (android) |
| Home assistant | 🟡→🟢 | home_bridge.py (sim) + plans |
| OmniRoute gateway | ⚪ optional | omni_route.py (external) |
| Fooocus image-gen | ⚪ optional | image_gen.py bridge |
| Keycloak IdP | ⚪ optional | integrations keycloak |
| Tauri desktop | 🟢 linux / 🟡 windows CI | src-tauri |
| Docker image | 🟢 | Dockerfile/compose |
| Modeling as “real” GPU training | 🟡 experimental | RTX LoRA tiny |

## Examples & data flow

- Example (voice): “Hey Richard, turn on the living room light.” → wake → Brain → Home Assistant → Tool → device → verify → voice.
- Example (project): “Build a fitness app” → Brain → Web Dept → frontend/backend → skills → models → execution → validation → security → deliver.

## Roadmap (🟠 PLANNED, from docs/ROADMAP_V7.md)
v7.x remote nodes · offline-first (STT/TTS local) · multi-repo hub signatures (partial live) · cluster/self-managing (partial) · v8 native mobile (Flutter shell, in progress) · v9 deep training.
