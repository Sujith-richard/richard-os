# Build a Windows setup.exe (Inno Setup)

## Method 1 — Inno Setup script (recommended)
1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php) on Windows.
2. Copy `install/windows/setup.cmd` to the repo root on Windows.
3. Run it (it's the **3-stage wizard**: license agree, install location, optional desktop/start-menu icons + perms, then auto-verify via `scripts/verify_install.py`).
4. For a single-file installer: inside Inno Setup open/edit `install/windows/RichardOS_Setup.iss` and press **Build → Compile** -> produces `output/Richard_OS_Setup.exe`.

## Method 2 — Tauri (the modern app, already built for Linux)
- We already produced `.deb/.rpm/.AppImage` on Linux via `cargo tauri build`.
- On Windows, same project (`src-tauri/`) builds `.msi`/`.exe` with: `cargo tauri build` (needs MSVC webview2 already present on Win10/11).

## What the installer does
- STAGE 1: Terms & conditions agree.
- STAGE 2: install location + desktop/start-menu shortcut + optional permissions (changeable later in Settings).
- STAGE 3: copy files, run `scripts/verify_install.py` (auto-checks all modules/files), download/emit user guide.
- Post: run desktop_launcher.py (starts server + opens UI) or the Tauri exe.


## Method 3 — GitHub Actions (no Windows box needed) ⭐
Push a tag `v*` and the workflow `.github/workflows/windows-build.yml` builds
`.msi` + `.exe` on a Windows runner and uploads them as artifacts:
  Repository → Actions → "Windows Desktop Build" → run
  Artifacts: richard-os-windows (msi) + richard-os-windows-exe (nsis exe)
