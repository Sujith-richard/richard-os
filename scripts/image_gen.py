#!/usr/bin/env python3
"""scripts/image_gen.py - v7.6 Fooocus image-generation bridge.
Calls Fooocus's local API (http://127.0.0.1:7865) when running; else reports
needs-fooocus honestly. Enables 'generate an image' tasks with the image-gen model."""
import json, pathlib, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = ROOT / "06-data" / "image_gen.json"
DEFAULT = {"enabled": False, "url": "http://127.0.0.1:7865"}
def _load():
    try:
        if CFG.exists(): return {**DEFAULT, **json.loads(CFG.read_text())}
    except Exception: return dict(DEFAULT)
    return dict(DEFAULT)
def status():
    c = _load()
    return {"ok": True, "name": "Fooocus", "enabled": c.get("enabled"), "url": c.get("url"),
            "needs": "GPU + SDXL weights (run: cd vendor/Fooocus && python entry_with_update.py)"}
def generate(prompt, size="1152x896"):
    c = _load()
    if not c.get("enabled"):
        return {"ok": False, "error": "Fooocus not enabled — set 06-data/image_gen.json enabled=true when running"}
    try:
        import urllib.request
        req = urllib.request.Request(c["url"].rstrip("/") + "/generate", data=json.dumps({"prompt": prompt, "size": size}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read())
            return {"ok": True, "image": d.get("image"), "prompt": prompt}
    except Exception as e:
        return {"ok": False, "error": str(e)[:120], "hint": "start Fooocus then enable image_gen.json"}

if __name__ == '__main__':
    import sys
    print(sys.argv)
