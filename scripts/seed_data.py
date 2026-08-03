#!/usr/bin/env python3
"""Richard OS — seed fake data into every system of record.
Run with DATA_MODE=fake. Real integrations replace this later."""
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "06-data"

def reset(name):
    """Idempotent: clears tables so re-seeding never duplicates, but keeps schema."""
    conn = sqlite3.connect(DATA / name)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    for t in tables:
        conn.execute(f"DELETE FROM {t}")
    conn.commit()
    return conn

def ensure_table(conn, name, ddl):
    """Create table if missing (keeps schema stable across re-seeds)."""
    conn.execute(ddl)
    conn.commit()

# ── second_brain: job leads (salary + applied date) ──
conn = reset("second_brain.db")
# add columns if missing (idempotent)
for col, ddl in [("salary", "TEXT"), ("applied_date", "TEXT")]:
    try:
        conn.execute(f"ALTER TABLE captures ADD COLUMN {col} {ddl}")
    except Exception:
        pass
conn.commit()
for title, note, source, salary, applied in [
    ("Data Scientist @ Google", "Applied via careers portal", "Google Careers", "$145K-$175K", "2026-07-25"),
    ("ML Engineer @ Stripe", "Referred by Priya — follow up", "Referral", "$160K-$200K", "2026-07-22"),
    ("AI Engineer @ Microsoft", "Recruiter reached out", "LinkedIn", "$150K-$180K", "2026-07-20"),
    ("Data Engineer @ Razorpay", "Screening call scheduled", "Naukri", "₹28L-₹36L", "2026-07-18"),
    ("Data Analyst @ Swiggy", "Application drafted — send", "Company site", "₹18L-₹24L", "2026-07-28"),
    ("Senior DS @ Flipkart", "Applied, waiting response", "LinkedIn", "₹32L-₹42L", "2026-07-15"),
    ("Applied Scientist @ Amazon", "Recruiter screening next week", "LinkedIn", "$165K-$210K", "2026-07-26"),
    ("ML Ops Engineer @ Zoho", "Resume shortlisted", "Company site", "₹24L-₹30L", "2026-07-21"),
    ("Data Scientist @ Salesforce", "Applied via portal", "Careers", "$140K-$170K", "2026-07-19"),
    ("GenAI Engineer @ NVIDIA", "Portfolio reviewed — stage 2", "Referral", "$170K-$220K", "2026-07-17"),
]:
    conn.execute("INSERT INTO captures (title, note, source, status, salary, applied_date) VALUES (?,?,?, 'job', ?, ?)",
                 (title, note, source, salary, applied))
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

# ── social: 60-day deterministic growth series (idempotent) ─────
conn = sqlite3.connect(DATA / "social.db")
conn.execute("CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT, day TEXT, followers INTEGER, source TEXT DEFAULT 'seed')")
conn.execute("DELETE FROM stats")
import math, datetime
def ramp(start, end, seed, n=60):
    out = []
    for i in range(n):
        t = i / (n - 1)
        trend = start + (end - start) * (0.7 * t + 0.3 * t * t)
        wobble = (math.sin(i * 0.7 + seed) * 0.6 + math.sin(i * 0.27 + seed * 2) * 0.4) * (end - start) * 0.012
        v = max(0, round(trend + wobble))
        out.append(v if i < n - 1 else end)
    return out
TARGETS = [("linkedin", 900, 2600), ("github", 45, 210), ("x", 300, 740), ("youtube", 120, 480)]
today = datetime.date.today()
for platform, start, end in TARGETS:
    series = ramp(start, end, hash(platform) % 100)
    for i, f in enumerate(series):
        day = (today - datetime.timedelta(days=59 - i)).isoformat()
        conn.execute("INSERT INTO stats (platform, day, followers) VALUES (?,?,?)", (platform, day, f))
conn.commit(); conn.close()

# ── 2. More deals in CRM ─────────────────────────────────────
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
    ("AI Chatbot MVP", "TechStart Ltd", 18000, "proposal"),
    ("Data Pipeline Build", "Cloudly", 32000, "negotiation"),
    ("ML Model Audit", "Finnovate", 12000, "prospect"),
    ("Dashboard Revamp", "Cloudly", 9500, "needs-follow-up"),
    ("E-commerce Integration", "ShopWave", 28000, "prospect"),
    ("CRM Migration", "Acme Corp", 21000, "contract-pending"),
    ("E-commerce Integration", "ShopWave", 28000, "lost"),
    ("CRM Migration", "Acme Corp", 21000, "lost"),
]:
    conn.execute("INSERT INTO deals (title, company, value, stage) VALUES (?,?,?,?)", (title, company, value, stage))
