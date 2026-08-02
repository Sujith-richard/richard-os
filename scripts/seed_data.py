#!/usr/bin/env python3
"""Richard OS — seed fake data into every system of record.
Run with DATA_MODE=fake. Real integrations replace this later."""
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "06-data"

def reset(name):
    conn = sqlite3.connect(DATA / name)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    for t in tables:
        conn.execute(f"DELETE FROM {t}")
    conn.commit()
    return conn

# ── second_brain: job leads ─────────────────────────
conn = reset("second_brain.db")
for title, note, source in [
    ("Data Scientist @ Google", "Applied via careers portal", "Google Careers"),
    ("ML Engineer @ Stripe", "Referred by Priya — follow up", "Referral"),
    ("AI Engineer @ Microsoft", "Recruiter reached out", "LinkedIn"),
    ("Data Engineer @ Razorpay", "Screening call scheduled", "Naukri"),
    ("Data Analyst @ Swiggy", "Application drafted — send", "Company site"),
    ("Senior DS @ Flipkart", "Applied, waiting response", "LinkedIn"),
]:
    conn.execute("INSERT INTO captures (title, note, source, status) VALUES (?,?,?, 'job')",
                 (title, note, source))
conn.commit(); conn.close()

# ── pm: projects + tasks ────────────────────────────
conn = reset("pm.db")
for name, client, value, status in [
    ("Richard OS v1", "Self", 0, "done"),
    ("AI-Workspace v1.1", "Self", 0, "done"),
    ("Portfolio Revamp", "Self", 0, "in_progress"),
    ("Freelance Dashboard", "Acme Corp", 25000, "proposal"),
    ("Chatbot MVP", "TechStart Ltd", 40000, "negotiation"),
]:
    conn.execute("INSERT INTO projects (name, client, value, status) VALUES (?,?,?,?)",
                 (name, client, value, status))
for title, project, status, priority in [
    ("Wire MCP into agents", "Richard OS v1", "todo", "high"),
    ("Seed fake data", "Richard OS v1", "todo", "high"),
    ("Build personal assistant", "Richard OS v1", "todo", "medium"),
    ("Deploy portfolio", "Portfolio Revamp", "in_progress", "high"),
    ("Send proposal to Acme", "Freelance Dashboard", "todo", "high"),
]:
    conn.execute("INSERT INTO tasks (title, project, status, priority) VALUES (?,?,?,?)",
                 (title, project, status, priority))
conn.commit(); conn.close()

# ── finance: accounts + transactions ────────────────
conn = reset("finance.db")
for name, type_, balance in [
    ("JP Morgan", "checking", 6200.00),
    ("City Bank", "checking", 5315.00),
    ("Paypal", "withdrawal", 846.00),
    ("Binance", "crypto", 570.00),
    ("Payoneer", "business", 200.00),
]:
    conn.execute("INSERT INTO accounts (name, type, balance) VALUES (?,?,?)", (name, type_, balance))
for kind, account, amount, note in [
    ("income", "Payoneer", 4650.00, "Freelance payout — Acme"),
    ("expense", "Paypal", 25.00, "HuggingFace subscription"),
    ("expense", "City Bank", 1200.00, "Rent"),
    ("income", "Paypal", 800.00, "Consulting"),
    ("expense", "JP Morgan", 540.00, "Groceries"),
]:
    conn.execute("INSERT INTO transactions (kind, account, amount, note) VALUES (?,?,?,?)",
                 (kind, account, amount, note))
conn.commit(); conn.close()

# ── crm: contacts + deals ───────────────────────────
conn = reset("crm.db")
for name, company, email, stage in [
    ("Priya Sharma", "Acme Corp", "priya@acme.com", "client"),
    ("Rahul Verma", "TechStart Ltd", "rahul@techstart.io", "lead"),
    ("Ananya Iyer", "Finnovate", "ananya@finnovate.com", "lead"),
    ("Karthik Nair", "Google", "karthik.nair@google.com", "recruiter"),
    ("Sarah Chen", "Stripe", "sarah.chen@stripe.com", "recruiter"),
]:
    conn.execute("INSERT INTO contacts (name, company, email, stage) VALUES (?,?,?,?)",
                 (name, company, email, stage))
for title, company, value, stage in [
    ("Website Design Project", "Acme Corp", 25000, "proposal"),
    ("Software License Agreement", "TechStart Ltd", 40000, "needs-follow-up"),
    ("Marketing Campaign", "Finnovate", 35000, "negotiation"),
    ("Mobile App Development", "Acme Corp", 15000, "contract-pending"),
]:
    conn.execute("INSERT INTO deals (title, company, value, stage) VALUES (?,?,?,?)",
                 (title, company, value, stage))
conn.commit(); conn.close()

# ── creator: content ideas ──────────────────────────
conn = reset("creator.db")
for title, platform, status in [
    ("Why I built my own AI OS", "LinkedIn", "draft"),
    ("How agents work: autonomy 1-5", "LinkedIn", "idea"),
    ("Richard OS demo walkthrough", "YouTube", "idea"),
    ("My MCP tool bridge in 60s", "X", "draft"),
    ("Data Science projects showcase", "GitHub", "published"),
]:
    conn.execute("INSERT INTO content (title, platform, status) VALUES (?,?,?)",
                 (title, platform, status))
conn.commit(); conn.close()

print("✓ Seeded fake data into all 5 systems of record:")
print("  second_brain: 6 job leads")
print("  pm:           5 projects, 5 tasks")
print("  finance:      5 accounts, 5 transactions")
print("  crm:          5 contacts, 4 deals")
print("  creator:      5 content items")
print("\nRun agents now — they'll work against rich fake data.")
