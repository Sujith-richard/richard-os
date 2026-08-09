#!/usr/bin/env python3
"""scripts/hub.py - v5.9.0 Richard Hub (registry layer).
Builds on the v5.3 Package Manager: every extension is an installable package.
This module is the marketplace index: local catalog + optional GitHub-hosted
remote index + publish/pull/search. No heavy deps (httpx lazy)."""
import json, sqlite3, pathlib, sys, argparse, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "06-data" / "hub.db"
MANIFEST_DIR = ROOT / "06-data" / "hub_manifests"
REMOTE_CFG = ROOT / "06-data" / "hub_remote.json"

def _now(): return time.strftime("%Y-%m-%d %H:%M:%S")

def _conn():
    DB.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS hub_packages (
        name TEXT PRIMARY KEY, kind TEXT, version TEXT, desc TEXT,
        author TEXT DEFAULT 'Developer-os', tier TEXT DEFAULT 'community',
        source TEXT DEFAULT 'local', repo TEXT DEFAULT '',
        status TEXT DEFAULT 'available', downloads INTEGER DEFAULT 0,
        installed_at TEXT, published_at TEXT, created_at TEXT, featured INTEGER DEFAULT 0, signature TEXT DEFAULT '');""")
    c.commit(); c.close()

def _dedupe(items):
    seen = {}
    for it in items:
        n = it.get("name")
        if n and n not in seen: seen[n] = it
    return list(seen.values())

def _local_catalog():
    out = []
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from package_manager import list_packages as pl
        r = pl()
        for p in (r.get("packages", []) if isinstance(r, dict) else r or []):
            out.append({**p, "source": "local"})
    except Exception:
        pass
    try:
        from plugin_store import catalog as cs
        r = cs()
        items = r.get("items", r) if isinstance(r, dict) else r
        for p in items or []:
            out.append({**p, "source": "local"})
    except Exception:
        pass
    return _dedupe(out)

def _remote_index():
    try:
        if not REMOTE_CFG.exists():
            return {"ok": True, "packages": []}
        cfg = json.loads(REMOTE_CFG.read_text())
        url = cfg.get("url", "")
        if not url:
            return {"ok": True, "packages": []}
        import httpx
        r = httpx.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            pkgs = data.get("packages", []) if isinstance(data, dict) else data
            return {"ok": True, "source": "remote", "packages": pkgs}
    except Exception:
        pass
    return {"ok": True, "source": "remote", "packages": []}

def index(include_remote=True):
    init_db()
    pkgs = _local_catalog()
    for p in pkgs:
        p.setdefault("kind", "package"); p.setdefault("version", "1.0.0")
        p.setdefault("desc", ""); p.setdefault("author", "Developer-os")
        p.setdefault("tier", "community"); p.setdefault("repo", ""); p.setdefault("featured", False)
        p.setdefault("status", "available")
    if include_remote:
        r = _remote_index()
        for p in r.get("packages", []):
            p["source"] = "remote"; p.setdefault("status", "available")
            pkgs.append(p)
    pkgs = _dedupe(pkgs)
    c = _conn()
    rows = {r["name"]: dict(r) for r in c.execute("SELECT * FROM hub_packages").fetchall()}
    c.close()
    existing = {p.get("name") for p in pkgs}
    for n, x in rows.items():
        if n not in existing:
            pkgs.append({"name": n, "kind": x.get("kind") or "package", "version": x.get("version") or "1.0.0",
                         "desc": x.get("desc") or "", "author": x.get("author") or "Developer-os",
                         "tier": x.get("tier") or "community", "source": x.get("source") or "hub",
                         "repo": x.get("repo") or "", "status": x.get("status") or "available",
                         "downloads": x.get("downloads") or 0, "installed_at": x.get("installed_at"),
                         "published_at": x.get("published_at")})
    for p in pkgs:
        n = p.get("name")
        if n in rows:
            x = rows[n]
            p.update({k: x.get(k) for k in ("status", "downloads", "installed_at", "published_at", "version", "featured", "signature", "repo") if x.get(k) is not None})
    return {"ok": True, "count": len(pkgs), "packages": pkgs}

def search(q=""):
    r = index()
    pkgs = r["packages"]
    if q:
        ql = q.lower()
        pkgs = [p for p in pkgs if ql in (p.get("name", "") + " " + p.get("kind", "") + " " + p.get("desc", "")).lower()]
    return {"ok": True, "query": q, "count": len(pkgs), "packages": pkgs}

def publish(name, kind="package", version="1.0.0", desc="", author="Developer-os", tier="community", repo="", featured=False):
    init_db(); MANIFEST_DIR.mkdir(exist_ok=True)
    import hashlib
    _core = json.dumps({"name": name, "kind": kind, "version": version, "desc": desc,
                        "author": author, "tier": tier, "repo": repo or "", "published_at": _now()}, sort_keys=True)
    manifest = {"name": name, "kind": kind, "version": version, "desc": desc,
                "author": author, "tier": tier, "repo": repo or "", "published_at": _now(),
                "signature": hashlib.sha256(_core.encode()).hexdigest()[:16]}
    path = MANIFEST_DIR / f"{name}.json"
    path.write_text(json.dumps(manifest, indent=2))
    c = _conn()
    c.execute("""INSERT OR REPLACE INTO hub_packages
        (name, kind, version, desc, author, tier, source, repo, status, published_at, created_at, featured, signature)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (name, kind, version, desc or "", author, tier, "local", repo or "", "published", _now(), _now(), 1 if featured else 0, manifest.get("signature", "")))
    c.commit(); c.close()
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from package_manager import install
        install(name)
    except Exception:
        pass
    return {"ok": True, "published": name, "kind": kind, "version": version, "manifest": str(path)}

