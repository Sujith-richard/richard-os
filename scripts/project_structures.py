#!/usr/bin/env python3
"""scripts/project_structures.py - Phase B6 Project Structure Repository
Catalog of project blueprints (folder trees + starter files). Project Gen selects by keyword."""
import json, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLUEPRINTS = {
    "react":    {"stack": "frontend", "tree": ["package.json", "vite.config.js", "index.html", "src/main.jsx", "src/App.jsx", "src/index.css", ".env.example", "README.md"]},
    "nextjs":   {"stack": "frontend", "tree": ["package.json", "next.config.js", "pages/index.js", "pages/_app.js", "components/", "styles/globals.css", ".env.local.example", "README.md"]},
    "vue":      {"stack": "frontend", "tree": ["package.json", "vite.config.js", "index.html", "src/main.js", "src/App.vue", "src/components/", ".env.example", "README.md"]},
    "fastapi":  {"stack": "backend",  "tree": ["requirements.txt", "app/main.py", "app/models.py", "app/schemas.py", "app/routers/health.py", ".env.example", "Dockerfile", "README.md"]},
    "django":   {"stack": "backend",  "tree": ["requirements.txt", "manage.py", "project/settings.py", "project/urls.py", "app/models.py", "app/views.py", "app/admin.py", ".env.example", "README.md"]},
    "express":  {"stack": "backend",  "tree": ["package.json", "src/server.js", "src/routes/index.js", "src/controllers/", "src/models/", ".env.example", "README.md"]},
    "postgres": {"stack": "database", "tree": ["schema.sql", "migrations/001_init.sql", "seed.sql", "README.md"]},
    "mongodb":  {"stack": "database", "tree": ["schema.js", "models/", "seed.js", "README.md"]},
    "rest":     {"stack": "api",      "tree": ["openapi.yaml", "routes/", "README.md"]},
    "graphql":  {"stack": "api",      "tree": ["schema.graphql", "resolvers/", "README.md"]},
    "docker":   {"stack": "devops",   "tree": ["Dockerfile", "docker-compose.yml", ".dockerignore", "README.md"]},
    "jwt":      {"stack": "auth",     "tree": ["auth.js", "middleware/", "README.md"]},
}
# alias: structure name -> blueprint
ALIASES = {"next.js": "nextjs", "next": "nextjs", "react-native": "react", "django-rest": "django"}

def resolve(name):
    name = name.lower().strip()
    if name in BLUEPRINTS: return name
    if name in ALIASES: return ALIASES[name]
    # keyword match
    for key in BLUEPRINTS:
        if key in name or name in key: return key
    return None

def get(name):
    b = resolve(name)
    if not b: return {"ok": False, "error": f"no blueprint for '{name}'", "available": list(BLUEPRINTS)}
    return {"ok": True, "name": b, **BLUEPRINTS[b]}

def catalog():
    return {"ok": True, "blueprints": {k: v["stack"] for k, v in BLUEPRINTS.items()}}

def scaffold(name, out_dir):
    """Write the blueprint's starter files into out_dir."""
    r = get(name)
    if not r["ok"]: return r
    root = pathlib.Path(out_dir); root.mkdir(parents=True, exist_ok=True)
    created = []
    for item in r["tree"]:
        p = root / item
        if item.endswith("/"): p.mkdir(parents=True, exist_ok=True); created.append(item); continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {item}\n") if p.suffix in (".md", ".py", ".js", ".jsx", ".ts", ".css", ".yaml", ".yml", ".json", ".sql") else p.write_text("")
        created.append(item)
    return {"ok": True, "name": r["name"], "created": created, "dir": str(root)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", action="store_true")
    ap.add_argument("--get", metavar="NAME")
    ap.add_argument("--scaffold", nargs=2, metavar=("NAME", "OUT_DIR"))
    args = ap.parse_args()
    if args.catalog:
        for k, v in catalog()["blueprints"].items(): print(f"  {k:10s} {v}")
        return
    if args.get:
        print(json.dumps(get(args.get), indent=2)); return
    if args.scaffold:
        print(json.dumps(scaffold(*args.scaffold), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
