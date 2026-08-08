#!/usr/bin/env python3
"""scripts/mobile_bridge.py - v6.5.0 Mobile Assistant: fake Android connector.
Simulates an Android device (state + actions) via the same fake-data-first
pattern as personal_agents. Swap in a real AccessibilityService later."""
import json, time, pathlib, random
DATA = pathlib.Path(__file__).resolve().parent.parent / "06-data"
STATE_FILE = DATA / "mobile_state.json"

def _now(): return time.strftime("%Y-%m-%d %H:%M:%S")

def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}

def _save(d):
    DATA.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(d, indent=2))
    return d

def default_state():
    return {
        "device": "Pixel 8 (fake)", "locked": False, "screen": True,
        "battery": random.randint(40, 100), "network": "wifi",
        "foreground": "launcher", "notifications": [],
        "apps": ["YouTube", "WhatsApp", "Gmail", "Chrome", "Maps", "Spotify"],
        "updated_at": _now(),
    }

def state():
    d = _load()
    if not d or not isinstance(d, dict) or "device" not in d:
        d = default_state(); _save(d)
    return d

def _set(**kw):
    d = state(); d.update(kw); d["updated_at"] = _now(); _save(d); return d

def open_app(app):
    d = _set(foreground=app, screen=True)
    return {"ok": True, "action": f"open_app {app}", "foreground": app}

def tap(x, y):
    d = _set(last_tap=[x, y])
    return {"ok": True, "action": f"tap {x},{y}"}

def swipe(x1, y1, x2, y2):
    d = _set(last_swipe=[x1, y1, x2, y2])
    return {"ok": True, "action": f"swipe ({x1},{y1})->({x2},{y2})"}

def type_text(text):
    d = _set(last_text=text)
    return {"ok": True, "action": f"type '{text}'"}

def press_back(): return _set(foreground="launcher") and {"ok": True, "action": "back"}
def press_home(): return _set(foreground="launcher") and {"ok": True, "action": "home"}

def take_screenshot():
    # fake: just log; real impl grabs a PNG via accessibility/MediaProjection
    return {"ok": True, "action": "screenshot", "note": "fake screenshot (real: MediaProjection)"}

def get_notifications(): return {"ok": True, "notifications": state().get("notifications", [])}

def set_locked(v): return _set(locked=bool(v))
