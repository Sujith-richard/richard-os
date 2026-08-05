#!/usr/bin/env python3
"""Richard OS — cloud utilities bridge (OmniCloud, 9drive, WebToApp).
Honest status: connected / not_configured / error. Never fakes."""
import shutil
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor"
UTILS = {
    "omnicloud": ("OmniCloud", "multi-cloud utility"),
    "9drive": ("9drive", "cloud/file storage helper"),
    "webtoweb": ("WebToApp", "web → app wrapper"),
}

def status(name=None):
    targets = [name] if name else list(UTILS)
    out = {}
    for key in targets:
        label, purpose = UTILS.get(key, (key, ""))
        local = VENDOR / label
        if local.exists():
            out[key] = {"status": "connected", "detail": purpose + " — local clone present"}
        else:
            out[key] = {"status": "not_configured", "detail": purpose + f" — clone into vendor/{label}"}
    return {"provider": "cloud-utilities", "statuses": out}

def run(name, args):
    """Invoke a vendored util via node/python (honest availability gate)."""
    label, _ = UTILS.get(name, (name, ""))
    local = VENDOR / label
    if not local.exists():
        return {"error": f"{label} not configured — clone into vendor/{label} (honest)"}
    try:
        import subprocess
        r = subprocess.run(["python", str(local / "main.py")] + args, capture_output=True, text=True, timeout=120)
        return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[:200]}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
