#!/usr/bin/env python3
"""Richard OS — FastAPI server: systems of record as a live API."""
import sqlite3, json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DATA = Path(__file__).resolve().parent.parent / "06-data"
app = FastAPI(title="Richard OS API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def q(db_name, table, limit=50):
    conn = sqlite3.connect(DATA / db_name)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/")
def root():
    return {"name": "Richard OS", "status": "live", "systems": ["second_brain","pm","finance","crm","creator"]}

@app.get("/graph")
def graph():
    """Knowledge-graph nodes + edges, built from your real data."""
    nodes, edges = [], []
    # Core
    nodes.append({"id": "core", "label": "Richard OS", "type": "core", "x": 0, "y": 0})
    # Systems of record -> tool nodes
    systems = [
        ("second_brain", "second_brain.db", "captures", "tool"),
        ("pm", "pm.db", "tasks", "tool"),
        ("finance", "finance.db", "transactions", "tool"),
        ("crm", "crm.db", "contacts", "tool"),
        ("creator", "creator.db", "content", "tool"),
    ]
    for i, (name, dbfile, table, ntype) in enumerate(systems):
        nodes.append({"id": name, "label": name, "type": ntype, "x": 200, "y": (i - 2) * 140})
        edges.append({"source": "core", "target": name, "strength": 3})
        try:
            rows = q(dbfile, table)
            for j, r in enumerate(rows[:5]):
                nid = f"{name}-{r.get('id')}"
                nodes.append({"id": nid, "label": str(r.get("title") or r.get("name") or r.get("note") or r.get("kind"))[:40], "type": "data", "x": 420, "y": (j - 2) * 90})
                edges.append({"source": name, "target": nid, "strength": 1})
        except Exception:
            pass
    return {"nodes": nodes, "edges": edges}

@app.get("/systems/{name}")
def system(name: str):
    tables = {
        "second_brain": ("second_brain.db", ["captures","goals"]),
        "pm": ("pm.db", ["tasks","projects"]),
        "finance": ("finance.db", ["accounts","transactions"]),
        "crm": ("crm.db", ["contacts","deals"]),
        "creator": ("creator.db", ["content"]),
    }
    if name not in tables:
        return {"error": "unknown system"}
    dbfile, tabs = tables[name]
    return {t: q(dbfile, t) for t in tabs}

from fastapi.staticfiles import StaticFiles
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
