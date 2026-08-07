#!/usr/bin/env python3
"""
scripts/local_inference.py - #11 local inference endpoint
Serves completions from a model loaded locally on the RTX (CUDA).
Uses the fine-tuned checkpoint (06-data/models/richard-<dataset>-tiny)
or falls back to a small pretrained model. Model loads once (module cache).
"""
import pathlib, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "06-data" / "models"
DEFAULT_CKPT = MODEL_DIR / "richard-richard-core-v1-tiny"
FALLBACK_MODEL = "sshleifer/tiny-gpt2"

_model = None
_tok = None
_device = None

def _load():
    global _model, _tok, _device
    if _model is not None:
        return _model, _tok, _device
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    # E4: use the registry-deployed active model if set
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from model_registry import active_model
        deployed = active_model()
    except Exception:
        deployed = None
    ckpt = deployed or (str(DEFAULT_CKPT) if DEFAULT_CKPT.exists() else FALLBACK_MODEL)
    _tok = AutoTokenizer.from_pretrained(str(ckpt) if DEFAULT_CKPT.exists() else ckpt)
    if _tok.pad_token is None:
        _tok.pad_token = _tok.eos_token
    _model = AutoModelForCausalLM.from_pretrained(str(ckpt) if DEFAULT_CKPT.exists() else ckpt)
    _model.to(_device)
    _model.eval()
    return _model, _tok, _device

def status():
    try:
        model, tok, device = _load()
        return {"ok": True, "status": "loaded", "device": device,
                "model": str(DEFAULT_CKPT) if DEFAULT_CKPT.exists() else FALLBACK_MODEL,
                "loaded": True}
    except Exception as e:
        return {"ok": False, "status": "error", "device": "cpu", "error": str(e)[:200], "loaded": False}

def generate(prompt, max_new=60, temperature=0.8):
    model, tok, device = _load()
    import torch
    inputs = tok(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new,
                             temperature=temperature, do_sample=True, pad_token_id=tok.pad_token_id)
    text = tok.decode(out[0], skip_special_tokens=True)
    return {"ok": True, "prompt": prompt, "completion": text, "device": device}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--prompt", metavar="TEXT")
    ap.add_argument("--max-new", type=int, default=60)
    args = ap.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2)); return
    if args.prompt:
        print(json.dumps(generate(args.prompt, args.max_new), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
