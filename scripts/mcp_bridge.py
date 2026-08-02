#!/usr/bin/env python3
"""Richard OS — MCP layer: tool registry + dispatch for agents."""
import json, os, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "tools" / "tools_config.json").read_text())

def _env():
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def list_tools():
    return {name: cfg["description"] for name, cfg in CONFIG.items()}

def call_tool(name, params=None):
    """Dispatch a tool call. This is the MCP 'invoke' point."""
    params = params or {}
    _env()
    if name not in CONFIG:
        return {"error": f"Unknown tool: {name}"}

    if name == "web":
        from duckduckgo_search import DDGS
        results = list(DDGS().text(params.get("query", ""), max_results=5))
        return {"results": [{"title": r["title"], "href": r["href"], "body": r["body"][:200]} for r in results]}

    if name == "weather":
        import urllib.request, json as j
        city = params.get("city", "Bengaluru")
        geocode = j.loads(urllib.request.urlopen(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").read())
        lat, lon = geocode["results"][0]["latitude"], geocode["results"][0]["longitude"]
        w = j.loads(urllib.request.urlopen(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").read())
        cw = w["current_weather"]
        return {"city": city, "temp_c": cw["temperature"], "windspeed": cw["windspeed"]}

    if name == "github":
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            return {"error": "GITHUB_TOKEN not set in .env"}
        import urllib.request
        repo = params.get("repo", "Sujith-richard/richard-os")
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})
        data = json.loads(urllib.request.urlopen(req).read())
        return {"repo": repo, "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0), "open_issues": data.get("open_issues_count", 0)}

    if name == "email":
        # IMAP read (needs EMAIL_APP_PASSWORD in .env)
        import imaplib, email as em
        user = os.environ.get("EMAIL_ADDRESS", "")
        pwd = os.environ.get("EMAIL_APP_PASSWORD", "")
        if not user or not pwd:
            return {"error": "EMAIL_ADDRESS / EMAIL_APP_PASSWORD not set in .env"}
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user, pwd)
        imap.select("INBOX")
        _, ids = imap.search(None, "ALL")
        out = []
        for num in ids[0].split()[:5]:
            _, data = imap.fetch(num, "(RFC822)")
            msg = em.message_from_bytes(data[0][1])
            out.append({"from": msg["From"], "subject": msg["Subject"]})
        imap.logout()
        return {"emails": out}

    return {"error": f"Tool '{name}' has no handler"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Tools:", json.dumps(list_tools(), indent=2))
        sys.exit(0)
    name = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(call_tool(name, params), indent=2, default=str))
