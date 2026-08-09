#!/usr/bin/env bash
# Richard OS — 60-second demo tour (boot server, show the OS, run a command)
set -e
PORT=8000
URL="http://127.0.0.1:$PORT/ui/"
echo "╔══════════════════════════════════════════════╗"
echo "║  RICHARD OS — 60-second demo                 ║"
echo "╚══════════════════════════════════════════════╝"
# 1) server
if curl -s -o /dev/null "http://127.0.0.1:$PORT/ui/"; then
  echo "[boot] server already up"
else
  echo "[boot] starting Richard..."
  (.venv/bin/python3 -m uvicorn scripts.server:app --port "$PORT" >/tmp/richard-demo.log 2>&1 &)
  for i in $(seq 1 20); do sleep 0.5; curl -s -o /dev/null "http://127.0.0.1:$PORT/ui/" && break; done
fi
echo "[open] $URL"
xdg-open "$URL" 2>/dev/null || open "$URL" 2>/dev/null || true
# 2) quick pulse
echo "[splash] logo + neural avatar (splash plays once)"
# 3) demo route — home command, persona reply (offline voice)
echo "[voice] 'hey richard, turn on the bedroom light'"
.venv/bin/python3 - <<'PY'
import sys; sys.path.insert(0, "scripts")
from voice_engine import set as vs, command
vs(True)
r = command("hey richard turn on the bedroom light")
print("  route:", r["route"], "| reply:", r["reply"])
print("  log:", "; ".join(r["log"][-3:]))
PY
# 4) stats
echo "[stats] hub + cluster"
curl -s "http://127.0.0.1:$PORT/api/v1/hub/stats"
echo ""
curl -s "http://127.0.0.1:$PORT/api/v1/cluster/health"
echo ""
echo "Done. Press Enter to close."
read -r