conn.commit(); conn.close()

# ── 3. More transactions over 3 months ───────────────────────
conn = reset("finance.db")
for name, type_, balance in [("JP Morgan", "checking", 6200.0), ("City Bank", "checking", 5315.0), ("Paypal", "withdrawal", 846.0), ("Binance", "crypto", 570.0), ("Payoneer", "business", 200.0)]:
    conn.execute("INSERT INTO accounts (name, type, balance) VALUES (?,?,?)", (name, type_, balance))
import datetime as dt2
rows = [
    ("income", "Payoneer", 4650, "Freelance payout — Acme", -0),
    ("expense", "Paypal", 25, "HuggingFace subscription", -1),
    ("expense", "City Bank", 1200, "Rent", -3),
    ("income", "Paypal", 800, "Consulting", -5),
    ("expense", "JP Morgan", 540, "Groceries", -7),
    ("income", "Payoneer", 3200, "Freelance payout — TechStart", -12),
    ("expense", "City Bank", 220, "Cloud hosting", -14),
    ("income", "Paypal", 450, "Mentoring session", -18),
    ("expense", "JP Morgan", 160, "Figma subscription", -21),
    ("income", "Payoneer", 5100, "Freelance payout — Finnovate", -26),
    ("expense", "Paypal", 99, "Domain renewals", -30),
    ("expense", "City Bank", 340, "Electricity", -34),
    ("income", "Paypal", 600, "Consulting — Cloudly", -38),
    ("expense", "JP Morgan", 130, "Netflix", -41),
    ("income", "Payoneer", 2750, "Freelance payout — ShopWave", -45),
    ("expense", "Paypal", 75, "Canva Pro", -50),
    ("expense", "City Bank", 260, "Internet", -55),
    ("income", "Paypal", 900, "Course sale", -59),
]
for kind, account, amount, note, days_back in rows:
    d = (dt2.date.today() - dt2.timedelta(days=days_back)).isoformat()
    conn.execute("INSERT INTO transactions (kind, account, amount, note, date) VALUES (?,?,?,?,?)", (kind, account, amount, note, d))
conn.commit(); conn.close()

# ── 4. More content items ─────────────────────────────────────
conn = reset("creator.db")
for title, platform, status in [
    ("Why I built my own AI OS", "LinkedIn", "draft"),
    ("How agents work: autonomy 1-5", "LinkedIn", "idea"),
    ("Richard OS demo walkthrough", "YouTube", "idea"),
    ("My MCP tool bridge in 60s", "X", "draft"),
    ("Data Science projects showcase", "GitHub", "published"),
    ("The fake-data-first strategy", "LinkedIn", "scheduled"),
    ("MCP layer explained in 3 mins", "YouTube", "script"),
    ("Screenshot tour of the brain graph", "X", "draft"),
    ("Building an AI OS in public", "LinkedIn", "published"),
    ("Approval queue: agents act, you approve", "LinkedIn", "idea"),
    ("Persona rosters: staffed teams", "LinkedIn", "draft"),
    ("Terminal aesthetics for AI tools", "X", "idea"),
    ("SQLite vs MySQL for your OS", "Blog", "scheduled"),
    ("How the scheduler runs my day", "YouTube", "idea"),
    ("Honest run logs in agents", "LinkedIn", "published"),
]:
    conn.execute("INSERT INTO content (title, platform, status) VALUES (?,?,?)", (title, platform, status))
conn.commit(); conn.close()

# ── content performance metrics (AFTER content insert) ─
pconn = sqlite3.connect(DATA / "creator.db")
content_ids = [r[0] for r in pconn.execute("SELECT id FROM content ORDER BY id").fetchall()]
import random as _r; _r.seed(42)
pconn.execute("CREATE TABLE IF NOT EXISTS performance (id INTEGER PRIMARY KEY AUTOINCREMENT, content_id INTEGER, views INTEGER, likes INTEGER, comments INTEGER, date TEXT)")
pconn.execute("DELETE FROM performance")
for cid in content_ids:
    for days_back in (0, 3, 7, 14):
        views = _r.randint(400, 9000)
        likes = int(views * _r.uniform(0.03, 0.09))
        comments = int(likes * _r.uniform(0.05, 0.2))
        d = (dt2.date.today() - dt2.timedelta(days=days_back)).isoformat()
        pconn.execute("INSERT INTO performance (content_id, views, likes, comments, date) VALUES (?,?,?,?,?)",
                      (cid, views, likes, comments, d))
