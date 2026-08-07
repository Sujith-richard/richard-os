#!/usr/bin/env python3
"""
scripts/vector_db.py - Phase G1 Vector DB (lightweight, sklearn TF-IDF)
Semantic-ish retrieval: index documents (memory/repo-intel/skills) as TF-IDF
vectors, search by cosine similarity. No new heavy deps; pluggable to
sentence-transformers later. Persists to 06-data/vector_index.json.
"""
import json, sqlite3, pathlib, re, argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "06-data" / "vector_index.json"

def _docs_from_sources():
    """Collect documents from memory, repo intel, skills."""
    docs = []
    # memory.db
    try:
        c = sqlite3.connect(ROOT / "06-data" / "memory.db"); c.row_factory = sqlite3.Row
        for r in c.execute("SELECT id, mtype, content FROM memories"):
            docs.append({"id": f"mem-{r['id']}", "source": f"memory/{r['mtype']}", "text": r["content"]})
        c.close()
    except Exception:
        pass
    # repo intel
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from repo_intel import list_intel
        for r in list_intel():
            docs.append({"id": f"repo-{r['name']}", "source": "repo-intel",
                         "text": f"{r['name']} {r['repo_type']} {r['categories']} {r['dept_mapping']}"})
    except Exception:
        pass
    # skills
    for f in sorted((ROOT / "04-skills").glob("*.md")):
        docs.append({"id": f"skill-{f.stem}", "source": "skill", "text": f.read_text(errors="ignore")[:300]})
    return docs

def build_index():
    """Build/refresh the TF-IDF index from all sources."""
    docs = _docs_from_sources()
    if not docs:
        return {"ok": False, "error": "no documents to index"}
    texts = [d["text"] for d in docs]
    vec = TfidfVectorizer(stop_words="english", max_features=2000)
    matrix = vec.fit_transform(texts)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps({
        "docs": docs,
        "vocab": vec.get_feature_names_out().tolist(),
        "matrix": matrix.toarray().tolist(),
    }))
    return {"ok": True, "indexed": len(docs)}

def _load():
    d = json.loads(INDEX_PATH.read_text())
    return d

def search(query, top=5):
    """Search the index by cosine similarity."""
    d = _load()
    texts = [doc["text"] for doc in d["docs"]]
    vec = TfidfVectorizer(stop_words="english", max_features=2000, vocabulary=d["vocab"])
    mat = np.array(d["matrix"])
    qv = vec.fit_transform(texts).__class__  # placeholder no-op
    # build query vector
    from sklearn.feature_extraction.text import TfidfVectorizer as TV
    v2 = TV(stop_words="english", max_features=2000, vocabulary=d["vocab"])
    # refit on corpus then transform query — simplest: build full matrix each search
    full = v2.fit_transform(texts)
    qvec = v2.transform([query])
    sims = cosine_similarity(qvec, full)[0]
    ranked = sorted(range(len(sims)), key=lambda i: -sims[i])[:top]
    return [{"id": d["docs"][i]["id"], "source": d["docs"][i]["source"],
             "text": d["docs"][i]["text"][:200], "score": round(float(sims[i]), 3)}
            for i in ranked if sims[i] > 0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--search", metavar="QUERY")
    args = ap.parse_args()
    if args.build:
        print(json.dumps(build_index(), indent=2)); return
    if args.search:
        try:
            for r in search(args.search):
                print(f"  {r['score']:6.3f} [{r['source']}] {r['text'][:80]}")
        except FileNotFoundError:
            print("index not built — run --build first")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
