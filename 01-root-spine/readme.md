# Richard OS

A personal AI operating system: memory, tools, agents, and skills
in one folder your AI runs.

## Boot
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py

## Structure
- 01-root-spine/        system, encoding, invariants, config
- 02-blocks/            departments (job-hunt, marketing, sales, finance, content, ops)
- 03-agents/            named workers + logs
- 04-skills/            repeatable moves
- 05-systems-of-record/ CRM, finance, PM, content, second brain
- 06-data/              SQLite DBs
- 07-schedules/         cron scripts + automations
