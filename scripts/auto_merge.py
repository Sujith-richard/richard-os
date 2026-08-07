#!/usr/bin/env python3
"""
scripts/auto_merge.py - Phase F4 Auto-merge
Brain merges local + cloud outputs into one coherent result.
If cloud returned empty/failed, keeps the best available part (local or a retry note).
"""
import json, sys, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent

def merge(request, local, cloud, gap=None):
    """Merge local + cloud outputs. Prefers cloud for the gapped capability, keeps local otherwise."""
    cloud_ok = cloud and cloud.strip() and not cloud.startswith("[LLM unavailable")
    local_ok = local and local.strip() and not local.startswith("[LLM unavailable")
    parts = []
    if local_ok and local.strip() not in ("OK",):
        parts.append(("local", local.strip()))
    if cloud_ok and cloud.strip() not in ("OK",):
        parts.append(("cloud", cloud.strip()))
    if not parts:
        merged = f"[merge] both models returned empty for: {request[:80]}"
        source = "none"
    elif len(parts) == 1:
        src, txt = parts[0]
        merged, source = txt, src
    else:
        # both present: cloud (specialist) fills the gap, local adds foundation
        merged = (f"### Local model output\n{parts[0][1]}\n\n"
                  f"### {gap or 'specialist'} model addition\n{parts[1][1]}")
        source = "merged"
    return {"ok": True, "request": request, "merged": merged, "source": source,
            "local_len": len(local or ""), "cloud_len": len(cloud or "")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="Build a fitness app")
    ap.add_argument("--local", default="")
    ap.add_argument("--cloud", default="")
    ap.add_argument("--gap", default="coding")
    args = ap.parse_args()
    print(json.dumps(merge(args.request, args.local, args.cloud, args.gap), indent=2))

if __name__ == "__main__":
    main()
