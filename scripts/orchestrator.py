#!/usr/bin/env python3
"""Richard OS — Super-Orchestrator: route requests to domain trees."""
import sys, yaml, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAINS = {
    "company":  ROOT / "02-blocks" / "company"  / "departments.yaml",
    "home":     ROOT / "02-blocks" / "home"     / "home.yaml",
    "personal": ROOT / "02-blocks" / "personal" / "personal.yaml",
}

def load_domains():
    return {name: yaml.safe_load(p.read_text()) for name, p in DOMAINS.items() if p.exists()}

def find_agent(text, domains):
    """Naive intent routing: match keywords → domain → sub-agent."""
    text = text.lower()
    rules = {
        "company": ["hr", "recruit", "onboard", "onboarding", "new hire", "payroll", "invoice", "expense", "backend", "frontend", "tester", "support", "dev", "finance", "hire"],
        "home": ["light", "tv", "ac", "temperature", "camera", "lock", "kitchen", "bedroom", "fan", "alarm"],
        "personal": ["email", "mail", "calendar", "schedule", "meeting", "task", "remind", "expense", "money"],
    }
    for domain, kws in rules.items():
        for kw in kws:
            if kw in text:
                return domain, kw
    return None, None

def main():
    domains = load_domains()
    text = " ".join(sys.argv[1:])
    if not text:
        print("Usage: python scripts/orchestrator.py <your request>")
        print("  e.g. 'check my email for recruiters' → personal/email")
        print("  e.g. 'turn on living room lights'    → home/living-room")
        print("  e.g. 'any new backend tickets?'      → company/development")
        print("\nLoaded domains:", ", ".join(domains))
        return

    domain, agent = find_agent(text, domains)
    if not domain:
        print(f"❓ No domain matched for: {text!r}")
        print("   Add keywords to scripts/orchestrator.py find_agent()")
        return

    print(f"🧭 Routed to: {domain} → {agent}")
    tree = domains.get(domain, {})
    # Show the matching sub-tree
    for dept, agents in tree.get(domain, {}).items():
        names = [list(a.keys())[0] for a in agents] if isinstance(agents, list) else list(agents)
        if agent in dept or agent in names or any(agent in n for n in names):
            print(f"   📂 {dept}: {', '.join(names)}")
    print("\n(Next: dispatch to a real agent via agents_runner.py + MCP tools)")

if __name__ == "__main__":
    main()
