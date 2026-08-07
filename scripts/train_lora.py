#!/usr/bin/env python3
"""
scripts/train_lora.py - #16 real fine-tune hook
Actually trains a tiny causal LM (sshleifer/tiny-gpt2) on the Richard OS
dataset (instruction/input/output JSONL) for a few steps on CPU.
Writes a real checkpoint to 06-data/models/ + a training log.
Honest: tiny model + small steps = real but modest (fits CPU / no GPU).
"""
import json, pathlib, sys, time, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "06-data" / "datasets"
MODEL_DIR = ROOT / "06-data" / "models"
LOG_DIR = ROOT / "06-data" / "train_logs"

def load_dataset(name="richard-core-v1"):
    p = DATASET_DIR / f"{name}.jsonl"
    if not p.exists():
        raise FileNotFoundError(f"dataset {name} not found")
    rows = []
    for line in p.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="richard-core-v1")
    ap.add_argument("--steps", type=int, default=12)
    ap.add_argument("--model", default="sshleifer/tiny-gpt2")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = load_dataset(args.dataset)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"train-{args.dataset}-{int(time.time())}.log"
    log = open(log_path, "w")
    def logp(msg):
        print(msg, flush=True)
        log.write(msg + "\n"); log.flush()

    logp(f"[train] dataset={args.dataset} samples={len(rows)} model={args.model} steps={args.steps} dry_run={args.dry_run}")
    import torch
    dev = "CUDA " + torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    logp(f"[train] device: {dev}")

    if args.dry_run:
        logp("[train] DRY RUN — no training executed (would train here)")
        log.close()
        print(json.dumps({"ok": True, "dry_run": True, "log": str(log_path), "samples": len(rows)}))
        return

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
    from transformers import DataCollatorForLanguageModeling
    from datasets import Dataset
    use_cuda = torch.cuda.is_available()

    logp(f"[train] loading tokenizer + model {args.model} ...")
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model)

    def fmt(r):
        return f"Instruction: {r.get('instruction','')}\n{r.get('input','')}\nAnswer: {r.get('output','')}"

    texts = [fmt(r) for r in rows]
    enc = tok(texts, truncation=True, padding="max_length", max_length=96, return_tensors="np")
    ds = Dataset.from_dict({"input_ids": enc["input_ids"].tolist(), "attention_mask": enc["attention_mask"].tolist()})

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = MODEL_DIR / f"richard-{args.dataset}-tiny"
    # E5: LoRA — freeze base, add low-rank adapters (fits bigger models on the RTX)
    try:
        from peft import LoraConfig, get_peft_model, TaskType
        lora = LoraConfig(task_type=TaskType.CAUSAL_LM, r=4, lora_alpha=8,
                          target_modules=["c_attn"], lora_dropout=0.05)
        model = get_peft_model(model, lora)
        logp("[train] LoRA enabled (r=4) — training adapters only")
    except Exception as e:
        logp(f"[train] LoRA unavailable, full fine-tune: {str(e)[:60]}")
    targs = TrainingArguments(
        output_dir=str(out_dir), max_steps=args.steps, per_device_train_batch_size=1,
        learning_rate=5e-5, logging_steps=args.steps, save_steps=args.steps,
        report_to=[],
    )
    trainer = Trainer(
        model=model, args=targs,
        train_dataset=ds,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tok, mlm=False),
    )
    logp(f"[train] starting {args.steps} steps ...")
    t0 = time.time()
    trainer.train()
    dt = round(time.time() - t0, 1)
    trainer.save_model(str(out_dir))
    logp(f"[train] done in {dt}s — checkpoint at {out_dir}")
    log.close()
    print(json.dumps({"ok": True, "dry_run": False, "checkpoint": str(out_dir),
                      "steps": args.steps, "samples": len(rows), "seconds": dt, "log": str(log_path)}))

if __name__ == "__main__":
    main()
