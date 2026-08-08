#!/usr/bin/env python3
"""
scripts/capability_gap.py - Phase F2 Capability-gap detection
Analyzes a request + (optional) the local model's incomplete output to
classify WHY it couldn't complete: coding / vision / reasoning / knowledge / speed.
Maps each gap to the specialized cloud model (per architecture).
"""
import re, json, argparse

# request keyword signals -> capability
SIGNALS = {
    "coding": ["build", "code", "app", "api", "function", "component", "bug", "refactor",
               "implement", "script", "backend", "frontend", "database", "website", "project"],
    "vision": ["image", "screenshot", "photo", "ui design", "picture", "visual", "logo", "icon",
               "look at this", "from this image", "extract the layout"],
    "reasoning": ["why", "explain", "analyze", "evaluate", "compare", "strategy", "decision",
                  "architecture", "plan", "logic", "solve", "prove"],
    "knowledge": ["what is", "tell me about", "who", "when", "history", "research", "facts",
                  "documentation", "explain concept", "define"],
    "speed": ["fast", "quick", "urgent", "asap", "now", "immediately", "batch", "many", "bulk"],
}

# failure-signal in incomplete output -> capability
OUTPUT_SIGNALS = {
    "coding": ["error", "exception", "traceback", "syntax", "import", "cannot", "incomplete", "missing"],
    "vision": ["vision", "image", "can't see", "cannot view", "base64", "visual"],
    "reasoning": ["unsure", "not confident", "cannot determine", "ambiguous", "unclear"],
    "knowledge": ["don't know", "not in context", "no information", "cannot answer"],
}

def detect(request, local_output=""):
    """Classify the capability gap(s). Returns ranked list with the specialized model."""
    r = request.lower()
    scores = {cap: 0 for cap in SIGNALS}
    for cap, kws in SIGNALS.items():
        for kw in kws:
            if kw in r:
                scores[cap] += 2
    # output signals weigh heavier (evidence of actual failure)
    o = (local_output or "").lower()
    for cap, kws in OUTPUT_SIGNALS.items():
        for kw in kws:
            if kw in o:
                scores[cap] += 3
    ranked = sorted([(c, s) for c, s in scores.items() if s > 0], key=lambda x: -x[1])
    if not ranked:
        return {"ok": True, "gaps": [], "primary": "none", "specialist": None,
                "message": "no capability gap detected — local model can proceed"}
    primary = ranked[0][0]
    specialist = {
        "coding": "deepseek", "vision": "gemini", "reasoning": "claude",
        "knowledge": "gpt", "speed": "groq",
    }[primary]
    # v5.8 Pool #3: ask OmniRoute for a candidate model for this gap first
    omni = None
    try:
        import sys as _cg, pathlib as _cp
        _cg.path.insert(0, str(_cp.Path(__file__).resolve().parent))
        from model_orchestrator import resolve_for_capability
        _r = resolve_for_capability(primary, "default")
        if _r.get("pool") == "omni-route" or str(_r.get("resolved", "")).startswith("omni://"):
            omni = _r["resolved"]
    except Exception:
        omni = None
    return {"ok": True, "gaps": ranked, "primary": primary, "specialist": specialist,
            "omni_candidate": omni,
            "message": f"gap: {primary} -> escalate to {omni or specialist}"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="Build a fitness app")
    ap.add_argument("--output", default="", help="local model's incomplete output (optional)")
    args = ap.parse_args()
    print(json.dumps(detect(args.request, args.output), indent=2))

if __name__ == "__main__":
    main()
