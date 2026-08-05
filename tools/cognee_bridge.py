#!/usr/bin/env python3
"""Richard OS — cognee bridge (real): index OS knowledge into shared memory,
query it back. Honest status — connected only when cognee + LLM key work."""
import os, shutil, subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _importable(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def _load_env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    # Real-key slot: an "LLM" connection saved in the Connections UI
    # overrides .env — the swap is one click from the UI.
    try:
        import sqlite3
        conn = sqlite3.connect(ROOT / "06-data" / "connections.db")
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT api_key, base_url FROM connections WHERE upper(provider) IN ('LLM','OPENAI') LIMIT 1").fetchone()
        conn.close()
        if row and row["api_key"]:
            os.environ["LLM_API_KEY"] = row["api_key"]
            if row["base_url"]:
                os.environ["OPENAI_API_BASE"] = row["base_url"]
                os.environ["LITELLM_BASE_URL"] = row["base_url"]
    except Exception:
        pass

def status():
    _load_env()
    if not _importable("cognee"):
        return {"provider": "cognee", "status": "not_configured",
                "detail": "pip install cognee to enable the shared-memory enhancer"}
    if not os.environ.get("LLM_API_KEY"):
        return {"provider": "cognee", "status": "partial",
                "detail": "cognee installed but LLM_API_KEY not set in .env (see README [10])"}
    return {"provider": "cognee", "status": "connected",
            "detail": "cognee + LLM key ready — shared memory active"}

def index_docs(folder="01-root-spine"):
    """Index the OS memory files into cognee (the shared-memory layer)."""
    _load_env()
    src = ROOT / folder
    if not src.exists():
        return {"error": f"{folder} not found"}
    try:
        from cognee.api.v1.add import add
        from cognee.api.v1.cognify import cognify
        import asyncio
        texts = []
        for f in sorted(src.glob("*.md")):
            texts.append(f"# {f.name}\n" + f.read_text()[:8000])
        asyncio.run(add("\n\n".join(texts)))
        asyncio.run(cognify())          # build the knowledge graph (embed + index)
        return {"ok": True, "docs": len(texts), "folder": folder}
    except Exception as e:
        return {"error": str(e)[:180]}

def query(q):
    """Query the shared memory (cognee) — returns passages if connected."""
    _load_env()
    try:
        from cognee.api.v1.search import search
        import asyncio
        results = asyncio.run(search(q))
        out = []
        for r in results or []:
            text = getattr(r, "text", None) or str(r)
            out.append(text[:400])
        return {"query": q, "results": out[:5], "count": len(out)}
    except Exception as e:
        return {"error": str(e)[:180]}

if __name__ == "__main__":
    import sys
    _load_env()
    print(json.dumps(status(), indent=2))
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        print(json.dumps(index_docs(), indent=2))
    if len(sys.argv) > 2 and sys.argv[1] == "query":
        print(json.dumps(query(" ".join(sys.argv[2:])), indent=2))