def sign(name):
    """Return the signature for a package (for multi-repo verification)."""
    mf = MANIFEST_DIR / f"{name}.json"
    if not mf.exists():
        return {"ok": False, "error": "no manifest"}
    d = json.loads(mf.read_text())
    return {"ok": True, "name": name, "signature": d.get("signature"), "repo": d.get("repo"), "kind": d.get("kind")}

def pull(name, kind=None):
    init_db()
    r = index(include_remote=False)
    found = next((p for p in r["packages"] if p.get("name") == name), None)
    if not found:
        rr = _remote_index()
        found = next((p for p in rr.get("packages", []) if p.get("name") == name), None)
    if not found:
        return {"ok": False, "error": f"package '{name}' not found in Hub"}
    k = kind or found.get("kind") or "package"
    ver = found.get("version") or "1.0.0"
    install_note = ""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        if k in ("plugin", "mcp", "tool"):
            from plugin_store import install as pi
            pi(name)
        else:
            from package_manager import install as pm
            pm(name)
    except Exception as e:
        install_note = f"registry-only (no local impl): {str(e)[:70]}"
    c = _conn()
    c.execute("""INSERT INTO hub_packages (name, kind, version, desc, status, downloads, created_at)
                 VALUES (?,?,?,?,'installed',1,?)
                 ON CONFLICT(name) DO UPDATE SET status='installed',
                   downloads=hub_packages.downloads+1, installed_at=?,
                   kind=excluded.kind, version=excluded.version""",
              (name, k, ver, found.get("desc") or "", _now(), _now()))
    c.commit(); c.close()
    return {"ok": True, "installed": name, "kind": k, "version": ver, "source": found.get("source", "local"), "note": install_note}

def stats():
    init_db()
    c = _conn()
    total = c.execute("SELECT COUNT(*) n FROM hub_packages").fetchone()["n"]
    published = c.execute("SELECT COUNT(*) n FROM hub_packages WHERE status IN ('published','installed')").fetchone()["n"]
    downloads = c.execute("SELECT COALESCE(SUM(downloads),0) s FROM hub_packages").fetchone()["s"]
    kinds = {x["kind"]: x["n"] for x in c.execute("SELECT kind, COUNT(*) n FROM hub_packages GROUP BY kind")}
    c.close()
    return {"ok": True, "in_registry": total, "published": published, "downloads": downloads, "kinds": kinds}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--search", metavar="Q")
    ap.add_argument("--publish", nargs="+", metavar="NAME")
    ap.add_argument("--pull", metavar="NAME")
    ap.add_argument("--remote", nargs=2, metavar=("URL","FILE"))
    ap.add_argument("--export-index", action="store_true")
    ap.add_argument("--remote-set", metavar="URL")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    if a.remote:
        url = a.remote[0]
        REMOTE_CFG.write_text(json.dumps({"url": url}, indent=2))
        print(json.dumps({"ok": True, "remote": url})); return
    if a.list:
        for p in index()["packages"]:
            print(f"[{p.get('kind','?')}] {p.get('name')} v{p.get('version')} — {p.get('desc','')[:50]} ({p.get('status')})")
        return
    if a.search:
        r = search(a.search)
        print(f"{r['count']} result(s):")
        for p in r["packages"]:
            print(f"  [{p.get('kind')}] {p.get('name')} v{p.get('version')}")
        return
    if a.publish:
        name = a.publish[0]; kind = a.publish[1] if len(a.publish) > 1 else "package"
        ver  = a.publish[2] if len(a.publish) > 2 else "1.0.0"
        desc = a.publish[3] if len(a.publish) > 3 else ""
        print(json.dumps(publish(name, kind, ver, desc), indent=2)); return
    if a.pull:
        print(json.dumps(pull(a.pull), indent=2)); return
    if a.stats:
        print(json.dumps(stats(), indent=2)); return
    if a.export_index:
        print(json.dumps(export_index(), indent=2)); return
    if a.remote_set:
        print(json.dumps(remote_set(a.remote_set), indent=2)); return
    ap.print_help()


def export_index():
    """Build a standalone marketplace index (hub-index.json) — commit this to
    any static host (GitHub repo / Pages / gist) as the 'remote' for other machines."""
    r = index(include_remote=False)
    pkgs = []
    for p in r["packages"]:
        if not p.get("name"):
            continue
        pkgs.append({
            "name": p["name"], "kind": p.get("kind") or "package",
            "version": p.get("version") or "1.0.0", "desc": (p.get("desc") or "")[:200],
            "author": p.get("author") or "Developer-os", "tier": p.get("tier") or "community",
            "repo": p.get("repo") or "", "status": "available", "featured": bool(p.get("featured")),
            "signature": p.get("signature") or "",
            "updated_at": p.get("published_at") or _now(),
        })
    out = {"hub": "hub-index", "version": 1, "generated_at": _now(), "count": len(pkgs), "packages": pkgs}
    path = ROOT / "06-data" / "hub-index.json"
    path.write_text(json.dumps(out, indent=2))
    return {"ok": True, "count": len(pkgs), "path": str(path), "file": "hub-index.json"}

def remote_set(url=""):
    """Set the remote index URL (GitHub Pages / raw gist / hosted JSON)."""
    cfg = {"url": url} if url else {}
    REMOTE_CFG.write_text(json.dumps(cfg, indent=2))
    return {"ok": True, "remote": url, "file": str(REMOTE_CFG)}

if __name__ == "__main__":
    main()
