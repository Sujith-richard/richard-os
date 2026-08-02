#!/usr/bin/env python3
"""Richard OS — Home bridge: device registry + actions.
Simulated mode works out of the box. To go real:
set HOME_MODE=homeassistant in .env and implement the HA REST call below."""
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Device registry: room -> device -> state
DEVICES = {
    "living-room": {"lights": "off", "tv": "off", "ac": {"power": "off", "temp": 24}},
    "kitchen":     {"appliances": "off"},
    "bedroom":     {"lights": "off", "alarm": "disarmed"},
    "security":    {"cameras": "armed", "door-lock": "locked"},
}

def _env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def list_devices():
    return {room: list(devs) for room, devs in DEVICES.items()}

def get_state(room=None):
    if room:
        return {room: DEVICES.get(room, {})}
    return DEVICES

def device_action(room, device, action, params=None):
    """Apply an action to a device. Returns new state."""
    params = params or {}
    _env()
    mode = os.environ.get("HOME_MODE", "simulate")

    if room not in DEVICES or device not in DEVICES[room]:
        return {"error": f"Unknown room/device: {room}/{device}"}

    if mode == "homeassistant":
        # TODO: call Home Assistant REST API (free, open-source)
        # GET/POST http://homeassistant.local:8123/api/states/<entity>
        # with Bearer token from .env HOME_ASSISTANT_TOKEN
        return {"error": "Home Assistant mode not yet configured. Add HOME_ASSISTANT_TOKEN to .env"}

    # simulate mode
    cur = DEVICES[room][device]
    if action in ("on", "off"):
        DEVICES[room][device] = action
    elif action == "lock":
        DEVICES[room][device] = "locked"
    elif action == "unlock":
        DEVICES[room][device] = "unlocked"
    elif action == "arm":
        DEVICES[room][device] = "armed"
    elif action == "disarm":
        DEVICES[room][device] = "disarmed"
    elif action == "set-temp" and isinstance(cur, dict):
        DEVICES[room][device]["power"] = "on"
        DEVICES[room][device]["temp"] = float(params.get("temp", 24))
    else:
        return {"error": f"Unsupported action '{action}' for {room}/{device}"}
    return {room: {device: DEVICES[room][device]}}