pconn.commit(); pconn.close()


# ── reading: your real curated links collection ──────
conn = sqlite3.connect(DATA / "reading.db")
conn.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, category TEXT, status TEXT DEFAULT 'unread')")
conn.execute("DELETE FROM links")
links = [
    ("The Founder OS", "https://thefounderos.com", "course"),
    ("Referral request template", "https://example.com/referral-template", "job-hunt"),
    ("AI-Workspace v1.1", "https://github.com/Sujith-richard/AI-Workspace", "project"),
    ("How to Use Claude Code Free", "https://docs.google.com/document/d/1DDnA0hSpdz6ZvWSU3w8NCjiugZHvXGdTbfUx2MBt764", "ai"),
    ("Auto Edit AI", "https://autoeditai.net", "tool"),
    ("OpenCode", "https://opencode.ai", "ai"),
    ("The 100K Job Playbook", "https://wave-pocket-284.notion.site/The-100K-Job-Playbook", "job-hunt"),
    ("BEST Resources Vault", "https://wave-pocket-284.notion.site/BEST-Resources-Vault", "job-hunt"),
    ("GitHub custom profile tutorial", "https://github.com/arifhaxn", "profile"),
    ("Nvidia free AI API", "https://build.nvidia.com", "ai"),
    ("Learn SQL/Excel/PowerBI free", "https://docs.google.com/document/d/13ARutMpdo0c2sNMcA2B8zLBwZpxiiLclOoJfk4ScLKw", "learning"),
    ("Automate Money Earn AI", "https://github.com/Conway-Research/automaton", "tool"),
    ("Auto Edit (Vyra)", "https://usevyra.com", "tool"),
    ("TreeMap Disk Visualizer", "https://github.com/Prithvi-Web/TreeMap-Disk-Visualizer", "tool"),
    ("AI job-search on your machine", "https://github.com/MadsLorentzen/ai-job-search", "job-hunt"),
    ("Download from 1800+ sites", "https://github.com/tonhowtf/omniget", "tool"),
    ("AI trending repos", "https://gittrend.io", "ai"),
    ("CuPy GPU NumPy", "https://github.com/cupy/cupy", "ai"),
    ("Free WhatsApp API", "https://github.com/evolution-foundation/evolution-go", "tool"),
    ("Build a LinkedIn Profile", "https://docs.google.com/file/d/1BeGXMGXOG0qDt14DwX4N2i4RqYx60f97", "profile"),
    ("Levels of DevOps", "https://learn.nextwork.org", "learning"),
    ("FounderOS Demo repo", "https://github.com/Bennettxai/FounderOS-DEMO", "course"),
    ("The 100K Playbook (Drive)", "https://docs.google.com/document/d/13ARutMpdo0c2sNMcA2B8zLBwZpxiiLclOoJfk4ScLKw", "learning"),
]
for t, u, c in links:
    conn.execute("INSERT INTO links (title, url, category) VALUES (?,?,?)", (t, u, c))
conn.commit(); conn.close()

# ── comms: multi-channel conversations (email, linkedin, x, whatsapp, slack, discord, calls) ──
conn = sqlite3.connect(DATA / "comms.db")
conn.execute("CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, contact TEXT, subject TEXT, body TEXT, sentiment TEXT, summary TEXT, suggested_reply TEXT, follow_up TEXT, status TEXT DEFAULT 'unread', ts TEXT)")
conn.execute("DELETE FROM conversations")
import random as rnd
rnd.seed(7)
channels = ["email", "linkedin", "x", "whatsapp", "slack", "discord", "calls"]
contacts = ["Priya Sharma", "Rahul Verma", "Ananya Iyer", "Karthik Nair", "Sarah Chen", "Alex Rivera", "Jordan Blake", "Grace Lin", "Marcus Webb", "Tayla Nguyen", "Noah Fields", "Elena Brooks"]
subjects = {
  "email": "Freelance proposal follow-up",
  "linkedin": "Connection request + job opportunity",
  "x": "Re: your AI OS thread",
  "whatsapp": "Can we sync this week?",
  "slack": "#general standup update",
  "discord": "community question about MCP",
  "calls": "Discovery call summary",
}
bodies = [
  "Hey, saw your work on the AI OS — really impressive. Would love to discuss a potential collaboration.",
  "Following up on the proposal we discussed last week. Any update on timing?",
  "Your thread on building an OS in one folder was excellent. Quick question on the approval queue.",
  "Can we schedule a call for Thursday? I have a few ideas that might fit your stack.",
  "The demo you shared was great. What does the onboarding look like for a new client?",
  "Noticed you're hiring — I know a great data engineer who might be a fit.",
  "Quick question: how does the scheduler handle failed runs?",
]
sents = ["positive", "neutral", "positive", "neutral", "negative", "positive", "neutral"]
for i in range(40):
    ch = channels[i % len(channels)]
    c = contacts[i % len(contacts)]
    body = bodies[i % len(bodies)]
    sent = sents[i % len(sents)]
    summary = f"{sent.title()} — {c} discussing {subjects[ch].lower()}"
    reply = "Thanks for reaching out — happy to sync this week. What time works?"
    follow = "3 days" if sent == "positive" else "1 week"
    days = i % 14
    ts = f"2026-08-{max(1, 19 - days)}T{10 + i % 8}:{i % 60:02d}:00"
    conn.execute("INSERT INTO conversations (channel, contact, subject, body, sentiment, summary, suggested_reply, follow_up, status, ts) VALUES (?,?,?,?,?,?,?,?, 'unread', ?)",
                 (ch, c, subjects[ch], body, sent, summary, reply, follow, ts))
