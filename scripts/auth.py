#!/usr/bin/env python3
"""
scripts/auth.py - Phase I1 Basic Auth
Password-hashed user store (06-data/users.json) + token sessions.
Login/logout/verify. Stdlib only (hashlib pbkdf2, secrets).
"""
import json, pathlib, hashlib, secrets, datetime, hmac

ROOT = pathlib.Path(__file__).resolve().parent.parent
USERS_PATH = ROOT / "06-data" / "users.json"
SESSIONS_PATH = ROOT / "06-data" / "sessions.json"

def _load(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default

def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def _hash_pw(password, salt=None):
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt, dk.hex()

def setup_user(username, password):
    """Create/update a user (first run: bootstraps the admin user)."""
    users = _load(USERS_PATH, {})
    salt, h = _hash_pw(password)
    users[username] = {"salt": salt, "hash": h, "created": datetime.datetime.now().isoformat(timespec="seconds")}
    _save(USERS_PATH, users)
    return {"ok": True, "user": username}

def login(username, password):
    users = _load(USERS_PATH, {})
    u = users.get(username)
    if not u:
        return {"ok": False, "error": "invalid credentials"}
    _, h = _hash_pw(password, u["salt"])
    if not hmac.compare_digest(h, u["hash"]):
        return {"ok": False, "error": "invalid credentials"}
    token = secrets.token_hex(24)
    sessions = _load(SESSIONS_PATH, {})
    sessions[token] = {"user": username, "created": datetime.datetime.now().isoformat(timespec="seconds")}
    _save(SESSIONS_PATH, sessions)
    return {"ok": True, "token": token, "user": username}

def logout(token):
    sessions = _load(SESSIONS_PATH, {})
    if token in sessions:
        del sessions[token]
        _save(SESSIONS_PATH, sessions)
    return {"ok": True}

def verify(token):
    sessions = _load(SESSIONS_PATH, {})
    s = sessions.get(token)
    if s:
        return {"ok": True, "user": s["user"]}
    return {"ok": False, "error": "invalid or expired token"}

def me(token):
    v = verify(token)
    if not v["ok"]:
        return v
    return {"ok": True, "user": v["user"]}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", nargs=2, metavar=("USER", "PASS"))
    ap.add_argument("--login", nargs=2, metavar=("USER", "PASS"))
    ap.add_argument("--verify", metavar="TOKEN")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--remove", metavar="USER")
    args = ap.parse_args()
    if args.setup:
        print(json.dumps(setup_user(*args.setup), indent=2)); return
    if args.login:
        print(json.dumps(login(*args.login), indent=2)); return
    if args.list:
        print(json.dumps(list_users(), indent=2)); return
    if args.remove:
        print(json.dumps(remove_user(args.remove), indent=2)); return
    if args.verify:
        print(json.dumps(verify(args.verify), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()


def list_users():
    users = _load(USERS_PATH, {})
    return {"ok": True, "users": [{"username": u, "created": d.get("created")} for u, d in users.items()]}

def remove_user(username):
    users = _load(USERS_PATH, {})
    if username not in users:
        return {"ok": False, "error": "user not found"}
    del users[username]
    _save(USERS_PATH, users)
    return {"ok": True, "removed": username}
