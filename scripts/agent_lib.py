#!/usr/bin/env python3
"""Richard OS — shared agent library: memory, logs, LLM calls."""
import sys, json, os, sqlite3, time
from datetime import datetime
from pathlib import Path
import httpx
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcp_bridge

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "06-data"
LOGS = ROOT / "03-agents" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

def load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    try:
        import sqlite3
        conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
        conn.row_factory = sqlite3.Row
        for r in conn.execute("SELECT provider, api_key, base_url FROM connections").fetchall():
            prov = (r["provider"] or "").upper()
            if r["api_key"]:
                os.environ.setdefault(f"{prov}_API_KEY", r["api_key"])
            if r["base_url"]:
                os.environ.setdefault(f"{prov}_URL", r["base_url"])
        conn.close()
    except Exception:
        pass

def read_memory():
    """Read the root spine + any memory files so agents never re-explain."""
    texts = []
    spine = ROOT / "01-root-spine"
    for f in sorted(spine.glob("*.md")):
        texts.append(f"--- {f.name} ---\n" + f.read_text()[:2000])
    return "\n".join(texts)

def call_llm(prompt, model=None, task_type="default", agent=None, context=None, dept="web", sub=None):
    """Call the model layer with the given prompt, routed by the Model Orchestrator.
    If model is None, the orchestrator picks per task_type (agent override wins).
    If context=True, the Context Assembly Engine packs the full OS envelope first."""
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from model_orchestrator import resolve_model
    if context:
        from context_assembly import assemble
        prompt = assemble(prompt, dept=dept, sub=sub) + "\n\nANSWER:"
    if model is None:
        r = resolve_model(task_type, agent)
        model = r["resolved"]
        import sys as _osys; print(f"[orchestrator] {task_type} -> {model} (tier {r['tier']})", file=_osys.stderr)
    load_env()
    url = os.environ.get("FREELLMAPI_URL", "http://localhost:3001/v1")
    key = os.environ.get("FREELLMAPI_KEY", "freellmapi-c049fbfe5ac7efae7133cf8aec333d78337827c19a644ed7")
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
    headers = {"Authorization": f"Bearer {key}"}
    try:
        r = httpx.post(f"{url}/chat/completions", json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM unavailable: {e}]"

def call_tool(name, params=None):
    """Agent-facing MCP tool call."""
    return mcp_bridge.call_tool(name, params)

def list_tools():
    return mcp_bridge.list_tools()

def queue_for_approval(agent, action, payload):
    """Queue a draft for human approval (autonomy-2 pattern)."""
    import subprocess, sys
    subprocess.run([sys.executable, "approval_queue.py", "add", agent, action,
                    __import__("json").dumps(payload)], cwd=str(Path(__file__).resolve().parent))

def log_run(agent, action, detail=""):
    """Append an honest run log line."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{stamp} | {agent} | {action} | {detail}\n"
    log_path = LOGS / f"{agent}.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"  ✍️  log: {agent} → {action}")

def db(name):
    return sqlite3.connect(DATA / name)

def latest_log(agent, n=5):
    f = LOGS / f"{agent}.md"
    if not f.exists():
        return "No runs yet."
    lines = f.read_text().splitlines()
    return "\n".join(lines[-n:])
