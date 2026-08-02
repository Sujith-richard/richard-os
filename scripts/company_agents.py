#!/usr/bin/env python3
"""Richard OS — Company hierarchy: department → employee agents.
Each employee agent has a role, autonomy level, and uses MCP tools + SQLite."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_lib import call_llm, log_run, read_memory, call_tool
from orchestrator import load_domains, find_agent

COMPANY = {
    "hr": {
        "recruiter":   {"autonomy": 2, "model": "deepseek-v4-flash-free", "tools": ["web"], "db": "crm.db"},
        "payroll":     {"autonomy": 3, "model": "deepseek-v4-flash-free", "tools": [], "db": "finance.db"},
        "onboarding":  {"autonomy": 2, "model": "deepseek-v4-flash-free", "tools": [], "db": "crm.db"},
    },
    "development": {
        "backend":     {"autonomy": 3, "model": "deepseek-v4-flash-free", "tools": ["github"], "db": "pm.db"},
        "frontend":    {"autonomy": 3, "model": "deepseek-v4-flash-free", "tools": ["github"], "db": "pm.db"},
        "tester":      {"autonomy": 2, "model": "deepseek-v4-flash-free", "tools": [], "db": "pm.db"},
    },
    "finance": {
        "invoicing":   {"autonomy": 2, "model": "deepseek-v4-flash-free", "tools": [], "db": "finance.db"},
        "expense":     {"autonomy": 3, "model": "deepseek-v4-flash-free", "tools": [], "db": "finance.db"},
    },
    "operations": {
        "fulfillment": {"autonomy": 3, "model": "deepseek-v4-flash-free", "tools": [], "db": "pm.db"},
        "support":     {"autonomy": 2, "model": "deepseek-v4-flash-free", "tools": ["web"], "db": "crm.db"},
    },
}

def dispatch(dept, employee, task):
    cfg = COMPANY.get(dept, {}).get(employee)
    if not cfg:
        return f"Unknown employee agent: {dept}/{employee}"
    mem = read_memory()[:1500]
    # Pull real data from the employee's system of record
    import sqlite3
    db_path = Path(__file__).resolve().parent.parent / "06-data" / cfg["db"]
    rows = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if tables:
            rows = [dict(r) for r in conn.execute(f"SELECT * FROM {tables[0]} LIMIT 8").fetchall()]
        conn.close()
    except Exception:
        pass
    # MCP tools available
    tool_hint = ""
    if cfg["tools"]:
        tool_hint = f"Tools available: {', '.join(cfg['tools'])}. Use call_tool() if needed."
    prompt = (f"You are the {employee} agent in the {dept} department. Autonomy level {cfg['autonomy']}. "
              f"{tool_hint}\nTask: {task}\n\nOS MEMORY:\n{mem}\n\nCURRENT DATA:\n{rows}")
    out = call_llm(prompt, cfg["model"])
    print(out[:1200])
    log_run(f"company/{dept}/{employee}", "run complete", out[:120])

def main():
    text = " ".join(sys.argv[1:])
    if not text:
        print("Usage: python scripts/company_agents.py <task>")
        print("  e.g. 'draft an onboarding checklist for new hire'")
        print("  e.g. 'summarize open backend tickets'")
        print("  e.g. 'check for invoices due'")
        return
    domains = load_domains()
    domain, agent = find_agent(text, domains)
    if domain != "company" or not agent:
        print(f"❓ Not a company request, or no employee matched: {text!r}")
        return
    # map keyword → dept/employee
    mapping = {
        "recruit": ("hr", "recruiter"), "payroll": ("hr", "payroll"), "onboard": ("hr", "onboarding"),
        "backend": ("development", "backend"), "frontend": ("development", "frontend"),
        "tester": ("development", "tester"), "test": ("development", "tester"),
        "invoice": ("finance", "invoicing"), "expense": ("finance", "expense"),
        "fulfill": ("operations", "fulfillment"), "support": ("operations", "support"),
    }
    if agent not in mapping:
        print(f"❓ No employee agent for keyword '{agent}'")
        return
    dept, employee = mapping[agent]
    print(f"🧭 Company → {dept}/{employee}")
    dispatch(dept, employee, text)

if __name__ == "__main__":
    main()
