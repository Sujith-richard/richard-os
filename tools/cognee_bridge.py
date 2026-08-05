#!/usr/bin/env python3
"""Richard OS — cognee bridge (AI memory + knowledge-graph builder).
Honest status: connected / not_configured / error. Never fakes."""
import shutil, subprocess
from pathlib import Path

def status():
    """Is cognee installed/available?"""
    if shutil.which("cognee") or _importable("cognee"):
        return {"provider": "cognee", "status": "connected", "detail": "cognee available — memory layer ready"}
    return {"provider": "cognee", "status": "not_configured", "detail": "pip install cognee to enable the shared-memory enhancer"}

def _importable(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def add_to_memory(text, namespace="richard"):
    """Push a note into cognee memory (only if available)."""
    if status()["status"] != "connected":
        return {"error": "cognee not installed — memory write skipped (honest)"}
    try:
        from cognee.api.v1.add import add
        import asyncio
        asyncio.run(add(text))
        return {"ok": True, "note": "added to cognee shared memory"}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