conn.commit(); conn.close()

# ── integrations registry (honest statuses — never fake) ──
conn = sqlite3.connect(DATA / "integrations.db")
conn.execute("CREATE TABLE IF NOT EXISTS integrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, desc TEXT, status TEXT, last_sync TEXT, category TEXT)")
conn.execute("DELETE FROM integrations")
rows = [
    ("Gmail", "Unified inbox + email triage", "not_configured", "—", "Comms"),
    ("GitHub", "Dev agents query repos", "connected", "2 min ago", "Dev"),
    ("OpenCode Proxy", "Free model gateway (127.0.0.1:1234)", "connected", "just now", "AI"),
    ("FreeLLMAPI", "Model server (port 3001)", "error", "unreachable", "AI"),
    ("Home Assistant", "Room device control", "not_configured", "—", "Home"),
    ("Slack", "Channel digests", "disabled", "—", "Comms"),
    ("Stripe", "Payments + revenue", "not_configured", "—", "Finance"),
    ("Notion", "Workspace docs", "disabled", "—", "Knowledge"),
    ("MySQL", "Optional enterprise data layer", "not_configured", "—", "Data"),
    ("SQLite", "Default local data layer", "connected", "live", "Data"),
    ("Scheduler", "Cron + agent schedules", "connected", "live", "System"),
    ("Approval Queue", "Human-in-the-loop drafts", "connected", "live", "System"),
]
for name, desc, status, sync, cat in rows:
    conn.execute("INSERT INTO integrations (name, desc, status, last_sync, category) VALUES (?,?,?,?,?)",
                 (name, desc, status, sync, cat))
conn.commit(); conn.close()

# ── SCALE-UP: match the spec volume (deterministic, idempotent) ──
import random as R; R.seed(2026)
# role: more tasks + projects
pc = sqlite3.connect(DATA / "pm.db")
pc.execute("CREATE TABLE IF NOT EXISTS tasks_scaled (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, project TEXT, status TEXT, priority TEXT, assignee TEXT, due TEXT)")
pc.execute("DELETE FROM tasks_scaled")
pc.execute("CREATE TABLE IF NOT EXISTS projects_scaled (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, client TEXT, value REAL, status TEXT)")
pc.execute("DELETE FROM projects_scaled")
proj_names = ["AI OS v3", "Portfolio Revamp", "Freelance Dashboard", "Chatbot MVP", "Data Pipeline", "Client Portal", "ML Model", "Mobile App"]
for i in range(90):
    pc.execute("INSERT INTO tasks_scaled (title, project, status, priority, assignee, due) VALUES (?,?,?,?,?,?)",
               (f"Task {i+1}: {proj_names[i % len(proj_names)]} item", proj_names[i % len(proj_names)],
                ["todo","in_progress","done"][i % 3], round(R.random() * 3, 1),
                ["job_hunter","content_ops","pm_assistant","portfolio_builder"][i % 4], f"2026-08-{(i % 28)+1}"))
for i in range(40):
    pc.execute("INSERT INTO projects_scaled (name, client, value, status) VALUES (?,?,?,?)",
               (proj_names[i % len(proj_names)], f"Client {i % 8 + 1}", round(5000 + i * 137), ["prospect","active","done"][i % 3]))
pc.commit(); pc.close()

