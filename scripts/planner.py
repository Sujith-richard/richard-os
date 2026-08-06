#!/usr/bin/env python3
"""
scripts/planner.py - #10 Planner AI
Turns a plain-English goal into a step plan in the WFS format:
steps of kind trigger / agent / data / approve / action.
Deterministic keyword templates (fake-first; LLM swap later via models integration).
"""
import re, datetime

def _slug(name):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return s or "plan"

def _steps_for(goal):
    g = goal.lower()
    if any(k in g for k in ("lead", "job", "prospect", "pipeline", "hire")):
        return [
            {"k": "trigger", "t": "New lead", "info": "second_brain"},
            {"k": "agent", "t": "Job Hunter", "info": "screens & scores"},
            {"k": "data", "t": "CRM update", "info": "crm.db"},
            {"k": "agent", "t": "Draft outreach", "info": "job_hunter"},
            {"k": "approve", "t": "Founder approval", "info": "approval queue"},
            {"k": "action", "t": "Send", "info": "outreach"},
        ]
    if any(k in g for k in ("email", "inbox", "triage", "reply")):
        return [
            {"k": "trigger", "t": "Email arrives", "info": "imap/comms"},
            {"k": "agent", "t": "Email Agent", "info": "triage"},
            {"k": "data", "t": "Classify", "info": "action-needed"},
            {"k": "agent", "t": "Draft reply", "info": "in your voice"},
            {"k": "approve", "t": "Founder approval", "info": "approval queue"},
            {"k": "action", "t": "Send reply", "info": "done"},
        ]
    if any(k in g for k in ("brief", "daily", "morning", "summary")):
        return [
            {"k": "trigger", "t": "Scheduled time", "info": "scheduler"},
            {"k": "agent", "t": "Agents run", "info": "jobs/tasks/finance"},
            {"k": "data", "t": "Collect", "info": "all systems"},
            {"k": "action", "t": "Morning Brief", "info": "one screen"},
        ]
    if any(k in g for k in ("content", "post", "publish", "social", "blog")):
        return [
            {"k": "trigger", "t": "Content idea", "info": "creator.db"},
            {"k": "agent", "t": "Content Ops", "info": "drafts"},
            {"k": "data", "t": "Schedule", "info": "calendar"},
            {"k": "approve", "t": "Founder approval", "info": "approval queue"},
            {"k": "action", "t": "Publish", "info": "social"},
        ]
    # generic fallback
    return [
        {"k": "trigger", "t": "Request received", "info": "orchestrator"},
        {"k": "agent", "t": "Route to department", "info": "department layer"},
        {"k": "data", "t": "Gather context", "info": "systems of record"},
        {"k": "approve", "t": "Founder approval", "info": "approval queue"},
        {"k": "action", "t": "Execute", "info": "deliverable"},
    ]

def plan_from_goal(goal):
    """Return a plan dict (name/goal/steps) for a goal string."""
    title = goal.split("\n")[0].strip()[:60] or "Untitled plan"
    name = _slug(title)
    return {"name": name, "title": title, "goal": goal, "steps": _steps_for(goal),
            "planned_at": datetime.datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    import sys, json
    goal = sys.argv[1] if len(sys.argv) > 1 else "Plan: process new job lead into pipeline"
    print(json.dumps(plan_from_goal(goal), indent=2))
