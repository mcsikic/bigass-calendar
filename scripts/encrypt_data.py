#!/usr/bin/env python3
"""Encrypt data/todos.json → data/todos.enc.json (AES-256-GCM, PBKDF2 key).

Usage:  python3 scripts/encrypt_data.py
        python3 scripts/encrypt_data.py --passphrase "..."   # non-interactive

The passphrase is NEVER stored in the repo or echoed into any file.
"""
import base64, json, os, sys, getpass, subprocess
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITERATIONS = 300_000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "data", "todos.json")
DST  = os.path.join(ROOT, "data", "todos.enc.json")

KC_SERVICE = "bigass-calendar"
KC_ACCOUNT = "wall-passphrase"

def from_keychain():
    """Read the passphrase from the macOS login Keychain, so publishing needs no
    human at the keyboard. Store it once with:
        security add-generic-password -U -a wall-passphrase -s bigass-calendar -w
    (put -w last: security then prompts, so it never enters shell history)."""
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", KC_ACCOUNT, "-s", KC_SERVICE, "-w"],
            capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.rstrip("\n")
    except Exception:
        pass
    return None

def derive_key(passphrase: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=ITERATIONS)
    return kdf.derive(passphrase)

def encrypt(plaintext: bytes, passphrase: bytes) -> dict:
    salt = os.urandom(16)
    iv   = os.urandom(12)
    key  = derive_key(passphrase, salt)
    ct   = AESGCM(key).encrypt(iv, plaintext, None)
    return {
        "v": 1,
        "salt": base64.b64encode(salt).decode(),
        "iter": ITERATIONS,
        "iv":   base64.b64encode(iv).decode(),
        "ct":   base64.b64encode(ct).decode(),
    }

def main():
    if not os.path.exists(SRC):
        sys.exit(f"Missing {SRC}")

    pw = None
    if "--passphrase" in sys.argv:
        idx = sys.argv.index("--passphrase")
        if idx + 1 < len(sys.argv):
            pw = sys.argv[idx + 1]
    if pw is None:
        pw = from_keychain()          # lets deploy run unattended
    if pw is None:
        pw = getpass.getpass("Passphrase (not in the Keychain — type it): ")
    if not pw:
        sys.exit("Empty passphrase — aborting.")

    plaintext = open(SRC, "rb").read()
    envelope  = encrypt(plaintext, pw.encode("utf-8"))

    with open(DST, "w") as f:
        json.dump(envelope, f)
    print(f"Encrypted {len(plaintext)} B → {DST}")

if __name__ == "__main__":
    main()
