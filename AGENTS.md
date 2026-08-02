# Richard OS — agent rules

This file gives any AI agent (Claude, Codex, or a future worker) the house
rules for working in this repo. Read it before making changes.

## Non-negotiables
- Never commit secrets. Credentials live in .env (gitignored).
- Fake-data-first: DATA_MODE=fake. Real integrations attach only at the very end.
- Every run is logged. No silent actions.
- Nothing ships past the autonomy level set in company.yaml.

## How to work
- TDD where practical: a failing check first, then the implementation.
- Everything reads through the repo layer (scripts/ + SQLite in 06-data/),
  never raw queries from a page.
- New data = a new seed entry in scripts/seed_data.py + a repo method + a test.
- Keep run.py, init_db.py, seed_data.py idempotent and cross-platform.

## Commands
- python3 run.py              boot check
- python3 scripts/init_db.py  create DBs
- python3 scripts/seed_data.py  seed (idempotent)
- python3 scripts/agents_runner.py all   run the roster
- python3 -m uvicorn scripts.server:app --reload --port 8000  UI

## Multi-agent etiquette
- Commit small and often; git log --oneline to see where others are.
- Don't edit a file another session has uncommitted changes in.
