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

# ── personal: fake inbox + calendar ────────────────
conn = sqlite3.connect(DATA / "second_brain.db")
conn.execute("CREATE TABLE IF NOT EXISTS inbox (id INTEGER PRIMARY KEY AUTOINCREMENT, from_addr TEXT, subject TEXT, body TEXT, status TEXT DEFAULT 'unread')")
conn.execute("CREATE TABLE IF NOT EXISTS calendar (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, when_date TEXT, status TEXT DEFAULT 'upcoming')")
for frm, subj, body in [
    ("recruiter@stripe.com", "Interview scheduling", "Hi Sujith, can we schedule the technical round for next week?"),
    ("priya@acme.com", "Re: Freelance Dashboard proposal", "Looks good! When can you start?"),
    ("alert@github.com", "PR #42: MCP bridge merged", "Your pull request was merged successfully."),
    ("newsletter@datacamp.com", "Weekly digest", "Here are this week's data science articles."),
    ("hiring@google.com", "Application status update", "Thank you for applying to Data Scientist @ Google."),
]:
    conn.execute("INSERT INTO inbox (from_addr, subject, body) VALUES (?,?,?)", (frm, subj, body))
for title, when in [
    ("Razorpay screening call", "2026-08-04"),
    ("Acme proposal follow-up", "2026-08-03"),
    ("Portfolio demo", "2026-08-05"),
]:
    conn.execute("INSERT INTO calendar (title, when_date) VALUES (?,?)", (title, when))
conn.commit(); conn.close()

# ── reading: curated links + resources ─────────────
conn = sqlite3.connect(DATA / "reading.db")
conn.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, category TEXT, status TEXT DEFAULT 'unread')")
for title, url, cat in [
    ("The Founder OS", "https://thefounderos.com", "course"),
    ("Referral request template", "https://example.com/referral-template", "job-hunt"),
    ("AI-Workspace v1.1", "https://github.com/Sujith-richard/AI-Workspace", "project"),
    ("How to Use Claude Code Free", "https://docs.google.com/document/d/1DDnA0hSpdz6ZvWSU3w8NCjiugZHvXGdTbfUx2MBt764", "ai"),
    ("Auto Edit AI", "https://autoeditai.net", "tool"),
    ("OpenCode", "https://opencode.ai", "ai"),
    ("The 100K Job Playbook", "https://wave-pocket-284.notion.site/The-100K-Job-Playbook", "job-hunt"),
    ("GitHub custom profile tutorial", "https://github.com/arifhaxn", "profile"),
    ("Nvidia free AI API", "https://build.nvidia.com", "ai"),
    ("Learn SQL/Excel/PowerBI free", "https://docs.google.com/document/d/13ARutMpdo0c2sNMcA2B8zLBwZpxiiLclOoJfk4ScLKw", "learning"),
]:
    conn.execute("INSERT INTO links (title, url, category) VALUES (?,?,?)", (title, url, cat))
conn.commit(); conn.close()

print("✓ Seeded fake data into all 5 systems of record:")
print("  second_brain: 6 job leads")
print("  pm:           5 projects, 5 tasks")
print("  finance:      5 accounts, 5 transactions")
print("  crm:          5 contacts, 4 deals")
print("  creator:      5 content items")
print("\nRun agents now — they'll work against rich fake data.")
