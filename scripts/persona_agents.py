#!/usr/bin/env python3
"""Richard OS — run any persona specialist as a real agent.
Usage: python scripts/persona_agents.py <persona> <specialist> <task>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_lib import call_llm, log_run, read_memory

ROOT = Path(__file__).resolve().parent.parent
PERSONAS = ROOT / "02-blocks" / "personas"

def find_specialist(persona, specialist):
    """Locate a specialist in the persona yaml; return its 'job' definition."""
    import yaml
    cfg = yaml.safe_load((PERSONAS / f"{persona}.yaml").read_text())
    for head, team in (cfg.get("heads") or {}).items():
        if specialist in team:
            return head, specialist
    for director, team in (cfg.get("directors") or {}).items():
        if specialist in team:
            return director, specialist
    if specialist in (cfg.get("orchestrators") or []):
        return "orchestrators", specialist
    return None, None

# A light job description per specialist (extends as you add more)
JOBS = {
    "script-writer": "Write a short-form video script: hook, problem, proof, CTA. ~150 words.",
    "hook-writer": "Write 5 hook variations for a video/post, each under 12 words.",
    "thumbnail-designer": "Describe a high-CTR thumbnail concept: composition, text overlay, contrast.",
    "title-strategist": "Suggest 5 titles for a video, mixing curiosity, numbers, and keywords.",
    "community-manager": "Draft 3 engagement questions to post in a community.",
    "postmortem-analyst": "List 5 things to review after a piece of content underperforms.",
    "icp-builder": "Draft an Ideal Customer Profile: demographics, pains, goals, objections.",
    "offer-architect": "Draft a compelling offer: outcome, mechanism, guarantee, price anchor.",
    "voice-extractor": "Extract brand voice traits from sample writing: tone, words, rhythm.",
    "hook-engineer": "Write 5 hook variations optimized for short-form retention.",
    "editor-lead": "Describe an edit plan: cuts, pacing, captions, sound design.",
    "prospector": "Draft a prospecting message for a specific client type.",
    "closer": "Draft a discovery-call outline that moves a lead to yes.",
    "account-manager": "Draft a weekly client status update in a friendly professional tone.",
    "revenue-analyst": "List 3 revenue metrics to watch and why.",
}

def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/persona_agents.py <persona> <specialist> <task>")
        print("  e.g. python scripts/persona_agents.py youtube-agency script-writer 'how I built an AI OS'")
        return
    persona, specialist, task = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])
    head, resolved = find_specialist(persona, specialist)
    if not resolved:
        print(f"❌ {specialist} not found in {persona}")
        return
    job = JOBS.get(specialist, f"Act as the {specialist} specialist. Deliver high-quality work.")
    mem = read_memory()[:1200]
    prompt = (f"You are the {specialist} specialist in {persona} (reports to {head}).\n"
              f"Your job: {job}\nTask: {task}\n\nOS MEMORY:\n{mem}")
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run(f"persona/{persona}/{specialist}", "run complete", out[:120])

if __name__ == "__main__":
    main()
