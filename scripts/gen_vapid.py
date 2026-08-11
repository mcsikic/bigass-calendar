#!/usr/bin/env python3
"""Generate VAPID keys for BAC web push (one time).

Writes:
  data/vapid_private.pem   — NEVER commit (gitignored)
  data/vapid_public.txt    — served to the app; safe to publish

Needs the 'cryptography' package (comes with pywebpush):
  pip3 install -r requirements.txt
"""
import base64, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRIV = os.path.join(ROOT, "data", "vapid_private.pem")
PUB = os.path.join(ROOT, "data", "vapid_public.txt")

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
except ImportError:
    sys.exit("❌ pip3 install -r requirements.txt first (needs 'cryptography')")

if os.path.exists(PRIV) and "--force" not in sys.argv:
    sys.exit(f"❌ {PRIV} exists — rerun with --force to overwrite (old subscriptions die!)")

key = ec.generate_private_key(ec.SECP256R1())
with open(PRIV, "wb") as f:
    f.write(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))
os.chmod(PRIV, 0o600)

point = key.public_key().public_bytes(
    serialization.Encoding.X962,
    serialization.PublicFormat.UncompressedPoint)
pub = base64.urlsafe_b64encode(point).rstrip(b"=").decode()
with open(PUB, "w") as f:
    f.write(pub + "\n")

print(f"✅ private → {PRIV} (gitignored, chmod 600)")
print(f"✅ public  → {PUB}")
print(f"   applicationServerKey: {pub}")
