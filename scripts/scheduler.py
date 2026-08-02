#!/usr/bin/env python3
"""Richard OS — scheduler: run agents on a schedule (cross-platform)."""
import time, subprocess, sys
from datetime import datetime

# Agent name -> list of HH:MM times (24h)
SCHEDULE = {
    "morning_brief":   ["07:00"],
    "job_hunter":      ["09:00"],
    "content_ops":     ["18:00"],  # Mon/Wed/Fri handled by weekday check below
    "freelance_biz":   ["12:00"],
    "pm_assistant":    ["08:00"],
    "portfolio_builder": ["09:30"],  # weekly, Monday
}
CONTENT_DAYS = {0, 2, 4}   # Mon, Wed, Fri
PORTFOLIO_DAY = 0          # Monday

def run(agent):
    if agent == "morning_brief":
        subprocess.run([sys.executable, "morning_brief.py"], cwd="scripts")
        return
    print(f"[{datetime.now():%H:%M:%S}] running {agent}...")
    subprocess.run([sys.executable, "agents_runner.py", agent], cwd="scripts")

def tick():
    now = datetime.now()
    hm = now.strftime("%H:%M")
    for agent, times in SCHEDULE.items():
        if hm in times:
            if agent == "content_ops" and now.weekday() not in CONTENT_DAYS:
                continue
            if agent == "portfolio_builder" and now.weekday() != PORTFOLIO_DAY:
                continue
            run(agent)

if __name__ == "__main__":
    print("Richard OS scheduler running (Ctrl+C to stop)...")
    while True:
        tick()
        time.sleep(30)
