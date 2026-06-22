#!/usr/bin/env python3
"""
Hermes Vault — Credential retrieval for skills and scripts.
Usage: python3 scripts/hermes-vault-read.py <passphrase> <key1> [key2 ...]

Auto-downloads from OneDrive if local cache is missing or stale.
"""

import json, sys, os, base64, hashlib, tempfile
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
except ImportError:
    os.system("pip install cryptography -q")
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

VAULT_LOCAL = os.path.expanduser("~/.hermes-vault.json.enc")
VAULT_ONEDRIVE_PATH = ".vault/hermes-vault.json.enc"
HELPER = os.path.expanduser("~/.config/hermy/onedrive_graph.py")

def derive_key(passphrase, salt):
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def read_vault(passphrase):
    vault_path = VAULT_LOCAL

    # Try OneDrive refresh if local is missing
    if not os.path.exists(vault_path) and os.path.exists(HELPER):
        print("Local vault not found. Attempting OneDrive download...", file=sys.stderr)
        tmp = tempfile.mktemp(suffix=".json.enc")
        ret = os.system(
            f'python3 {HELPER} download "{VAULT_ONEDRIVE_PATH}" "{tmp}" 2>/dev/null'
        )
        if ret == 0 and os.path.exists(tmp):
            os.rename(tmp, vault_path)
            print(f"Downloaded from OneDrive to {vault_path}", file=sys.stderr)
        else:
            print("OneDrive download failed or helper not available.", file=sys.stderr)

    if not os.path.exists(vault_path):
        return None

    vault = json.loads(Path(vault_path).read_text())
    salt = base64.b64decode(vault["salt"])
    key = derive_key(passphrase, salt)
    f = Fernet(key)
    payload = f.decrypt(vault["ciphertext"].encode())
    return json.loads(payload)["entries"]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 hermes-vault-read.py <passphrase> <key1> [key2 ...]")
        sys.exit(1)

    passphrase = sys.argv[1]
    keys = sys.argv[2:]

    entries = read_vault(passphrase)
    if entries is None:
        print("VAULT_NOT_FOUND")
        sys.exit(1)

    result = {}
    for k in keys:
        if k in entries:
            result[k] = entries[k]

    print(json.dumps(result))
