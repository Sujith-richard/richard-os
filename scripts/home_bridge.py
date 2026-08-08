#!/usr/bin/env python3
"""scripts/home_bridge.py - v6.6.0 Home Assistant: fake IoT devices.
Simulates smart-home device state + actions. Real HomeAssistant/MQTT later."""
import json, time, pathlib, random
DATA = pathlib.Path(__file__).resolve().parent.parent / "06-data"
FILE = DATA / "home_state.json"

def _now(): return time.strftime("%Y-%m-%d %H:%M:%S")

def _load():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text())
        except Exception:
            pass
    return {}

def _save(d):
    DATA.mkdir(exist_ok=True); FILE.write_text(json.dumps(d, indent=2)); return d

def default():
    return {"hub": "smart-home (fake)", "devices": {
        "lights": {"on": True, "level": 70},
        "ac": {"on": False, "temp": 24},
        "tv": {"on": False, "channel": 1},
        "camera": {"on": True},
        "speaker": {"on": False},
        "plug": {"on": True},
    }, "updated_at": _now()}

def state():
    d = _load()
    if not d or "devices" not in d:
        d = default(); _save(d)
    return d

def _set(key, **kw):
    d = state(); d["devices"].setdefault(key, {}); d["devices"][key].update(kw); d["updated_at"] = _now(); _save(d); return d

def toggle(key): return _set(key, on=not state()["devices"].get(key, {}).get("on", False))

def set_temp(t): return _set("ac", temp=int(t))
def set_level(l): return _set("lights", level=int(l))
