#!/usr/bin/env python3
"""scripts/offline_model.py - Phase J1 Offline local model
Dataset inventory + train-on-accumulated + offline status."""
import json, pathlib, subprocess, sys, argparse
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASETS = ROOT / "06-data" / "datasets"

def inventory():
    files = sorted(DATASETS.glob("*.jsonl"))
    total, out = 0, []
    for f in files:
        n = sum(1 for _ in f.open() if _.strip())
        total += n
        out.append({"file": f.name, "samples": n})
    return {"ok": True, "datasets": out, "total_samples": total}

def train(steps=30, model="sshleifer/tiny-gpt2"):
    inv = inventory()
    if inv["total_samples"] == 0:
        return {"ok": False, "error": "no datasets to train on"}
    merged = DATASETS / "merged-training.jsonl"
    with open(merged, "w") as out:
        for f in DATASETS.glob("*.jsonl"):
            if f.name == "merged-training.jsonl": continue
            for line in f.open():
                if line.strip(): out.write(line)
    cmd = [sys.executable, str(ROOT / "scripts" / "train_lora.py"),
           "--dataset", "merged-training", "--steps", str(steps), "--model", model]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {"ok": r.returncode == 0,
                "detail": (r.stdout or r.stderr)[-200:], "samples": inv["total_samples"]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "training timed out"}

def offline_status():
    inv = inventory()
    local = (ROOT / "06-data" / "models").exists() and any((ROOT / "06-data" / "models").iterdir())
    return {"ok": True, "offline_ready": local, "datasets": inv["total_samples"],
            "local_model": "trained" if local else "none"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--train", nargs="?", const="30")
    ap.add_argument("--offline-status", action="store_true")
    args = ap.parse_args()
    if args.inventory:
        d = inventory()
        print(f"datasets: {len(d['datasets'])} | total samples: {d['total_samples']}")
        for x in d["datasets"]: print(f"  {x['file']}: {x['samples']}")
        return
    if args.offline_status:
        print(json.dumps(offline_status(), indent=2)); return
    if args.train:
        print(json.dumps(train(steps=int(args.train)), indent=2, default=str)); return
    ap.print_help()

if __name__ == "__main__":
    main()
