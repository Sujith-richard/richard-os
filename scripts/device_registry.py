#!/usr/bin/env python3
"""scripts/device_registry.py - v7.1 Device/node registry.
Registers devices (computer / mobile / home / remote node); commands route to the right device."""
import json, pathlib, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "06-data" / "devices.json"
def _now(): return time.strftime("%Y-%m-%d %H:%M:%S")
def _load():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text())
        except Exception:
            return {}
    return {}
def _save(d):
    FILE.parent.mkdir(exist_ok=True); FILE.write_text(json.dumps(d, indent=2)); return d
def default_device():
    return {"id": "computer", "name": "this pc", "kind": "computer", "url": None, "reachable": True, "registered": _now()}
def list_devices():
    d = _load()
    if "devices" not in d:
        d = {"devices": [default_device()]}; _save(d)
    return {"ok": True, "devices": d["devices"]}
def register(name, kind="mobile", url=None):
    d = _load(); devs = d.get("devices", [default_device()])
    for dev in devs:
        if dev.get("name", "").lower() == str(name).lower():
            dev.update({"kind": kind, "url": url, "registered": _now()}); break
    else:
        devs.append({"id": str(name).lower().replace(" ", "-"), "name": name, "kind": kind, "url": url, "registered": _now()})
    d["devices"] = devs; _save(d)
    return {"ok": True, "devices": devs}
def route(kind):
    devs = _load().get("devices", [default_device()])
    for dev in devs:
        if dev.get("kind") == kind:
            return dev
    for dev in devs:
        if dev.get("url"):
            return dev
    return devs[0] if devs else default_device()
def ping(url):
    return {"device": "remote", "url": url, "reachable": True}   # thin stub — real ping via httpx later
