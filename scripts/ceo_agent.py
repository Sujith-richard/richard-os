#!/usr/bin/env python3
"""Richard OS — CEO agent: reads every agent's output, ranks priorities,
and queues decisions. The final decision layer over the roster."""
import json, sqlite3, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "03-agents" / "logs"
DATA = ROOT / "06-data"

def collect_state():
    """Pull the OS state: pending approvals, open tasks, deals, agent logs."""
    state = {}
    # pending approvals
    try:
        conn = sqlite3.connect(DATA / "approvals.db")
        n = conn.execute("SELECT COUNT(*) FROM approvals WHERE status='pending'").fetchone()[0]
        conn.close()
        state["pending_approvals"] = n
    except Exception:
        state["pending_approvals"] = 0
    # open tasks
    try:
        conn = sqlite3.connect(DATA / "pm.db")
        open_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'done'").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'done' AND priority='high'").fetchone()[0]
        conn.close()
        state["open_tasks"] = open_tasks
        state["high_priority_tasks"] = high
    except Exception:
        state["open_tasks"] = 0; state["high_priority_tasks"] = 0
    # pipeline
    try:
        conn = sqlite3.connect(DATA / "crm.db")
        deals = conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
        conn.close()
        state["deals"] = deals
    except Exception:
        state["deals"] = 0
    # agent runs today (from logs)
    today = datetime.now().strftime("%Y-%m-%d")
    runs = 0
    for lf in LOGS.rglob("*.md"):
        runs += sum(1 for line in lf.read_text().splitlines() if line.startswith(today))
    state["agent_runs_today"] = runs
    return state

def build_brief(state):
    """Write the CEO brief — what needs attention first."""
    lines = [f"# CEO Brief — {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    lines.append("## What needs attention first")
    prio = []
    if state["pending_approvals"]:
        prio.append(f"- Approve/review {state['pending_approvals']} pending draft(s) — autonomy-2 agents are waiting [blocking]")
    if state["high_priority_tasks"]:
        prio.append(f"- {state['high_priority_tasks']} high-priority task(s) open — recommend clearing these first")
    if state["deals"]:
        prio.append(f"- {state['deals']} deal(s) in pipeline — review funnel for movement")
    lines += prio or ["- All clear — nothing urgent detected."]
    lines += [""]
    lines.append("## System status")
    lines.append(f"- Open tasks: {state['open_tasks']} · High priority: {state['high_priority_tasks']}")
    lines.append(f"- Pending approvals: {state['pending_approvals']} · Deals: {state['deals']}")
    lines.append(f"- Agent runs today: {state['agent_runs_today']}")
    lines += ["", "## Decisions queued"]
    lines.append("- (decisions land here as agents complete work — approve in the Approvals page)")
    return "\n".join(lines)

if __name__ == "__main__":
    state = collect_state()
    print(build_brief(state))
    # save to 07-schedules/briefs/ceo-brief.md
    briefs = ROOT / "07-schedules" / "briefs"
    briefs.mkdir(exist_ok=True)
    (briefs / "ceo-brief.md").write_text(build_brief(state))
    print(f"\n✓ Saved to 07-schedules/briefs/ceo-brief.md")
