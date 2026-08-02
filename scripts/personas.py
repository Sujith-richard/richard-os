#!/usr/bin/env python3
"""Richard OS — persona roster viewer: open a folder, meet the team."""
import sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONAS = ROOT / "02-blocks" / "personas"

def main():
    files = sorted(PERSONAS.glob("*.yaml"))
    if not files:
        print("No personas yet — create 02-blocks/personas/*.yaml")
        return
    name = sys.argv[1] if len(sys.argv) > 1 else "list"
    if name == "list":
        print("Personas (folders):")
        for f in files:
            cfg = yaml.safe_load(f.read_text())
            ceo = cfg.get("ceo") or cfg.get("director") or "?"
            print(f"  - {f.stem}  (lead: {ceo})")
        return
    path = PERSONAS / f"{name}.yaml"
    if not path.exists():
        print(f"Unknown persona: {name}"); return
    cfg = yaml.safe_load(path.read_text())
    print(f"\n📂 {path.stem} — the roster")
    for key, workers in cfg.items():
        if isinstance(workers, list):
            print(f"  {key}: {', '.join(workers)}")
        elif isinstance(workers, dict):
            print(f"  {key}:")
            for head, team in workers.items():
                print(f"    {head} → {', '.join(team)}")

if __name__ == "__main__":
    main()
