#!/usr/bin/env python3
"""Richard OS — cross-platform boot."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FOLDERS = ["01-root-spine","02-blocks","03-agents","04-skills",
           "05-systems-of-record","06-data","07-schedules"]

def main():
    print("╔══════════════════════════════════════╗")
    print("║   RICHARD OS · boot sequence          ║")
    print("╚══════════════════════════════════════╝")
    ok = True
    for folder in FOLDERS:
        p = ROOT / folder
        status = "✓" if p.is_dir() else "✗ missing"
        if not p.is_dir():
            ok = False
        print(f"  {status}  {folder}/")
    print("\n✓ Richard OS structure ready." if ok
          else "\n✗ Missing folders. Run the mkdir step.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