# role: more job leads
cb = sqlite3.connect(DATA / "second_brain.db")
for i in range(30):
    cb.execute("INSERT INTO captures (title, note, source, status, salary, applied_date) VALUES (?,?,?, 'job', ?, ?)",
               (f"Data Role {i+1} @ Company {chr(65 + i % 26)}", f"cooling/referral {i%3}", ["LinkedIn","Naukri","Careers"][i%3],
                f"${120 + (i%40)*5}K", f"2026-08-{(i%28)+1}"))
cb.commit(); cb.close()

# role: scale finance transactions to 60
fc = sqlite3.connect(DATA / "finance.db")
for i in range(42):
    kind = "income" if i % 2 == 0 else "expense"
    fc.execute("INSERT INTO transactions (kind, account, amount, note, date) VALUES (?,?,?,?,?)",
               (kind, ["Payoneer","City Bank","Paypal"][i % 3], round(200 + R.random() * 900, 2),
                f"auto txn {i}", f"2026-08-{(i % 28)+1}"))
fc.commit(); fc.close()

# role: more content + performance
cr = sqlite3.connect(DATA / "creator.db")
for i in range(25):
    cr.execute("INSERT INTO content (title, platform, status) VALUES (?,?,?)",
               (f"Piece {i+1}: {proj_names[i % len(proj_names)]}", ["LinkedIn","YouTube","X","Blog","GitHub"][i % 5], ["idea","draft","scheduled","published"][i % 4]))
cr.commit(); cr.close()

# ── finance: invoices, subscriptions, bills, categories ──
fc = sqlite3.connect(DATA / "finance.db")
fc.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, amount REAL, status TEXT, due TEXT)")
fc.execute("DELETE FROM invoices")
fc.execute("CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, cost REAL, cycle TEXT, next_bill TEXT)")
fc.execute("DELETE FROM subscriptions")
fc.execute("CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, due TEXT)")
fc.execute("DELETE FROM bills")
fc.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL)")
fc.execute("DELETE FROM categories")
for client, amt, status, due in [
    ("Acme Corp", 25000, "sent", "2026-08-10"), ("TechStart", 18000, "sent", "2026-08-12"),
    ("Finnovate", 12000, "paid", "2026-08-01"), ("Cloudly", 9500, "draft", "2026-08-15"),
    ("ShopWave", 28000, "sent", "2026-08-18"),
]:
    fc.execute("INSERT INTO invoices (client, amount, status, due) VALUES (?,?,?,?)", (client, amt, status, due))
for name, cost, cycle, next_bill in [
    ("HuggingFace", 25, "monthly", "2026-08-09"), ("Figma", 15, "monthly", "2026-08-11"),
    ("Cloud hosting", 60, "monthly", "2026-08-07"), ("Canva Pro", 12, "monthly", "2026-08-20"),
    ("Netflix", 13, "monthly", "2026-08-22"), ("Domain renewals", 99, "yearly", "2026-09-01"),
]:
    fc.execute("INSERT INTO subscriptions (name, cost, cycle, next_bill) VALUES (?,?,?,?)", (name, cost, cycle, next_bill))
for name, amt, due in [
    ("Rent", 1200, "2026-08-05"), ("Electricity", 340, "2026-08-08"), ("Internet", 260, "2026-08-14"),
    ("Groceries", 540, "2026-08-16"), ("Transport", 180, "2026-08-19"),
]:
    fc.execute("INSERT INTO bills (name, amount, due) VALUES (?,?,?)", (name, amt, due))
for name, amt in [("Subscriptions", 224), ("Rent", 1200), ("Food", 540), ("Cloud", 60), ("Transport", 180), ("Other", 300)]:
    fc.execute("INSERT INTO categories (name, amount) VALUES (?,?)", (name, amt))
fc.commit(); fc.close()

# ── connections: user-added API keys (real-data swap bridge) ──
conn = sqlite3.connect(DATA / "connections.db")
conn.execute("CREATE TABLE IF NOT EXISTS connections (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, provider TEXT, api_key TEXT, base_url TEXT, status TEXT DEFAULT 'not_configured', saved_at TEXT DEFAULT CURRENT_TIMESTAMP)")
conn.commit(); conn.close()

print("✓ Seeded fake data into all 5 systems of record:")
print("  second_brain: 10 job leads (salary + applied dates)")
print("  pm:           5 projects, 5 tasks")
print("  finance:      5 accounts, 18 transactions")
print("  crm:          5 contacts, 10 deals")
print("  creator:      15 content items + 60 performance rows")
print("  reading:      23 curated links")
print("\nRun agents now — they'll work against rich fake data.")
