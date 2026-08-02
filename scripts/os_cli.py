#!/usr/bin/env python3
"""Richard OS CLI — manage your systems of record."""
import sqlite3, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "06-data"

def db(name):
    return sqlite3.connect(DATA / name)

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python scripts/os_cli.py <command>")
        print("  add-job  |  log-expense  |  add-contact  |  add-task  |  add-content")
        return
    cmd = args[0]

    if cmd == "add-job":
        # second_brain: capture a job lead
        conn = db("second_brain.db")
        conn.execute("INSERT INTO captures (title, note, source, status) VALUES (?,?,?, 'job')",
                     (args[1], args[2] if len(args) > 2 else "", args[3] if len(args) > 3 else ""))
        conn.commit(); conn.close()
        print("✓ Job lead captured.")

    elif cmd == "log-expense":
        conn = db("finance.db")
        conn.execute("INSERT INTO transactions (kind, account, amount, note) VALUES ('expense', ?, ?, ?)",
                     (args[1] if len(args) > 1 else "cash", float(args[2]), args[3] if len(args) > 3 else ""))
        conn.commit(); conn.close()
        print("✓ Expense logged.")

    elif cmd == "add-contact":
        conn = db("crm.db")
        conn.execute("INSERT INTO contacts (name, company, email, stage) VALUES (?,?,?, 'lead')",
                     (args[1], args[2] if len(args) > 2 else "", args[3] if len(args) > 3 else ""))
        conn.commit(); conn.close()
        print("✓ Contact added.")

    elif cmd == "add-task":
        conn = db("pm.db")
        conn.execute("INSERT INTO tasks (title, project, status) VALUES (?,?, 'todo')",
                     (args[1], args[2] if len(args) > 2 else ""))
        conn.commit(); conn.close()
        print("✓ Task added.")

    elif cmd == "add-content":
        conn = db("creator.db")
        conn.execute("INSERT INTO content (title, platform, status) VALUES (?,?, 'idea')",
                     (args[1], args[2] if len(args) > 2 else ""))
        conn.commit(); conn.close()
        print("✓ Content idea saved.")

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
