#!/usr/bin/env python3
"""Richard OS — cross-platform boot."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print("╔══════════════════════════════════════╗")
    print("║   RICHARD OS · boot sequence          ║")
    print("╚══════════════════════════════════════╝")
    ok = True
    for folder in ["01-root-spine","02-blocks","03-agents","04-skills",
                   "05-systems-of-record","06-data","07-schedules"]:
        p = ROOT / folder
        status = "✓" if p.is_dir() else "✗ missing"
        if not p.is_dir():
            ok = False
        print(f"  {status}  {folder}/")
    if ok:
        print("\n✓ Richard OS structure ready.")
        print("  Next: python run.py --interview   (encode your judgment)")
    else:
        print("\n✗ Some folders missing. Re-run the mkdir step.")
        sys.exit(1)

if __name__ == "__main__":
    main()
