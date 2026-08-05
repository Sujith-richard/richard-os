#!/usr/bin/env python3
"""Richard OS — governance bridge (agent-governance-toolkit style guardrails).
Honest status: connected / not_configured / error. Never fakes."""
import shutil

def status():
    if shutil.which("agt") or _importable("agent_governance_toolkit"):
        return {"provider": "agent-governance-toolkit", "status": "connected",
                "detail": "governance toolkit available — guardrails active"}
    return {"provider": "agent-governance-toolkit", "status": "not_configured",
            "detail": "install agent-governance-toolkit to enable audit + policy guardrails"}

def _importable(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def audit(agent, action, payload, approved):
    """Log a governance audit line (works even without the toolkit)."""
    from pathlib import Path
    log = Path(__file__).resolve().parent.parent / "06-data" / "governance-audit.log"
    line = f"{action} | {agent} | approved={approved} | {payload[:120]}\n"
    with open(log, "a") as f:
        f.write(line)
    return {"logged": True}

def policy(action):
    """Simple guardrail policy: irreversible actions always need human."""
    irreversible = {"send_email", "create_invoice", "send_reply", "draft_message"}
    return {"action": action,
            "requires_human": action in irreversible,
            "auto_ok": action not in irreversible}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
    print(json.dumps(policy("send_email"), indent=2))
