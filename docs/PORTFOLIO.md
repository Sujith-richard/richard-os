# Richard OS — Portfolio / Demo Notes

## One-liner
A personal AI operating system: 5-product platform (Core · Engine · Studio · SDK · Hub) + external gateway (OmniRoute) + native Studio (Tauri) + multi-device agents (Computer / Mobile / Home) + active voice (JARVIS-style persona).

## The build (82/52 roadmap items + 7 v5 gaps + v6 line)
- **52/52** phase plan (Phases A–J) + **8 v4 arch** + **7 v5 platform gaps** (v5.1 Runtime … v5.7 managers)
- **5 products** (the VS Code/Docker scaling shape)
- **46–48 Studio pages**, **198+ API endpoints**, 6 systems of record
- **OmniRoute Pool #3** — 281-model keyless `auto`, capability routing, learn-from-teacher loop
- **3D AI Avatar** — full-sphere neural core (icons, drag, zoom, hover, path glow)
- **Mobile + Home agents** — device state, commands, Observe→Act→Verify, active-path glow
- **Voice + Persona** — wake-first local, master switch, JARVIS-style responses
- **Hub 2.0** — marketplace with featured official packages + live health
- **Tauri native Studio** scaffold — `cargo tauri dev` for a desktop window

## Numbers
- tags: v1.0.0 → v6.9.0 (28+)
- pages: 48 · endpoints: 198+ · hub packages: 27 (6 featured) · free, MIT, $0

## The 3-pool model
Local (P1) → DeepSeek direct (P2) → OmniRoute (P3) → learn → Local v2

## The extension loop
richard-sdk new → validate → pack → publish → hub pull → install

## Story for a demo video
1. Boot Richard OS → shell (sidebar, hub/sdk/avatar/mobile/home/voice in nav)
2. Brain graph (2D + 3D avatar, drag/zoom, active-path glow)
3. Submit a voice command → wake → route → execute → persona reply
4. Hub 2.0 → official featured packages + live marketplace
5. Studio in a native window (Tauri).

## Try it
```bash
git clone https://github.com/Sujith-richard/richard-os.git
cd richard-os
python3 scripts/desktop_launcher.py   # starts server + opens UI
# or: cargo tauri dev (native window)
