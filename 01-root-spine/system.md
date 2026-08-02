# Richard OS — System

Richard OS is a file-based AI operating system for one person: Sujith Richard.
It runs the job hunt, freelance business, learning, and portfolio from one folder
the AI reads before every task.

## The four layers
1. Memory — who you are, your skills, goals, offer
2. Tools — systems of record (second brain, PM, finance, CRM, creator)
3. Agents — named workers with honest run logs
4. Skills — repeatable moves written down with evidence

## How it runs
- Agents read `01-root-spine/` + memory before acting
- Tools live in `05-systems-of-record/` (SQLite-backed)
- Every run is logged in `03-agents/*/logs/`
- Schedules fire from `07-schedules/`

## Cross-platform
100% Python + SQLite + web UI. Runs on Linux, macOS, Windows.
All paths relative to repo root. Never hardcode /home/... or C:\...
