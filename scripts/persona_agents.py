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
    """Locate a specialist in the persona yaml; return its head/director."""
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
    "niche-architect": "Pick a niche: size, pain, who wins, why now, entry wedge.",
    "brand-voice-researcher": "Research a brand's voice: tone, vocabulary, sentence rhythm, values.",
    "financial-modeler": "Build a simple revenue model: units, price, costs, margin, break-even.",
    "content-strategist": "Plan a 30-day content calendar with topics, formats, and cadence.",
    "paid-ads-shortform": "Draft a paid short-form ad concept: hook, offer, CTA, audience.",
    "stories-producer": "Outline 5 story-driven content ideas with a beginning, middle, pay-off.",
    "twitter-writer": "Write 3 Twitter/X posts with a hook, insight, and reply-bait.",
    "linkedin-writer": "Draft a LinkedIn post: personal story, lesson, call to action.",
    "youtube-producer": "Outline a YouTube video: title, hook, chapters, CTA.",
    "vsl-builder": "Write a video sales letter outline: hook, problem, story, offer, guarantee, CTA.",
    "vsl-writer": "Write VSL copy sections: attention, pain, solution, proof, objection, close.",
    "funnel-architect": "Design a funnel: traffic to opt-in to tripwire to core to upsell to backend.",
    "sales-scripter": "Write a sales call script: open, qualify, present, handle objections, close.",
    "sales-ops": "Define sales ops: pipeline stages, follow-up cadence, metrics, tools.",
    "email-copywriter": "Write 3 emails: subject, preview, body, single CTA each.",
    "lead-magnet-designer": "Design a lead magnet: format, promise, structure, delivery.",
    "webinar-producer": "Outline a webinar: title, promise, agenda, offer, urgency.",
    "show-rate-ops": "Improve show rate: reminders, reschedule flow, calendar blocks.",
    "jv-outreach": "Draft a joint-venture outreach message: value to partner, ask, CTA.",
    "affiliate-architect": "Design an affiliate program: commission, cookie window, creatives, terms.",
    "referral-designer": "Design a referral loop: incentive, ask timing, tracking, reward.",
    "launch-manager": "Build a launch plan: pre, open, close phases with daily actions.",
    "post-launch-analyst": "Analyze a launch: numbers, breakdowns, wins, next iteration.",
    "sop-builder": "Write an SOP: goal, inputs, steps, owner, quality bar.",
    "talent-recruiter": "Draft a job post and screening questions for a role.",
    "client-success": "Draft a client health check: wins, risks, next action, cadence.",
    "case-study-producer": "Draft a case study: client, problem, solution, results, quote.",
    "competitor-analyst": "Analyze a competitor: offer, pricing, content, gaps.",
    "linkedin-ghostwriter": "Write a LinkedIn post in the client's voice: story, insight, CTA.",
    "dm-strategist": "Draft a DM sequence: open, value, qualify, book, follow-up.",
    "lead-list-builder": "Describe a lead list build: sources, filters, enrichment, export.",
    "call-prep-specialist": "Prepare a call brief: prospect, goals, questions, objections, next step.",
    "client-reporter": "Draft a client report: progress, results, next actions, metrics.",
    "program-mentor": "Draft a mentor check-in: progress, blockers, encouragement, next goal.",
    "audience-researcher": "Research an audience: demographics, pains, content they consume, objections.",
    "creator-voice-encoder": "Encode a creator's voice: cadence, phrases, topics, values, do/don'ts.",
    "content-orchestrator": "Plan a content week: themes, formats, who produces, deadlines.",
    "monetization-orchestrator": "Plan monetization: offers, pricing, upsells, sponsors, memberships.",
    "onboarder": "Draft a client onboarding: welcome, kickoff, assets, milestones.",
    "reporter": "Draft a performance report: output, outcomes, next week plan.",
    "moment-scorer": "Score clips: watchability, hook strength, shareability, pick top 3.",
    "voice-keeper": "Preserve brand voice in edits: phrasing, pacing, signature lines.",
    "account-warmer": "Draft a warm-up sequence: follow, engage, comment, DM.",
    "poster": "Draft posting specs: platform, caption, hashtags, best time.",
    "library-compounder": "Organize a clip library: tags, categories, reusables, indexing.",
    "outcome-tracker": "Track outcomes: metric, baseline, result, next experiment.",
}

KNOWLEDGE = {
    "script-writer": "creator.db + performance metrics",
    "thumbnail-writer": "creator.db/performance",
    "hook-writer": "creator.db content ideas",
    "icp-builder": "crm.db contacts",
    "offer-architect": "encoding.md pricing + crm.db",
    "revenue-analyst": "finance.db transactions",
    "voice-writer": "reference docs", 
    "funnel-architect": "crm.db deals",
    "competitor-analyst": "web search (mcp)", 
    "client-reporter": "pm.db projects",
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
    prompt = (f"You are the {specialist} specialist in {persona} (reports to {head}).\n" + f"Knowledge to draw from: {KNOWLEDGE.get(specialist, 'core')}\n" +
              f"Your job: {job}\nTask: {task}\n\nOS MEMORY:\n{mem}")
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run(f"persona/{persona}/{specialist}", "run complete", out[:120])

if __name__ == "__main__":
    main()
