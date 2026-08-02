#!/usr/bin/env python3
"""Richard OS — Morning Brief: one summary of everything that needs you today."""
import sqlite3
from pathlib import Path
from datetime import date

DATA = Path(__file__).resolve().parent.parent / "06-data"

def q(db_name, sql):
    conn = sqlite3.connect(DATA / db_name)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def main():
    brief = []
    brief.append(f"# Morning Brief — {date.today().isoformat()}")
    brief.append("")

    # Jobs (second_brain)
    try:
        jobs = q("second_brain.db", "SELECT title, status FROM captures WHERE status IN ('job','inbox') LIMIT 10")
        brief.append("## 🎯 Jobs / Leads")
        for j in jobs:
            brief.append(f"- {j['title']} [{j['status']}]")
    except Exception:
        pass

    # Tasks (pm)
    try:
        tasks = q("pm.db", "SELECT title, status, priority FROM tasks WHERE status != 'done' LIMIT 10")
        brief.append("\n## ✅ Tasks due")
        for t in tasks:
            brief.append(f"- {t['title']} [{t['status']} / {t['priority']}]")
    except Exception:
        pass

    # Finance
    try:
        tx = q("finance.db", "SELECT kind, amount, note FROM transactions LIMIT 10")
        brief.append("\n## 💰 Recent transactions")
        for t in tx:
            brief.append(f"- {t['kind']}: ${t['amount']} — {t['note']}")
    except Exception:
        pass

    # Contacts
    try:
        c = q("crm.db", "SELECT name, company, stage FROM contacts LIMIT 10")
        brief.append("\n## 👥 Contacts")
        for x in c:
            brief.append(f"- {x['name']} @ {x['company']} [{x['stage']}]")
    except Exception:
        pass

    out = "\n".join(brief)
    print(out)

    # Save to 07-schedules/briefs/
    briefs_dir = Path(__file__).resolve().parent.parent / "07-schedules" / "briefs"
    briefs_dir.mkdir(exist_ok=True)
    (briefs_dir / f"brief-{date.today().isoformat()}.md").write_text(out)
    print(f"\n📄 Saved to 07-schedules/briefs/brief-{date.today().isoformat()}.md")

if __name__ == "__main__":
    main()
