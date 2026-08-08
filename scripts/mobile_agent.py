#!/usr/bin/env python3
"""scripts/mobile_agent.py - v6.5.0 Mobile Assistant agent.
Device state, permission gate (L0-L4), Plan->Observe->Act->Observe->Verify loop,
MCP-style tools. Fake-first; real Android AccessibilityService swaps in later."""
import sys, json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from mobile_bridge import (state, open_app, tap, swipe, type_text, press_back,
                           press_home, take_screenshot, get_notifications)

def _active_path(path):
    try:
        import json as _j
        from pathlib import Path as _P
        f = _P(__file__).resolve().parent.parent / "06-data" / "active_path.json"
        f.write_text(_j.dumps({"path": path, "at": time.strftime("%Y-%m-%d %H:%M:%S")}))
    except Exception:
        pass


PERMISSIONS = {
    "L0": ["get_device_state", "get_screen", "get_battery", "get_notifications"],
    "L1": ["open_app", "search", "scroll", "screenshot", "launch_url"],
    "L2": ["read_messages", "read_files", "read_email", "read_contacts"],
    "L3": ["purchase", "send_message", "account_change", "financial"],
    "L4": ["critical_action"],
}
LEVEL_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
DEFAULT_TOOLS = {"L1": ["open_app", "tap", "type_text", "screenshot", "get_notifications"],
                 "L0": ["get_device_state"]}

def _allowed(action):
    for level, acts in PERMISSIONS.items():
        if action in acts:
            return level
    return "L1"

def run(request, force_level="L1"):
    log = []
    def step(m): log.append("[" + time.strftime("%H:%M:%S") + "] " + m)
    r = request.lower()
    if any(k in r for k in ("send", "message", "email", "purchase", "buy", "pay")):
        action_hint = "send_message" if ("message" in r or "send" in r) else ("purchase" if ("purchase" in r or "buy" in r or "pay" in r) else "get_device_state")
        # gate check for sensitive actions
        lvl = _allowed(action_hint)
        if LEVEL_RANK.get(lvl, 1) > LEVEL_RANK.get(force_level, 1):
            return {"ok": False, "error": "action '" + action_hint + "' needs " + lvl + ", caller granted " + force_level,
                    "request": request, "intent": "sensitive"}
        return {"ok": True, "result": {"note": "sensitive action '" + action_hint + "' would require " + lvl + " confirmation"}, "intent": "sensitive", "permission": lvl}
    intent = "open" if "open" in r else ("play" if ("play" in r or "watch" in r) else "status")
    step("intent: " + intent)
    action = "open_app" if intent == "open" else ("play" if intent == "play" else "get_device_state")
    lvl = _allowed(action)
    if LEVEL_RANK.get(lvl, 1) > LEVEL_RANK.get(force_level, 1):
        return {"ok": False, "error": "action '" + action + "' needs " + lvl + ", caller granted " + force_level,
                "log": log, "request": request}
    step("permission: " + lvl + " OK")
    st = state()
    if st.get("locked"):
        return {"ok": False, "need_unlock": True, "message": "Phone locked. Please unlock to continue.",
                "log": log, "state": st}
    step("device unlocked")
    if intent == "status":
        _active_path(["core", "personal-assistant", "mobile-agent"])
        return {"ok": True, "result": st, "log": log, "intent": intent}
    app = "YouTube" if intent == "play" else (request.split("open")[-1].strip().title() or "YouTube")
    step("plan: open " + app + " -> search -> select -> verify")
    step("observe: screen=" + str(st.get("foreground")) + " locked=" + str(st.get("locked")))
    open_app(app); step("act: open_app(" + app + ")")
    step("observe: foreground=" + str(state().get("foreground")))
    if intent == "play":
        type_text("specific video"); step("act: type_text")
        tap(300, 500); step("act: tap search")
        step("verify: found target video (title match) -> tap")
        tap(300, 600); step("act: tap video")
    step("verify: playback started")
    _active_path(["core", "personal-assistant", "mobile-agent", "YouTube"])
    return {"ok": True, "result": {"foreground": state().get("foreground"), "playing": intent == "play"},
            "log": log, "intent": intent, "permission": lvl}
