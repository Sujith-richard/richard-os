#!/usr/bin/env python3
"""scripts/training_pipeline.py - Phase E6 Training Pipeline 2.0
Pre-fine-tune stages: clean -> label -> vectorize -> eval split."""
import json, pathlib, re, argparse
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASETS = ROOT / "06-data" / "datasets"

def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()

def label(row):
    ins = row.get("instruction", "").lower()
    if any(k in ins for k in ["code", "api", "function", "build", "app"]): return "coding"
    if any(k in ins for k in ["image", "vision", "screenshot"]): return "vision"
    if any(k in ins for k in ["what", "explain", "tell", "define"]): return "knowledge"
    return "chat"

def vectorize(texts):
    from sklearn.feature_extraction.text import TfidfVectorizer
    v = TfidfVectorizer(stop_words="english", max_features=500)
    m = v.fit_transform(texts)
    return m.shape[0]

def run_pipeline(name="merged-training", output=None, eval_frac=0.2):
    src = DATASETS / f"{name}.jsonl"
    if not src.exists():
        return {"ok": False, "error": f"{name}.jsonl not found"}
    rows = [json.loads(l) for l in src.open() if l.strip()]
    cleaned, out_rows = [], []
    for r in rows:
        c = clean(r.get("output", ""))
        if len(c) < 10:
            continue
        cleaned.append(c)
        out_rows.append({"instruction": r.get("instruction", ""), "input": r.get("input", ""),
                         "output": c, "label": label(r), "source": r.get("source", name)})
    n_vec = vectorize(cleaned) if cleaned else 0
    n_eval = max(1, int(len(out_rows) * eval_frac))
    out_path = DATASETS / (output or f"{name}-clean.jsonl")
    eval_path = DATASETS / (output or f"{name}-eval.jsonl")
    with open(out_path, "w") as f, open(eval_path, "w") as fe:
        for i, r in enumerate(out_rows):
            (fe if i < n_eval else f).write(json.dumps(r) + "\n")
    return {"ok": True, "input": len(rows), "cleaned": len(out_rows),
            "dropped": len(rows) - len(out_rows), "vectorized": n_vec,
            "eval_size": n_eval, "train_file": str(out_path), "eval_file": str(eval_path)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", nargs="?", const="merged-training")
    args = ap.parse_args()
    if args.run:
        print(json.dumps(run_pipeline(args.run), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
