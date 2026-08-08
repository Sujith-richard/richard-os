#!/usr/bin/env python3
"""scripts/sdk.py - v6.0.0 Richard SDK (authoring layer).
Scaffold -> validate -> pack -> publish to Richard Hub.
Complements Package Manager (v5.3) + Hub (v5.9): this is how extension authors
create valid packages (department/skill/workflow/plugin/agent/structure)."""
import json, pathlib, zipfile, subprocess, argparse, time, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STAGE = ROOT / "06-data" / "sdk"
KINDS = ("department", "skill", "workflow", "plugin", "agent", "structure")

def _now(): return time.strftime("%Y-%m-%dT%H:%M:%S")

def _dir(kind, name): return STAGE / kind / name

def _ensure_manifest(kind, name, version, author, desc):
    d = _dir(kind, name); d.mkdir(parents=True, exist_ok=True)
    mf = d / "manifest.json"
    if not mf.exists():
        mf.write_text(json.dumps({
            "name": name, "kind": kind, "version": version,
            "author": author or "Developer-os", "desc": desc or "",
            "tier": "community", "created_at": _now(),
        }, indent=2))

def scaffold(kind, name, version="1.0.0", desc="", author=""):
    if kind not in KINDS:
        return {"ok": False, "error": f"kind must be one of {KINDS}"}
    if not name or any(c in name for c in " /\\:"):
        return {"ok": False, "error": "name must be a simple slug (no spaces/slashes)"}
    _ensure_manifest(kind, name, version, author, desc)
    d = _dir(kind, name)
    if not (d / "README.md").exists():
        (d / "README.md").write_text("# " + name + "\n\nA Richard OS " + kind + " package.\n")
    if kind == "skill":
        for f in ("skill.md", "examples.md", "reference.md"):
            if not (d / f).exists():
                (d / f).write_text("# " + f.replace(".md", "") + " — " + name + "\n\n_(SDK stub — replace me)_\n")
    elif kind == "department":
        (d / "spine.md").write_text("# Spine — " + name + " (20 items)\n\n" + "".join(f"{i}. _item {i}_\n" for i in range(1, 21)))
    elif kind == "workflow":
        (d / "workflow.md").write_text("# Workflow — " + name + "\n\n- trigger\n- execute\n- validate\n")
    elif kind == "plugin":
        (d / "plugin.py").write_text("def setup(richard):\n    return {'name': '" + name + "'}\n")
    elif kind == "agent":
        (d / "agent.md").write_text("# Agent — " + name + "\n\nroles: [task]\n")
    elif kind == "structure":
        (d / "structure.md").write_text("# Structure — " + name + "\n")
    return {"ok": True, "path": str(d), "kind": kind, "name": name, "version": version}

def validate(kind, name):
    d = _dir(kind, name)
    if not d.is_dir():
        return {"ok": False, "error": f"package not found: {kind}/{name}"}
    if not (d / "manifest.json").exists():
        return {"ok": False, "error": "missing manifest.json"}
    try:
        m = json.loads((d / "manifest.json").read_text())
    except Exception as e:
        return {"ok": False, "error": f"manifest not valid JSON: {e}"}
    req = ["manifest.json", "README.md"]
    missing = [r for r in req if not (d / r).exists()]
    return {"ok": not missing, "name": m.get("name"), "kind": m.get("kind"),
            "version": m.get("version"), "missing": missing}

def pack(kind, name):
    r = validate(kind, name)
    if not r.get("ok"):
        return r
    d = _dir(kind, name)
    build = STAGE / "build"; build.mkdir(exist_ok=True)
    ver = r.get("version", "1.0.0")
    out = build / f"{name}-{kind}-{ver}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in d.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(d.parent))
    return {"ok": True, "artifact": str(out), "bytes": out.stat().st_size}

def publish(kind, name, desc=""):
    r = validate(kind, name)
    if not r.get("ok"):
        return r
    sys.path.insert(0, str(ROOT / "scripts"))
    from hub import publish as hub_publish
    m = json.loads((_dir(kind, name) / "manifest.json").read_text())
    return hub_publish(name, kind, m.get("version", "1.0.0"), desc or m.get("desc", ""))

def main():
    ap = argparse.ArgumentParser(prog="richard-sdk", description="Richard OS extension authoring CLI")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("new"); p.add_argument("kind"); p.add_argument("name"); p.add_argument("-v", "--version", default="1.0.0"); p.add_argument("-d", "--desc", default=""); p.add_argument("-a", "--author", default="")
    p = sub.add_parser("validate"); p.add_argument("kind"); p.add_argument("name")
    p = sub.add_parser("pack"); p.add_argument("kind"); p.add_argument("name")
    p = sub.add_parser("publish"); p.add_argument("kind"); p.add_argument("name"); p.add_argument("-d", "--desc", default="")
    p = sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "new": print(json.dumps(scaffold(a.kind, a.name, a.version, a.desc, a.author), indent=2))
    elif a.cmd == "validate": print(json.dumps(validate(a.kind, a.name), indent=2))
    elif a.cmd == "pack": print(json.dumps(pack(a.kind, a.name), indent=2))
    elif a.cmd == "publish": print(json.dumps(publish(a.kind, a.name, a.desc), indent=2))
    elif a.cmd == "list":
        for k in KINDS:
            pth = STAGE / k
            if pth.is_dir():
                for d in sorted(pth.glob("*")):
                    print(f"[{k}] {d.name}")
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
