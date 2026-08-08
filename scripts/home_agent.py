#!/usr/bin/env python3
"""scripts/home_agent.py - v6.6.0 Home Assistant agent.
Understands simple home commands: lights, AC, TV, speaker, status."""
import sys, time, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from home_bridge import state, toggle, set_temp, set_level

def run(request):
    r = request.lower()
    log = []
    def step(m): log.append("[" + time.strftime("%H:%M:%S") + "] " + m)
    step("intent: " + request[:40])
    dev = None
    for k in ("light", "ac", "tv", "camera", "speaker", "plug"):
        if k in r: dev = k; break
    if dev:
        if "off" in r: toggle(dev); step("act: " + dev + " off")
        else: toggle(dev); step("act: " + dev + " on")
    elif "temp" in r or "degree" in r or "cool" in r:
        try:
            t = int(r.split("degree")[0].split()[-1]) if "degree" in r else 24
        except Exception:
            t = 24
        set_temp(t); step("act: ac temp -> " + str(t))
    elif "level" in r or "brightness" in r:
        lvl = 60; set_level(lvl); step("act: lights level -> " + str(lvl))
    else:
        step("status: all devices reported")
    st = state()
    _path(["core", "personal-assistant", "smart-home", (dev or "status")])
    return {"ok": True, "devices": st["devices"], "log": log, "intent": dev or "status"}

def _path(p):
    try:
        import json as _j
        f = ROOT / "06-data" / "active_path.json"
        f.write_text(_j.dumps({"path": p, "at": time.strftime("%Y-%m-%d %H:%M:%S")}))
    except Exception:
        pass
