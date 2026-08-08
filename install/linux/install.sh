#!/usr/bin/env bash
# Richard OS — Linux one-command installer
# Usage:  curl -fsSL https://raw.githubusercontent.com/Sujith-richard/richard-os/main/install/linux/install.sh | bash
set -e
echo "== Richard OS — Linux install =="
DEST="${HOME}/richard-os"
echo "[1/4] License accepted (MIT)."
echo "[2/4] Install location: ${DEST}"
[ -d "$DEST" ] || git clone --depth 1 https://github.com/Sujith-richard/richard-os.git "$DEST"
cd "$DEST"
echo "[3/4] Installing deps + venv..."
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --quiet -r requirements.txt 2>/dev/null || echo "(no requirements.txt — optional runtime deps)"
echo "[4/4] Verifying installation..."
.venv/bin/python3 scripts/verify_install.py
echo "== Done. Run:  cd $DEST && .venv/bin/python3 scripts/desktop_launcher.py"
