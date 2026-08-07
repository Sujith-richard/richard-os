#!/usr/bin/env python3
"""
scripts/integrations.py - Live Integrations Hub (v3.4)
Per-source registry: fake | unconfigured | live | error.
Config stored in 06-data/integrations.json (gitignored, secrets stay local).
Connectors: github, gmail, weather, home, models. Stdlib only.
"""
import json, os, pathlib, datetime, re, sqlite3
import urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"
CONFIG_PATH = DATA / "integrations.json"
DB_PATH = DATA / "second_brain.db"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _load():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"sources": {}}

def _save(state):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(state, indent=2))

def _http_json(url, headers=None, timeout=12):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

# ---------------- sources registry ----------------
DEFAULTS = {
    "github":  {"owner": "Sujith-richard", "repo": "richard-os", "token": ""},
    "gmail":   {"email": "", "app_password": "", "imap_host": "imap.gmail.com", "max": 20},
    "weather": {"lat": "12.9716", "lon": "77.5946", "city": "Bangalore"},
    "home":    {"url": "http://homeassistant.local:8123", "token": "", "mode_env": "HOME_MODE"},
    "models":  {"base_url": "http://127.0.0.1:1234/v1", "api_key": "not-needed"},
}
REQUIRED = {
    "github":  ["owner"],
    "gmail":   ["email", "app_password"],
    "weather": ["lat", "lon"],
    "home":    ["url", "token"],
    "models":  ["base_url"],
}

def _cfg(name):
    state = _load()
    src = state.get("sources", {}).get(name, {})
    merged = dict(DEFAULTS.get(name, {}))
    merged.update(src.get("config", {}))
    return merged, src

def _save_src(name, src):
    state = _load()
    state.setdefault("sources", {})[name] = src
    _save(state)

def status_of(name):
    cfg, src = _cfg(name)
    mode = src.get("mode", "fake")
    if mode == "fake":
        return {"mode": "fake", "status": "fake", "configured": True}
    missing = [f for f in REQUIRED.get(name, []) if not str(cfg.get(f, "")).strip()]
    if missing:
        return {"mode": "real", "status": "unconfigured", "configured": False, "missing": missing}
    last_test = src.get("last_test")
    ok = bool(last_test and last_test.get("ok"))
    return {"mode": "real", "status": "live" if ok else "error",
            "configured": True, "last_test": last_test}

# ---------------- connectors ----------------
def test_github(cfg):
    url = f"https://api.github.com/users/{urllib.parse.quote(cfg['owner'])}/repos?per_page=100"
    headers = {"Accept": "application/vnd.github+json"}
    if cfg.get("token"):
        headers["Authorization"] = f"Bearer {cfg['token']}"
    repos = _http_json(url, headers)
    public = [r for r in repos if not r.get("private")]
    return {"ok": True, "detail": f"{len(public)} public repos for @{cfg['owner']}",
            "repos": [r["name"] for r in public][:20]}

def sync_github(cfg):
    r = test_github(cfg)
    out = DATA / "live_github.json"
    out.write_text(json.dumps(r, indent=2))
    return r

def test_weather(cfg):
    q = urllib.parse.urlencode({"latitude": cfg["lat"], "longitude": cfg["lon"],
                                 "current_weather": "true", "timezone": "auto"})
    d = _http_json(f"https://api.open-meteo.com/v1/forecast?{q}")
    cw = d.get("current_weather", {})
    return {"ok": True,
            "detail": f"{cw.get('temperature', '?')}°C, wind {cw.get('windspeed', '?')} km/h @ {cfg['city']}",
            "temp": cw.get("temperature"), "windspeed": cw.get("windspeed")}

def sync_weather(cfg):
    r = test_weather(cfg)
    (DATA / "live_weather.json").write_text(json.dumps({**r, "synced_at": _now()}, indent=2))
    return r

def _secret(name):
    try:
        from vault import get_secret
        return get_secret(name)
    except Exception:
        return None

