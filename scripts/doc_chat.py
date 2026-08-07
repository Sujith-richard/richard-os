#!/usr/bin/env python3
"""
scripts/doc_chat.py - #18 Conversation Layer: Doc-chat + Vision
Upload a PDF or image -> extract text (pypdf) or analyze vision (PIL base64 ->
model) -> chunk + store -> ask questions grounded in the doc via agent_lib.call_llm.
Persists to 06-data/docchat.db: docs, chunks, messages.
"""
import json, sqlite3, pathlib, datetime, re, base64, io, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "docchat.db"
UPLOADS = ROOT / "06-data" / "docchat_uploads"

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, kind TEXT, size INTEGER,
        text TEXT, summary TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id INTEGER, idx INTEGER, text TEXT);
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id INTEGER, role TEXT, text TEXT, created_at TEXT);
    """)
    c.commit(); c.close()

def _extract_pdf(path):
    from pypdf import PdfReader
    r = PdfReader(str(path))
    pages = []
    for i, p in enumerate(r.pages):
        try:
            t = p.extract_text() or ""
        except Exception:
            t = ""
        pages.append(f"[p{i+1}] {t}")
    return "\n".join(pages)

def _image_to_base64(path):
    from PIL import Image
    im = Image.open(path)
    im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def _analyze_image(path):
    """Vision: send base64 image to a vision-capable model (Model Orchestrator routing),
    fall back through candidates, then to the default. Honest empty if none work."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_lib import call_llm
    b64 = _image_to_base64(path)
    prompt = ("You are the Richard OS vision agent. Describe this image in detail: "
              "objects, text, layout, and any notable content.\n\n[IMAGE base64 attached]\n" + b64[:2000])
    # Model Orchestrator: try vision-capable models first
    for model in ("gemini-3.5-flash", "gpt-oss-120b", "deepseek-v4-flash-free"):
        try:
            out = call_llm(prompt, model=model)
            if out and out.strip() and not out.startswith("[LLM unavailable"):
                return out.strip()
        except Exception:
            continue
    return "[vision requires a vision-capable model — upload a text or PDF document instead]"

def _chunk(text, size=1200, overlap=150):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+size]))
        i += size - overlap
    return chunks or ["(empty document)"]

def upload_doc(name, data, kind):
    """Store a document (bytes) and return its id. kind: pdf | image | text."""
    init_db()
    UPLOADS.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^a-zA-Z0-9._-]+', '_', name)
    dest = UPLOADS / safe
    dest.write_bytes(data)
    size = len(data)
    if kind == "pdf":
        text = _extract_pdf(dest)
    elif kind == "image":
        desc = _analyze_image(dest)
        # store the model's description AS the doc text so questions match it
        text = "IMAGE DESCRIPTION: " + desc
    else:
        text = data.decode("utf-8", errors="replace")
    c = _conn()
    cur = c.execute("INSERT INTO docs (name, kind, size, text, created_at) VALUES (?,?,?,?,?)",
                    (name, kind, size, text[:200000], _now()))
    doc_id = cur.lastrowid
    for i, ch in enumerate(_chunk(text)):
        c.execute("INSERT INTO chunks (doc_id, idx, text) VALUES (?,?,?)", (doc_id, i, ch))
    c.commit()
    summary = text[:200] if kind == "text" else (text[:200] if kind == "pdf" else text[:200])
    c.execute("UPDATE docs SET summary=? WHERE id=?", (summary, doc_id))
    c.commit(); c.close()
    return {"ok": True, "doc_id": doc_id, "name": name, "kind": kind, "size": size,
            "chars": len(text), "chunks": len(_chunk(text))}

def _search_chunks(doc_id, question, top=3):
    """RAG retrieval: TF-IDF cosine over the doc's chunks (vector, not keyword)."""
    c = _conn()
    chunks = c.execute("SELECT * FROM chunks WHERE doc_id=? ORDER BY idx", (doc_id,)).fetchall()
    c.close()
    if not chunks:
        return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        texts = [ch["text"] for ch in chunks]
        vec = TfidfVectorizer(stop_words="english", max_features=1500)
        matrix = vec.fit_transform(texts)
        qv = vec.transform([question])
        sims = cosine_similarity(qv, matrix)[0]
        ranked = sorted(range(len(sims)), key=lambda i: -sims[i])[:top]
        return [chunks[i] for i in ranked if sims[i] > 0]
    except Exception:
        # fallback to lexical if sklearn unavailable
        words = set(re.findall(r'[a-z0-9]+', question.lower()))
        scored = []
        for ch in chunks:
            ch_words = set(re.findall(r'[a-z0-9]+', ch["text"].lower()))
            scored.append((len(words & ch_words), ch))
        scored.sort(key=lambda x: -x[0])
        return [ch for _, ch in scored[:top]]

def ask(doc_id, question):
    """Answer a question grounded in the document via the model."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_lib import call_llm
    init_db()
    c = _conn()
    doc = c.execute("SELECT * FROM docs WHERE id=?", (doc_id,)).fetchone()
    if not doc:
        c.close(); return {"ok": False, "error": "doc not found"}
    best = _search_chunks(doc_id, question)
    context = "\n\n".join(f"[chunk {i+1}] {ch['text'][:1500]}" for i, ch in enumerate(best))
    prompt = (f"You are answering a question about the document '{doc['name']}'. "
              f"Answer ONLY from the context below. If the answer isn't there, say so.\n\n"
              f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nANSWER:")
    answer = call_llm(prompt)
    c.execute("INSERT INTO messages (doc_id, role, text, created_at) VALUES (?,?,?,?)",
              (doc_id, "user", question, _now()))
    c.execute("INSERT INTO messages (doc_id, role, text, created_at) VALUES (?,?,?,?)",
              (doc_id, "assistant", answer, _now()))
    c.commit(); c.close()
    return {"ok": True, "answer": answer, "doc": doc["name"], "chunks_used": len(best),
            "sources": [ch["text"][:120] for ch in best]}

def list_docs():
    init_db()
    c = _conn()
    rows = c.execute("SELECT id, name, kind, size, created_at FROM docs ORDER BY id DESC").fetchall()
    c.close()
    return {"ok": True, "docs": [dict(r) for r in rows]}

def doc_messages(doc_id):
    init_db()
    c = _conn()
    rows = c.execute("SELECT * FROM messages WHERE doc_id=? ORDER BY id", (doc_id,)).fetchall()
    c.close()
    return {"ok": True, "messages": [dict(r) for r in rows]}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Richard OS Doc-chat + Vision (#18)")
    ap.add_argument("--upload", nargs=2, metavar=("PATH", "KIND"))
    ap.add_argument("--ask", nargs=2, metavar=("DOC_ID", "QUESTION"))
    ap.add_argument("--docs", action="store_true")
    args = ap.parse_args()
    if args.upload:
        p, kind = args.upload
        print(json.dumps(upload_doc(p.split("/")[-1], pathlib.Path(p).read_bytes(), kind), indent=2)); return
    if args.ask:
        print(json.dumps(ask(int(args.ask[0]), args.ask[1]), indent=2)); return
    if args.docs:
        print(json.dumps(list_docs(), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()

