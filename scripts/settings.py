#!/usr/bin/env python3
"""
scripts/settings.py - Phase H4 Settings / user preferences
Persists user preferences to 06-data/settings.json (gitignored).
get()/update()/reset() with sane defaults. Consumed by agents + UI.
"""
import json, pathlib, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "06-data" / "settings.json"

DEFAULTS = {
    "name": "Sujith",
    "city": "Bangalore",
    "timezone": "Asia/Kolkata",
    "preferred_dept": "web",
    "default_model": "auto",          # auto = model orchestrator picks
    "theme": "dark",
    "notifications": True,
    "morning_brief": True,
    "voice_enabled": False,
    "autonomy_level": 2,              # 1-5 per Founder OS spectrum
}

def _load():
    if SETTINGS_PATH.exists():
        try:
            d = json.loads(SETTINGS_PATH.read_text())
            return {**DEFAULTS, **d}
        except Exception:
            pass
    return dict(DEFAULTS)

def get():
    return {"ok": True, "settings": _load()}

def _coerce(v):
    """Coerce string values to bool/int where appropriate."""
    if isinstance(v, str):
        if v.lower() in ("true", "false"):
            return v.lower() == "true"
        try:
            return int(v)
        except ValueError:
            pass
    return v

def update(fields):
    """Merge provided fields into saved settings (with type coercion)."""
    cur = _load()
    fields = {k: _coerce(v) for k, v in (fields or {}).items()}
    cur.update(fields)
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(cur, indent=2))
    return {"ok": True, "settings": cur}

def reset():
    SETTINGS_PATH.write_text(json.dumps(DEFAULTS, indent=2))
    return {"ok": True, "settings": dict(DEFAULTS)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--get", action="store_true")
    ap.add_argument("--set", nargs="*", metavar="KEY=VALUE")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    if args.get:
        for k, v in get()["settings"].items():
            print(f"  {k:18s} {v}")
        return
    if args.reset:
        print(json.dumps(reset(), indent=2)); return
    if args.set:
        fields = {}
        for kv in args.set:
            k, _, v = kv.partition("=")
            fields[k.strip()] = v.strip()
        print(json.dumps(update(fields), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
