#!/usr/bin/env python3
"""scripts/cluster.py - v7.4 Cluster monitor / self-managing.
Watches registered devices (devices.json), reports status, supports failover."""
import json, pathlib, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "06-data" / "devices.json"

def _load():
    try:
        if FILE.exists():
            return json.loads(FILE.read_text())
    except Exception:
        return {}
    return {}

def _reachable(device, timeout=6):
    url = device.get("url")
    if not url:
        return True
    try:
        req = urllib.request.Request(url.rstrip("/") + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False

def health():
    devs = _load().get("devices", [])
    out = []
    for dev in devs:
        ok = _reachable(dev)
        out.append({**dev, "online": ok, "last_check": time.strftime("%Y-%m-%d %H:%M:%S")})
    _save({"devices": out})
    online = [d for d in out if d.get("online")]
    return {"ok": True, "nodes": len(out), "online": len(online),
            "degraded": [d.get("name") for d in out if not d.get("online")],
            "devices": out}

def failover(kind):
    devs = _load().get("devices", [])
    for d in devs:
        if d.get("kind") == kind and _reachable(d):
            return {"ok": True, "device": d.get("name"), "url": d.get("url"), "kind": kind}
    for d in devs:
        if _reachable(d):
            return {"ok": True, "device": d.get("name"), "url": d.get("url"), "note": "fallback"}
    return {"ok": False, "error": "no reachable node for kind " + kind}
