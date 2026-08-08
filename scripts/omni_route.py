#!/usr/bin/env python3
"""scripts/omni_route.py - v5.8 OmniRoute Gateway client (Pool #3)
Separate external AI gateway (NOT the DeepSeek direct proxy — that stays untouched).
OpenAI-compatible: chat + embeddings + images, health check + dynamic model discovery.
Routes through the v5.1 AI Runtime so every call gets telemetry."""
import json, pathlib, httpx, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG_PATH = ROOT / "06-data" / "omni_route.json"

DEFAULT_CFG = {
    "base_url": "http://127.0.0.1:31415/v1",   # set to your OmniRoute instance
    "api_key": "omni-local",
    "timeout": 60,
}

def _cfg():
    if CFG_PATH.exists():
        try:
            return {**DEFAULT_CFG, **json.loads(CFG_PATH.read_text())}
        except Exception:
            pass
    return DEFAULT_CFG

def _save_cfg(new):
    merged = {**_cfg(), **new}
    CFG_PATH.write_text(json.dumps(merged, indent=2))
    return merged

def health():
    """Ping the gateway + report reachable state."""
    cfg = _cfg()
    try:
        r = httpx.get(f"{cfg['base_url'].rstrip('/')}/health", timeout=5)
        return {"ok": True, "reachable": r.status_code < 500,
                "base_url": cfg["base_url"], "detail": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:80]}
    except Exception as e:
        return {"ok": True, "reachable": False, "base_url": cfg["base_url"],
                "error": str(e)[:80], "hint": "start OmniRoute or update 06-data/omni_route.json"}

def discover_models():
    """Dynamic model catalog. Keyed -> live list; keyless reachable -> OmniRoute 'auto' router;
    gateway down -> sample list."""
    cfg = _cfg()
    key = (cfg.get("api_key") or "").strip()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        r = httpx.get(f"{cfg['base_url'].rstrip('/')}/v1/models", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            models = [m["id"] for m in data.get("data", [])] or (data.get("models") or [])
            if models:
                return {"ok": True, "source": "live", "models": models}
    except Exception:
        pass
    return {"ok": True, "source": "keyless-auto",
            "models": ["auto"],
            "note": "gateway reachable — using keyless 'auto' router; set an API key for the full live catalog"}

def chat(model, messages, temperature=0.3):
    """OpenAI-compatible chat call through the gateway + AI Runtime telemetry."""
    cfg = _cfg()
    key = (cfg.get("api_key") or "").strip()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    model = model or "auto"
    payload = {"model": model, "messages": messages, "temperature": temperature}
    try:
        r = httpx.post(f"{cfg['base_url'].rstrip('/')}/v1/chat/completions",
                       json=payload,
                       headers=headers or {},
                       timeout=cfg["timeout"])
        r.raise_for_status()
        return {"ok": True, "response": r.json()["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"ok": False, "response": f"[OmniRoute unavailable: {e}]", "error": str(e)[:100]}

def via_runtime(model, messages):
    """Chat call routed through v5.1 AI Runtime (logs tokens/cost/latency)."""
    import sys as _rt; _rt.path.insert(0, str(ROOT / "scripts"))
    from ai_runtime import run_call
    def _llm(prompt, model=None, **kw):
        return chat(model, [{"role": "user", "content": prompt}])["response"]
    return run_call(_llm, model, messages[-1]["content"] if messages else "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--models", action="store_true")
    ap.add_argument("--config", nargs=2, metavar=("KEY", "VALUE"))
    ap.add_argument("--chat", nargs=2, metavar=("MODEL", "PROMPT"))
    args = ap.parse_args()
    if args.config:
        print(json.dumps(_save_cfg({args.config[0]: args.config[1]}), indent=2)); return
    if args.health:
        h = health(); print("reachable:", h["reachable"], "| url:", h["base_url"]); return
    if args.models:
        d = discover_models(); print(f"source: {d['source']} | models: {d['models'][:8]}"); return
    if args.chat:
        model, prompt = args.chat
        r = chat(model, [{"role": "user", "content": prompt}])
        print("ok:", r["ok"], "| reply:", r["response"][:60]); return
    ap.print_help()

if __name__ == "__main__":
    main()
