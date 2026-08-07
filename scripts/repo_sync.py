#!/usr/bin/env python3
"""scripts/repo_sync.py - Phase C5 Repo update/sync lifecycle
git pull + re-extract every ingested repo; report staleness."""
import subprocess, pathlib, json, sys, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"

def sync_all():
    repos = sorted(p for p in VENDOR.iterdir() if p.is_dir() and (p / ".git").exists())
    out = []
    for r in repos:
        try:
            res = subprocess.run(["git", "-C", str(r), "pull", "--ff-only"],
                                 capture_output=True, text=True, timeout=120)
            out.append({"repo": r.name, "ok": res.returncode == 0,
                        "detail": res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr.strip()[:80]})
        except Exception as e:
            out.append({"repo": r.name, "ok": False, "detail": str(e)[:80]})
    return {"ok": True, "synced": out}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true")
    args = ap.parse_args()
    if args.sync:
        r = sync_all()
        for x in r["synced"]:
            print(f"  {'ok ' if x['ok'] else 'ERR'} {x['repo']}: {x.get('detail','')[:60]}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
