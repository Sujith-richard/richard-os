#!/usr/bin/env python3
"""
scripts/model_orchestrator.py - #11/#10 Model Orchestrator
Routes each task to the best model: task-type -> tier -> model, with fallback.
Per-task tiers (cloud/local) + per-agent override + honest live status.
"""
import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "06-data" / "model_routes.json"

# Task types -> preferred model (tier: fast/balanced/power) — the routing table
ROUTES = {
    "chat":        {"model": "deepseek-v4-flash-free", "tier": "fast",     "why": "low latency chat"},
    "plan":        {"model": "qwen3-32b",              "tier": "balanced", "why": "structured planning"},
    "code":        {"model": "deepseek-v4-flash-free", "tier": "fast",     "why": "coding model"},
    "analysis":    {"model": "gpt-oss-120b",           "tier": "power",    "why": "deep reasoning"},
    "creative":    {"model": "gemini-3.5-flash",       "tier": "balanced", "why": "creative writing"},
    "reasoning":   {"model": "gpt-oss-120b",           "tier": "power",    "why": "hard reasoning"},
    "vision":      {"model": "gemini-3.5-flash",       "tier": "balanced", "why": "vision-capable first"},
    "research":    {"model": "llama-3.3-70b-instruct", "tier": "balanced", "why": "research summaries"},
    "summarize":   {"model": "llama-3.3-70b-instruct", "tier": "balanced", "why": "long-doc summarize"},
    "quick":       {"model": "big-pickle",             "tier": "fast",     "why": "tiny tasks"},
    "default":     {"model": "deepseek-v4-flash-free", "tier": "fast",     "why": "general fallback"},
}
# Fallback chain per tier (if preferred is down)
FALLBACK = {
    "fast":     ["deepseek-v4-flash-free", "big-pickle", "qwen3-32b"],
    "balanced": ["qwen3-32b", "llama-3.3-70b-instruct", "gemini-3.5-flash", "deepseek-v4-flash-free"],
    "power":    ["gpt-oss-120b", "gemini-3.5-flash", "qwen3-32b"],
}

def load_routes():
    if CONFIG.exists():
        try:
            d = json.loads(CONFIG.read_text())
            return d.get("routes", ROUTES)
        except Exception:
            pass
    return ROUTES

def save_routes(routes):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({"routes": routes}, indent=2))

def available_models():
    """Live list from the models integration (or proxy directly)."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:1234/v1/models", timeout=5) as r:
            d = json.loads(r.read().decode())
            return [m["id"] for m in d.get("data", [])]
    except Exception:
        return ["deepseek-v4-flash-free"]

def route_model(task_type="default", agent=None, routes=None):
    """Return the model + tier + fallback chain for a task type (agent override wins)."""
    routes = routes or load_routes()
    key = task_type if task_type in routes else "default"
    entry = routes[key]
    model = entry["model"]
    if agent:
        # per-agent override in routes.agents
        agent_model = routes.get("agents", {}).get(agent)
        if agent_model:
            model = agent_model
            entry = {"model": agent_model, "tier": entry["tier"], "why": f"agent override ({agent})"}
    chain = FALLBACK.get(entry["tier"], FALLBACK["fast"])
    if model not in chain:
        chain = [model] + [m for m in chain if m != model]
    return {"task_type": key, "model": model, "tier": entry.get("tier", "fast"),
            "why": entry.get("why", ""), "fallback_chain": chain}

def resolve_model(task_type="default", agent=None):
    """Pick the model to actually call (preferred, or first available in chain)."""
    routes = load_routes()
    r = route_model(task_type, agent, routes)
    avail = set(available_models())
    for m in r["fallback_chain"]:
        if m in avail:
            r["resolved"] = m
            return r
    r["resolved"] = r["model"]  # last resort: preferred even if not in live list
    return r

def set_route(task_type, model, tier=None, why=""):
    routes = load_routes()
    routes[task_type] = {"model": model, "tier": tier or routes.get(task_type, {}).get("tier", "fast"), "why": why or f"manual route to {model}"}
    save_routes(routes)
    return {"ok": True, "task_type": task_type, **routes[task_type]}

# Phase F6: provider priority chain (architecture: local first, cloud assisted)
PROVIDER_CHAIN = [
    ("local",    "richard-local",            "local RTX inference"),
    ("deepseek", "deepseek-v4-flash-free",   "general coding"),
    ("gemini",   "gemini-3.5-flash",         "vision"),
    ("groq",     "big-pickle",               "fast execution"),
    ("claude",   "gpt-oss-120b",             "complex reasoning"),
    ("gpt",      "gemini-3.5-flash",         "broad knowledge"),
    ("qwen",     "qwen3-32b",                "specialized language"),
    ("mistral",  "llama-3.3-70b-instruct",   "efficiency"),
]
def provider_status():
    avail = set(available_models())
    return {"ok": True, "chain": [
        {"priority": i + 1, "provider": p, "model": m, "capability": c,
         "available": m in avail} for i, (p, m, c) in enumerate(PROVIDER_CHAIN)]}

def status():
    routes = load_routes()
    avail = set(available_models())
    rows = []
    for k, v in routes.items():
        r = resolve_model(k)
        rows.append({"task_type": k, "model": v.get("model"), "tier": v.get("tier"),
                     "why": v.get("why", ""), "available": v.get("model") in avail,
                     "resolved": r["resolved"]})
    return {"ok": True, "models_available": sorted(avail), "routes": rows}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Richard OS Model Orchestrator (#11)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--route", metavar="TASK_TYPE", nargs="?", const="default")
    ap.add_argument("--resolve", nargs=2, metavar=("TASK_TYPE", "AGENT"))
    ap.add_argument("--set", nargs=3, metavar=("TASK_TYPE", "MODEL", "TIER"))
    args = ap.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2)); return
    if args.resolve:
        print(json.dumps(resolve_model(args.resolve[0], args.resolve[1]), indent=2)); return
    if args.route:
        print(json.dumps(route_model(args.route), indent=2)); return
    if args.set:
        print(json.dumps(set_route(args.set[0], args.set[1], args.set[2]), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
