#!/usr/bin/env python3
"""
scripts/knowledge_graph.py - Phase G2 Real Knowledge Graph
Extracts subject-relation-object triples from text (memory/repo-intel/skills),
persists nodes+edges, supports neighbor/relation queries.
Lightweight heuristic extraction; pluggable to LLM-based extraction later.
"""
import json, sqlite3, pathlib, re, datetime, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "06-data" / "knowledge_graph.db"

RELATIONS = [
    (r"\b(\w[\w -]*?)\s+is a\s+(\w[\w -]*?)\b", "is-a"),
    (r"\b(\w[\w -]*?)\s+is an\s+(\w[\w -]*?)\b", "is-a"),
    (r"\b(\w[\w -]*?)\s+uses\s+(\w[\w -]*?)\b", "uses"),
    (r"\b(\w[\w -]*?)\s+builds?\s+(\w[\w -]*?)\b", "builds"),
    (r"\b(\w[\w -]*?)\s+runs on\s+(\w[\w -]*?)\b", "runs-on"),
    (r"\b(\w[\w -]*?)\s+contains\s+(\w[\w -]*?)\b", "contains"),
    (r"\b(\w[\w -]*?)\s+depends on\s+(\w[\w -]*?)\b", "depends-on"),
    (r"\b(\w[\w -]*?)\s+belongs to\s+(\w[\w -]*?)\b", "belongs-to"),
]

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
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY, label TEXT, kind TEXT, source TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT, src TEXT, rel TEXT, dst TEXT, source TEXT,
        created_at TEXT, UNIQUE(src, rel, dst));
    """)
    c.commit(); c.close()

def add_triple(subj, rel, obj, source="manual", subj_kind="entity", obj_kind="entity"):
    init_db()
    c = _conn()
    c.execute("INSERT OR IGNORE INTO nodes (id, label, kind, source, created_at) VALUES (?,?,?,?,?)",
              (subj.lower(), subj, subj_kind, source, _now()))
    c.execute("INSERT OR IGNORE INTO nodes (id, label, kind, source, created_at) VALUES (?,?,?,?,?)",
              (obj.lower(), obj, obj_kind, source, _now()))
    c.execute("INSERT OR IGNORE INTO edges (src, rel, dst, source, created_at) VALUES (?,?,?,?,?)",
              (subj.lower(), rel, obj.lower(), source, _now()))
    c.commit(); c.close()
    return {"ok": True, "triple": f"{subj} -{rel}-> {obj}"}

def extract_from_text(text, source):
    """Extract triples from free text using the relation patterns."""
    added = []
    for pat, rel in RELATIONS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            s, o = m.group(1).strip(), m.group(2).strip()
            if len(s) > 2 and len(o) > 2 and s.lower() != o.lower():
                add_triple(s, rel, o, source)
                added.append(f"{s} -{rel}-> {o}")
    return added

def extract_from_sources():
    """Extract triples from memory, repo intel, skills (idempotent-ish)."""
    added = []
    # memory
    try:
        c = sqlite3.connect(ROOT / "06-data" / "memory.db"); c.row_factory = sqlite3.Row
        for r in c.execute("SELECT content FROM memories"):
            added += extract_from_text(r["content"], "memory")
        c.close()
    except Exception:
        pass
    # repo intel
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from repo_intel import list_intel
        for r in list_intel():
            add_triple(r["name"], "is-a", r["repo_type"], "repo-intel", "repository", "type")
            add_triple(r["name"], "maps-to", r["dept_mapping"], "repo-intel", "repository", "department")
            added.append(f"{r['name']} -is-a-> {r['repo_type']}")
            added.append(f"{r['name']} -maps-to-> {r['dept_mapping']}")
    except Exception:
        pass
    return added

def graph():
    init_db()
    c = _conn()
    nodes = c.execute("SELECT * FROM nodes ORDER BY label LIMIT 500").fetchall()
    edges = c.execute("SELECT * FROM edges LIMIT 1000").fetchall()
    c.close()
    return {"ok": True, "nodes": [dict(n) for n in nodes], "edges": [dict(e) for e in edges]}

def neighbors(node, depth=1):
    init_db()
    c = _conn()
    node = node.lower()
    out = c.execute("""SELECT e.rel, e.dst, n2.label FROM edges e
                       JOIN nodes n2 ON n2.id = e.dst
                       WHERE e.src=?""", (node,)).fetchall()
    inc = c.execute("""SELECT e.rel, e.src, n2.label FROM edges e
                       JOIN nodes n2 ON n2.id = e.src
                       WHERE e.dst=?""", (node,)).fetchall()
    c.close()
    return {"ok": True, "node": node,
            "outgoing": [{"rel": r["rel"], "target": r["dst"], "label": r["label"]} for r in out],
            "incoming": [{"rel": r["rel"], "source": r["src"], "label": r["label"]} for r in inc]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--add", nargs=3, metavar=("SUBJ", "REL", "OBJ"))
    ap.add_argument("--graph", action="store_true")
    ap.add_argument("--neighbors", metavar="NODE")
    args = ap.parse_args()
    if args.extract:
        added = extract_from_sources()
        print(json.dumps({"ok": True, "added": len(added), "sample": added[:6]}, indent=2)); return
    if args.add:
        print(json.dumps(add_triple(*args.add), indent=2)); return
    if args.graph:
        g = graph()
        print(f"nodes: {len(g['nodes'])} | edges: {len(g['edges'])}"); return
    if args.neighbors:
        d = neighbors(args.neighbors)
        print(f"neighbors of {args.neighbors}:")
        for r in d["outgoing"]: print(f"  -{r['rel']}-> {r['label']}")
        for r in d["incoming"]: print(f"  <-{r['rel']}- {r['label']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
