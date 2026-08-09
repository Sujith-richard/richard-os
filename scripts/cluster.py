#!/usr/bin/env python3
"""scripts/cluster.py - v7.4 Cluster monitor / self-managing.
Watches registered devices (devices.json), reports status, supports failover
(if the primary node for a kind is down, pick the next reachable)."""
import json, pathlib, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "06-data" / "devices.json"
def _load():
    try:
        if FILE.exists():
            return json.loads(FILE.read_text())
    except Exception:
        pass
    return {}
def _save(d):
    FILE.parent.mkdir(exist_ok=True); FILE.write_text(json.dumps(d, indent=2))

def _reachable(dev, timeout=3):
    url = dev.get("url")
    if not url:
        return True  # local node is always "up"
    try:
        req = urllib.request.Request(url.rstrip("/") + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False

def status():
    d = _load().get("devices", [])
    out = []
    for dev in d:
        ok = _reachable(dev)
        dev["online"] = ok
        dev["last_check"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out.append(dev)
    _save({"devices": out})
    healthy = [d for d in out if d.get("online")]
    return {"ok": True, "nodes": len(out), "online": len(healthy),
            "degraded": [d.get("name") for d in out if not d.get("online")],
            "devices": out}

def failover(kind):
    devs = _load().get("devices", [])
    candidates = [d for d in devs if d.get("kind") == kind]
    for d in candidates:
        if _reachable(d):
            return {"device": d.get("name"), "url": d.get("url"), "ok": True}
    for d in devs:
        if _reachable(d):
            return {"device": d.get("name"), "url": d.get("url"), "ok": True, "note": "primary down, using fallback"}
    return {"ok": False, "error": "no reachable node for kind " + kind}
