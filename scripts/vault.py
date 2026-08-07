#!/usr/bin/env python3
"""
scripts/vault.py - Phase I3 Secret Vault
Encrypts sensitive fields (API keys, tokens, passwords) at rest with Fernet
(AES-128-CBC + HMAC), key derived from a master passphrase (PBKDF2).
Vault file: 06-data/vault.json (encrypted). Decrypt-on-use for connectors.
"""
import json, pathlib, base64, os, getpass, sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = pathlib.Path(__file__).resolve().parent.parent
VAULT_PATH = ROOT / "06-data" / "vault.json"
MASTER_KEY_ENV = "RICHARD_MASTER_KEY"
KEY_FILE = ROOT / "06-data" / ".vault_key"

def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def _get_key() -> bytes:
    """Key from env, key file, or prompt (first run generates + saves key file)."""
    env = os.environ.get(MASTER_KEY_ENV)
    if env:
        return env.encode() if len(env) == 44 else base64.urlsafe_b64encode(env.encode())[:44]
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip().encode()
    key = Fernet.generate_key()
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(key.decode())
    os.chmod(KEY_FILE, 0o600)
    return key

def _fernet() -> Fernet:
    return Fernet(_get_key())

def save_secret(name: str, value: str):
    """Encrypt + store a secret (e.g. gmail app password, github token)."""
    vault = {}
    if VAULT_PATH.exists():
        try:
            vault = json.loads(_fernet().decrypt(VAULT_PATH.read_bytes()).decode())
        except Exception:
            vault = {}
    vault[name] = value
    blob = _fernet().encrypt(json.dumps(vault).encode())
    VAULT_PATH.write_bytes(blob)
    return {"ok": True, "stored": name}

def get_secret(name: str):
    """Decrypt + return a secret (None if not present)."""
    if not VAULT_PATH.exists():
        return None
    try:
        vault = json.loads(_fernet().decrypt(VAULT_PATH.read_bytes()).decode())
        return vault.get(name)
    except Exception:
        return None

def list_names():
    if not VAULT_PATH.exists():
        return []
    try:
        vault = json.loads(_fernet().decrypt(VAULT_PATH.read_bytes()).decode())
        return list(vault.keys())
    except Exception:
        return []

def delete_secret(name: str):
    if not VAULT_PATH.exists():
        return {"ok": False, "error": "vault empty"}
    vault = json.loads(_fernet().decrypt(VAULT_PATH.read_bytes()).decode())
    if name in vault:
        del vault[name]
        VAULT_PATH.write_bytes(_fernet().encrypt(json.dumps(vault).encode()))
        return {"ok": True, "deleted": name}
    return {"ok": False, "error": "not found"}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"))
    ap.add_argument("--get", metavar="NAME")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--delete", metavar="NAME")
    args = ap.parse_args()
    if args.set:
        print(json.dumps(save_secret(*args.set), indent=2)); return
    if args.get:
        print(json.dumps({"name": args.get, "value": get_secret(args.get)}, indent=2)); return
    if args.list:
        print("secrets:", list_names()); return
    if args.delete:
        print(json.dumps(delete_secret(args.delete), indent=2)); return
    ap.print_help()

if __name__ == "__main__":
    main()