def test_gmail(cfg):
    import imaplib
    # I3: prefer vault-stored credentials
    if not cfg.get("app_password") and cfg.get("vault_app_password"):
        cfg["app_password"] = _secret(cfg["vault_app_password"]) or ""
    M = imaplib.IMAP4_SSL(cfg["imap_host"])
    M.login(cfg["email"], cfg["app_password"])
    M.select("INBOX")
    typ, data = M.search(None, "ALL")
    total = len(data[0].split()) if typ == "OK" and data and data[0] else 0
    typ, data = M.search(None, "UNSEEN")
    unseen = len(data[0].split()) if typ == "OK" and data and data[0] else 0
    M.logout()
    return {"ok": True, "detail": f"INBOX: {total} total, {unseen} unread", "total": total, "unseen": unseen}

def sync_gmail(cfg):
    import imaplib, email as eml
    from email.header import decode_header
    M = imaplib.IMAP4_SSL(cfg["imap_host"])
    M.login(cfg["email"], cfg["app_password"])
    M.select("INBOX")
    typ, data = M.search(None, "ALL")
    ids = data[0].split()[-int(cfg.get("max", 20)):] if typ == "OK" and data and data[0] else []
    msgs = []
    for i in ids:
        typ, d = M.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        if typ != "OK" or not d or not d[0]:
            continue
        raw = d[0][1].decode(errors="replace")
        m = eml.message_from_string(raw)
        def dec(v):
            if not v: return ""
            parts = decode_header(v)
            return "".join(b.decode(p or "utf-8", errors="replace") if isinstance(b, bytes) else b for b, p in parts)
        msgs.append({"from": dec(m.get("From")), "subject": dec(m.get("Subject")),
                     "date": m.get("Date", ""), "uid": i.decode()})
    M.logout()
    (DATA / "live_gmail.json").write_text(json.dumps({"synced_at": _now(), "messages": msgs}, indent=2))
    # upsert into second_brain.db if an inbox table exists
    if DB_PATH.exists():
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('emails','inbox','live_inbox')")
        tbl = cur.fetchone()
        if tbl:
            t = tbl[0]
            cur.execute(f"DELETE FROM {t}")
            for m in msgs:
                try:
                    cur.execute(f"INSERT INTO {t} (sender, subject, received_at) VALUES (?,?,?)",
                                (m["from"], m["subject"], m["date"]))
                except sqlite3.Error:
                    pass
            con.commit()
        con.close()
    return {"ok": True, "detail": f"synced {len(msgs)} messages", "count": len(msgs)}

def test_home(cfg):
    if os.environ.get("HOME_MODE", "simulate") != "homeassistant":
        return {"ok": False, "detail": "HOME_MODE=simulate (fake devices)", "simulated": True}
    try:
        states = _http_json(cfg["url"].rstrip("/") + "/api/states",
                            {"Authorization": f"Bearer {cfg['token']}"})
        return {"ok": True, "detail": f"{len(states)} entities in Home Assistant", "count": len(states)}
    except Exception as e:
        return {"ok": False, "detail": f"HA unreachable: {e}", "simulated": False}

def sync_home(cfg):
    r = test_home(cfg)
    (DATA / "live_home.json").write_text(json.dumps({**r, "synced_at": _now()}, indent=2))
    return r

def test_models(cfg):
    try:
        d = _http_json(cfg["base_url"].rstrip("/") + "/models")
        models = [m.get("id") for m in d.get("data", [])]
        return {"ok": True, "detail": f"{len(models)} models via {cfg['base_url']}", "models": models[:20]}
    except Exception as e:
        return {"ok": False, "detail": f"proxy unreachable: {e}"}

def sync_models(cfg):
    r = test_models(cfg)
    (DATA / "live_models.json").write_text(json.dumps({**r, "synced_at": _now()}, indent=2))
    return r

