# Build the desktop app (Tauri)
Requires: Rust + tauri-cli + webkit2gtk-4.1 (Linux) / MSVC (Windows)
```bash
# one-time
curl https://sh.rustup.rs -sSf | sh -s -- -y
cargo install tauri-cli --locked     # ~2-3 min
sudo apt install -y libwebkit2gtk-4.1-dev build-essential libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev

# build
cd src-tauri && cargo tauri build
# outputs: target/release/bundle/{deb,rpm,appimage}/Richard OS_*.{deb,rpm,AppImage}
The app spawns the Richard API server (port 8000) on launch, then opens the UI in a native window.
