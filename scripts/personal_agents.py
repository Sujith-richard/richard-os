#!/usr/bin/env python3
"""Richard OS — Personal Assistant: email triage, calendar, reminders.
Fake-data first; real Gmail/calendar swaps in via DATA_MODE later."""
import sys, json, re, sqlite3
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_lib import call_llm, log_run, read_memory, call_tool, queue_for_approval

DATA = Path(__file__).resolve().parent.parent / "06-data"

def q(db_name, sql):
    conn = sqlite3.connect(DATA / db_name)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _read_inbox():
    """Read real Gmail if a GMAIL connection is saved; else fall back to fake inbox."""
    # v3.4 hub-first: use live_gmail.json when the Gmail integration is LIVE
    try:
        from integrations import resolve_source
        live = resolve_source("gmail")
    except Exception:
        live = None
    if live:
        try:
            import json as j
            d = j.loads(live.read_text())
            msgs = d.get("messages", [])
            out = [{"from_addr": m.get("from", ""), "subject": m.get("subject", ""),
                    "body": m.get("date", ""), "status": "unread"} for m in msgs]
            if out:
                print("(live Gmail via hub - " + str(len(out)) + " emails)")
                return out
        except Exception as e:
            print("(live gmail parse failed, using fake:", str(e)[:80], ")")
    try:
        import sqlite3, os as _os
        c = sqlite3.connect(Path(__file__).resolve().parent.parent / "06-data" / "connections.db")
        c.row_factory = sqlite3.Row
        row = c.execute("SELECT api_key, base_url FROM connections WHERE upper(provider)='GMAIL'").fetchone()
        c.close()
    except Exception:
        row = None
    if row and row["base_url"]:
        import imaplib, email as em
        user = row["base_url"]
        token = row["api_key"] or ""
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(user, token)
            imap.select("INBOX")
            _, ids = imap.search(None, "ALL")
            out = []
            for num in ids[0].split()[:5]:
                _, data = imap.fetch(num, "(RFC822)")
                msg = em.message_from_bytes(data[0][1])
                body = ""
            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", "ignore")[:500]
                            break
                else:
                    body = str(msg.get_payload())[:500]
            except Exception:
                body = str(msg.get_payload())[:500]
            out.append({"from_addr": msg["From"], "subject": msg["Subject"], "body": body, "status": "unread"})
            imap.logout()
            if out:
                print("(real Gmail inbox — " + str(len(out)) + " emails)")
                return out
        except Exception as e:
            print("(Gmail connect failed, using fake:", str(e)[:80], ")")
    # fake fallback
    return q("second_brain.db", "SELECT * FROM inbox ORDER BY id LIMIT 10")

def triage_email():
    """Email agent: read inbox, flag what needs you (autonomy 2)."""
    emails = _read_inbox()
    mem = read_memory()[:1200]
    prompt = (
        "You are the email triage agent. Autonomy 2 (recommend only).\n"
        "Classify each email: action-needed / info / newsletter. "
        "For action-needed, draft a 1-line reply. Reply ONLY with a JSON array "
        'like [{"from": "...", "subject": "...", "reply": "..."}] '
        "for action-needed emails only.\n\nINBOX:\n" + str(emails) + "\n\nOS MEMORY:\n" + mem[:1200]
    )
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run("personal/email", "triage", out[:120])
    # Queue action-needed drafts for approval (autonomy 2 -> human approves)
    try:
        m = re.search(r"\[.*\]", out, re.DOTALL)
        if m:
            for d in json.loads(m.group(0)):
                if isinstance(d, dict) and d.get("reply"):
                    queue_for_approval("personal/email", "send-reply", {
                        "to": d.get("from", ""), "subject": d.get("subject", ""),
                        "body": d["reply"], "execute": "send_email"})
    except Exception as e:
        log_run("personal/email", "queue-error", str(e))
    # mark read
    conn = sqlite3.connect(DATA / "second_brain.db")
    conn.execute("UPDATE inbox SET status='read'")
    conn.commit(); conn.close()

def calendar_summary():
    """Calendar agent: upcoming events + prep (autonomy 2)."""
    events = q("second_brain.db", "SELECT * FROM calendar WHERE status='upcoming' ORDER BY when_date LIMIT 10")
    mem = read_memory()[:1000]
    prompt = (
        "You are the calendar agent. Autonomy 2 (recommend only).\n"
        "List upcoming events and give prep tips for each.\n\nCALENDAR:\n" + str(events) + "\n\nOS MEMORY:\n" + mem[:1000]
    )
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run("personal/calendar", "summary", out[:120])

def reminder():
    """Reminder agent: check due tasks + follow-ups (autonomy 3)."""
    tasks = q("pm.db", "SELECT title, status, priority FROM tasks WHERE status != 'done' LIMIT 10")
    jobs = q("second_brain.db", "SELECT title, note FROM captures WHERE status='job' LIMIT 10")
    mem = read_memory()[:1000]
    prompt = (
        "You are the reminder agent. Autonomy 3 (flag blockers, escalate odd ones).\n"
        "Find what's due soon and flag anything needing urgent attention.\n\nTASKS:\n" + str(tasks) +
        "\n\nJOBS:\n" + str(jobs) + "\n\nOS MEMORY:\n" + mem[:1000]
    )
    out = call_llm(prompt, "deepseek-v4-flash-free")
    print(out[:1400])
    log_run("personal/reminders", "scan", out[:120])

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    actions = {"email": triage_email, "calendar": calendar_summary, "reminder": reminder}
    if cmd in actions:
        actions[cmd]()
    elif cmd == "all":
        for fn in actions.values():
            fn(); print("─" * 50)
    else:
        print("Usage: python scripts/personal_agents.py [email|calendar|reminder|all]")

if __name__ == "__main__":
    main()