CONNECTORS = {
    "github":  {"title": "GitHub", "icon": "🐙", "test": test_github, "sync": sync_github},
    "gmail":   {"title": "Gmail", "icon": "📧", "test": test_gmail, "sync": sync_gmail},
    "weather": {"title": "Weather", "icon": "🌦️", "test": test_weather, "sync": sync_weather},
    "home":    {"title": "Home Assistant", "icon": "🏠", "test": test_home, "sync": sync_home},
    "models":  {"title": "AI Models", "icon": "🧠", "test": test_models, "sync": sync_models},
}

# ---------------- orchestration API ----------------
def list_integrations():
    out = {}
    for name, c in CONNECTORS.items():
        cfg, src = _cfg(name)
        st = status_of(name)
        out[name] = {
            "name": name, "title": c["title"], "icon": c["icon"],
            "status": st["status"], "mode": st["mode"],
            "configured": st.get("configured", False),
            "missing": st.get("missing", []),
            "last_test": src.get("last_test", {}).get("detail"),
            "last_sync": src.get("last_sync"),
            "fields": [{"key": k, "label": k.replace("_", " ").title(), "set": bool(str(cfg.get(k, "")).strip())}
                       for k in DEFAULTS.get(name, {})],
        }
    return {"ok": True, "integrations": out}

def test_source(name):
    if name not in CONNECTORS:
        return {"ok": False, "error": "unknown source"}
    cfg, src = _cfg(name)
    try:
        r = CONNECTORS[name]["test"](cfg)
    except Exception as e:
        r = {"ok": False, "detail": str(e)}
    src["last_test"] = {"ok": r.get("ok", False), "detail": r.get("detail", ""), "at": _now()}
    _save_src(name, src)
    return {"ok": True, "source": name, "result": r, "status": status_of(name)}

def sync_source(name):
    if name not in CONNECTORS:
        return {"ok": False, "error": "unknown source"}
    cfg, src = _cfg(name)
    try:
        r = CONNECTORS[name]["sync"](cfg)
    except Exception as e:
        r = {"ok": False, "detail": str(e)}
    src["last_sync"] = _now()
    src["last_test"] = {"ok": r.get("ok", False), "detail": r.get("detail", ""), "at": _now()}
    _save_src(name, src)
    return {"ok": True, "source": name, "result": r, "status": status_of(name)}

def set_mode(name, mode):
    if name not in CONNECTORS:
        return {"ok": False, "error": "unknown source"}
    if mode not in ("fake", "real"):
        return {"ok": False, "error": "mode must be fake|real"}
    _, src = _cfg(name)
    src["mode"] = mode
    _save_src(name, src)
    return {"ok": True, "source": name, "mode": mode, "status": status_of(name)}

def save_source_config(name, fields):
    if name not in CONNECTORS:
        return {"ok": False, "error": "unknown source"}
    cfg, src = _cfg(name)
    allowed = set(DEFAULTS.get(name, {}))
    for k, v in (fields or {}).items():
        if k in allowed:
            cfg[k] = str(v).strip()
    src["config"] = cfg
    _save_src(name, src)
    return {"ok": True, "source": name, "status": status_of(name)}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Live Integrations Hub")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--test", metavar="SOURCE")
    ap.add_argument("--sync", metavar="SOURCE")
    ap.add_argument("--mode", nargs=2, metavar=("SOURCE", "fake|real"))
    args = ap.parse_args()
    if args.list:
        print(json.dumps(list_integrations(), indent=2)); return
    if args.test:
        print(json.dumps(test_source(args.test), indent=2)); return
    if args.sync:
        print(json.dumps(sync_source(args.sync), indent=2)); return
    if args.mode:
        print(json.dumps(set_mode(*args.mode), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()

def resolve_source(name):
    """Return live file path if source is live, else None (callers fall back to seeded data)."""
    st = status_of(name)
    if st.get("status") == "live":
        f = DATA / f"live_{name}.json"
        if f.exists():
            return f
    return None
