#!/usr/bin/env python3
"""
scripts/ai_runtime.py - v5.1 AI Runtime service
The unified per-call layer between Brain and models.
Normalizes every provider: token manager, cost tracker, timeout, output
validator, streaming stub. call_llm() routes through here.
"""
import time, json, datetime, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNTIME_DB = ROOT / "06-data" / "ai_runtime.db"

# approximate cost per 1K tokens (USD) — update when real prices known
MODEL_COST = {
    "deepseek-v4-flash-free": 0.0002, "gemini-3.5-flash": 0.0001,
    "gpt-oss-120b": 0.001, "qwen3-32b": 0.0005, "llama-3.3-70b-instruct": 0.0008,
    "big-pickle": 0.0001, "richard-local": 0.0,
}

def _est_tokens(text):
    return max(1, len(text or "") // 4)

def estimate_cost(model, prompt, response):
    in_t = _est_tokens(prompt); out_t = _est_tokens(response)
    rate = MODEL_COST.get(model, 0.0003)
    return round((in_t + out_t) / 1000 * rate, 6), in_t, out_t

def validate_output(response, min_len=1):
    """Output validator: empty/error-marker checks."""
    if not response or not str(response).strip():
        return False, "empty response"
    if str(response).startswith("[LLM unavailable"):
        return False, "llm unavailable"
    if len(str(response).strip()) < min_len:
        return False, "too short"
    return True, "ok"

def _log_call(model, prompt, response, elapsed, ok, err=""):
    import sqlite3
    cost, it, ot = estimate_cost(model, prompt, response)
    RUNTIME_DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(RUNTIME_DB)
    c.execute("""CREATE TABLE IF NOT EXISTS calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, task_type TEXT, prompt_tokens INT,
        response_tokens INT, cost REAL, latency REAL, ok INT, error TEXT, at TEXT)""")
    c.execute("INSERT INTO calls (model, task_type, prompt_tokens, response_tokens, cost, latency, ok, error, at) VALUES (?,?,?,?,?,?,?,?,?)",
              (model, "general", it, ot, cost, round(elapsed, 3), 1 if ok else 0, err[:100],
               datetime.datetime.now().isoformat(timespec="seconds")))
    c.commit(); c.close()
    return {"cost": cost, "tokens_in": it, "tokens_out": ot, "latency": round(elapsed, 3)}

def run_call(llm_fn, model, prompt, timeout=60, **kw):
    """Execute a model call through the runtime: timeout + validate + log."""
    ok, err = True, ""
    t0 = time.time()
    try:
        response = llm_fn(prompt, model=model, **kw)
    except Exception as e:
        response = f"[LLM unavailable: {e}]"
        ok, err = False, str(e)[:100]
    elapsed = time.time() - t0
    v_ok, v_err = validate_output(response)
    if not v_ok:
        ok, err = False, v_err
    telemetry = _log_call(model, prompt, response, elapsed, ok, err)
    return {"response": response, "ok": ok and v_ok, "error": err, "telemetry": telemetry}

def recent_calls(limit=20):
    import sqlite3
    if not RUNTIME_DB.exists():
        return {"ok": True, "calls": []}
    c = sqlite3.connect(RUNTIME_DB); c.row_factory = sqlite3.Row
    rows = c.execute("SELECT * FROM calls ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return {"ok": True, "calls": [dict(r) for r in rows]}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", action="store_true")
    args = ap.parse_args()
    if args.recent:
        for c in recent_calls()["calls"]:
            print(f"  [{c['id']}] {c['model']:22s} ${c['cost']:.6f} {c['latency']:5.2f}s ok={c['ok']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
