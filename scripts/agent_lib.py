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

def read_memory():
    """Read the root spine + any memory files so agents never re-explain."""
    texts = []
    spine = ROOT / "01-root-spine"
    for f in sorted(spine.glob("*.md")):
        texts.append(f"--- {f.name} ---\n" + f.read_text()[:2000])
    return "\n".join(texts)

def call_llm(prompt, model="deepseek-v4-flash-free"):
    """Call FreeLLMAPI (or OpenCode proxy) with the given prompt."""
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
