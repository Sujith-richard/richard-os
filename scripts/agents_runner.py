#!/usr/bin/env python3
"""Richard OS — run a named agent against a system of record."""
import sys
from agent_lib import db, log_run, read_memory, call_llm, queue_for_approval

AGENTS = {
    "job_hunter": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are the Job-Hunter agent. Read the OS memory. "
                   "Summarize the current job leads from the second_brain DB "
                   "and recommend the next 3 actions, at autonomy level 2 (recommend only)."),
    },
    "content_ops": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are Content-Ops. Read the OS memory. Look at content ideas in the "
                   "creator DB and draft one LinkedIn post outline for each, autonomy 2."),
    },
    "freelance_biz": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are Freelance-Biz. Read OS memory. Review finance transactions and "
                   "CRM contacts, then list follow-ups and any invoice due, autonomy 2."),
    },
    "pm_assistant": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are PM-Assistant. Read OS memory. List open tasks from the pm DB, "
                   "flag blockers, and suggest today's top 3 priorities, autonomy 3."),
    },
    "reading_agent": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are Reading-Ops. Read the OS memory. Look at the saved links in the "
                   "reading DB and recommend the top 3 to read today based on current goals "
                   "(job hunt, freelance, learning), autonomy 2."),
    },
    "portfolio_builder": {
        "model": "deepseek-v4-flash-free",
        "prompt": ("You are Portfolio-Builder. Read OS memory. Based on projects and content "
                   "in the DBs, suggest 3 improvements to the portfolio, autonomy 1."),
    },
}

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = [name] if name != "all" else list(AGENTS)
    for a in targets:
        if a not in AGENTS:
            print(f"Unknown agent: {a}"); continue
        cfg = AGENTS[a]
        print(f"\n● {a} (autonomy set in company.yaml) — model {cfg['model']}")
        mem = read_memory()
        # pull real data from the matching DB
        tables = {
            "job_hunter": ("second_brain.db", "captures"),
            "content_ops": ("creator.db", "content"),
            "freelance_biz": ("finance.db", "transactions"),
            "pm_assistant": ("pm.db", "tasks"),
            "portfolio_builder": ("pm.db", "projects"),
            "reading_agent": ("reading.db", "links"),
        }
        dbfile, table = tables[a]
        rows = []
        try:
            conn = db(dbfile)
            rows = conn.execute(f"SELECT * FROM {table} LIMIT 10").fetchall()
            conn.close()
        except Exception as e:
            rows = [("no data",)]
        prompt = cfg["prompt"] + f"\n\nOS MEMORY:\n{mem[:1500]}\n\nCURRENT DATA ({table}):\n{rows}"
        out = call_llm(prompt, cfg["model"])
        print(out[:1200])
        log_run(a, "run complete", out[:120])
        # Job-hunter: queue outreach/follow-up drafts for approval
        if a == "job_hunter":
            queue_for_approval("job_hunter", "outreach-followup",
                               {"recommendations": out[:800], "execute": "draft_message"})

if __name__ == "__main__":
    main()
