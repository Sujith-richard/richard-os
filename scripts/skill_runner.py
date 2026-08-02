#!/usr/bin/env python3
"""Richard OS — run a skill (cross-platform)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "04-skills"

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/skill_runner.py <skill> [detail]")
        print("Skills:", ", ".join(p.name for p in SKILLS.iterdir() if p.is_dir()))
        return
    name = sys.argv[1]
    detail = sys.argv[2] if len(sys.argv) > 2 else ""
    skill_dir = SKILLS / name
    if not skill_dir.is_dir():
        print(f"Unknown skill: {name}")
        return
    skill = (skill_dir / "skill.md").read_text()
    print(f"● Loading skill: {name}")
    print("─" * 50)
    print(skill[:1500])
    if detail:
        print(f"\nTarget: {detail}")
    print("\n→ Ready. (Wire this to an agent to auto-execute.)")

if __name__ == "__main__":
    main()
