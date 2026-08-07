#!/usr/bin/env python3
"""
scripts/escalation_engine.py - Phase F3 Intelligent Escalation Engine
Local First, Cloud Assisted:
1. Try local model (priority 1) with full context
2. If incomplete -> detect capability gap (F2)
3. Escalate to specialized cloud model (deepseek/gemini/groq/claude/gpt/qwen/mistral)
4. Return the assisted result to the Brain
"""
import json, sys, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent

def _local_llm(prompt, task_type="default", context=False, dept="web", sub=None):
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_lib import call_llm
    return call_llm(prompt, task_type=task_type, context=context, dept=dept, sub=sub)

def _cloud_llm(prompt, model, context=False, dept="web", sub=None):
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_lib import call_llm
    return call_llm(prompt, model=model, context=context, dept=dept, sub=sub)

# map capability -> specialist provider (per architecture: coding=DeepSeek, vision=Gemini,
# reasoning=Claude, knowledge=GPT, speed=Groq); resolved to a real model via the chain
SPECIALIST_PROVIDERS = {
    "coding": "deepseek", "vision": "gemini", "reasoning": "claude",
    "knowledge": "gpt", "speed": "groq",
}
def _resolve_model(specialist):
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from model_orchestrator import PROVIDER_CHAIN
        for p, m, c in PROVIDER_CHAIN:
            if p == specialist:
                return m
    except Exception:
        pass
    return "deepseek-v4-flash-free"

def execute(request, dept="web", sub=None, context=True, task_type="default"):
    """The full escalation pipeline. Returns local or assisted result + trace."""
    trace = []
    # Step 1: local model first (with full context envelope)
    local = _local_llm(request, task_type=task_type, context=context, dept=dept, sub=sub)
    trace.append({"step": "local", "model": "local-or-routed", "len": len(local)})
    if local.startswith("[LLM unavailable"):
        trace.append({"step": "local-error", "detail": local[:80]})
    # Step 2: detect capability gap from the local output
    sys.path.insert(0, str(ROOT / "scripts"))
    from capability_gap import detect
    gap = detect(request, local)
    trace.append({"step": "gap-detect", "primary": gap["primary"], "specialist": gap["specialist"]})
    if gap["primary"] == "none":
        return {"ok": True, "request": request, "result": local, "assisted": False, "trace": trace}
    # Step 3: escalate to the specialist cloud model
    specialist = gap["specialist"]
    model = _resolve_model(specialist)
    prompt = (f"Richard OS escalated this task because the local model hit a "
              f"'{gap['primary']}' capability gap.\n\n"
              f"Local model's attempt:\n{local[:600]}\n\n"
              f"Complete the task with your stronger {gap['primary']} capability:\n{request}")
    assisted = _cloud_llm(prompt, model=model, context=context, dept=dept, sub=sub)
    trace.append({"step": "escalate", "specialist": specialist, "model": model, "len": len(assisted)})
    # F5: learn from the cloud-assisted result (append to dataset if quality passes)
    try:
        from learn_from_cloud import learn
        lr = learn(request, assisted, gap=gap["primary"], specialist=specialist)
        trace.append({"step": "learn", "quality": lr.get("quality"), "appended": lr.get("dataset_appended")})
    except Exception as e:
        trace.append({"step": "learn", "error": str(e)[:60]})
    return {"ok": True, "request": request, "result": assisted, "assisted": True,
            "gap": gap["primary"], "specialist": specialist, "model": model, "trace": trace}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="Build a fitness app landing page")
    ap.add_argument("--dept", default="web")
    ap.add_argument("--sub", default=None)
    args = ap.parse_args()
    r = execute(args.request, args.dept, args.sub)
    print(json.dumps({"ok": r["ok"], "assisted": r["assisted"],
                      "gap": r.get("gap"), "specialist": r.get("specialist"),
                      "trace": r["trace"], "result_len": len(r["result"]),
                      "result_preview": r["result"][:200]}, indent=2))

if __name__ == "__main__":
    main()
