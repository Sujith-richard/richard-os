# Richard OS — Real Data Swap Playbook

> Rule: build everything on DATA_MODE=fake first. Attach real integrations ONLY
> at the very end, after the entire process is complete. This doc is the
> turnkey checklist for that final step.

## 1. The switch
Edit .env:
```bash
DATA_MODE=real
