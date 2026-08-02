#!/usr/bin/env python3
"""Richard OS — run an SOP as an executable agent playbook.
Usage: python scripts/sop_runner.py <sop-name> <task>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_lib import call_llm, log_run, read_memory

ROOT = Path(__file__).resolve().parent.parent
SOPS = ROOT / "04-skills" / "sops"

def main():
    if len(sys.argv) < 2:
        print("SOPs:", ", ".join(f.stem for f in sorted(SOPS.glob("*.md"))))
        print("Usage: python scripts/sop_runner.py <sop> <task>")
        return
    name = sys.argv[1]
    task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    f = SOPS / f"{name}.md"
    if not f.exists():
        print(f"Unknown SOP: {name}"); return
    sop = f.read_text()
    mem = read_memory()[:1000]
    prompt = (f"You are executing this SOP step by step. Follow each step exactly.\n\n"
              f"SOP:\n{sop}\n\nTASK: {task}\n\nOS MEMORY:\n{mem}\n\n"
              f"Output the completed steps with the result of each, then any next actions.")
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run(f"sop/{name}", "run complete", out[:120])

if __name__ == "__main__":
    main()
