#!/bin/bash
# Publish the wall. One command, no prompts, safe to run twice.
#   validate → encrypt → commit → push
# The passphrase comes from the macOS Keychain (see encrypt_data.py: from_keychain).
# Store it once:  security add-generic-password -U -a wall-passphrase -s bigass-calendar -w
#
# Usage:  scripts/deploy.sh ["commit message"]
set -euo pipefail
cd "$(dirname "$0")/.."

PY=/usr/bin/python3
MARK=data/.deployed.sha256

# 1. schema check — refuses to publish a broken wall
"$PY" scripts/validate.py >/dev/null

# 2. has the content actually changed since the last publish?
#    (encryption uses a fresh random salt+IV every run, so the ciphertext always
#     differs — comparing it would commit on every invocation. Hash the plaintext.)
NOW=$("$PY" -c "import hashlib;print(hashlib.sha256(open('data/todos.json','rb').read()).hexdigest())")
WAS=$(cat "$MARK" 2>/dev/null || echo "")
OTHER=$(git status --porcelain -- ':!data' | head -1)

if [ "$NOW" = "$WAS" ] && [ -z "$OTHER" ]; then
  echo "nothing to publish — wall already live and unchanged"
  exit 0
fi

# 3. stamp, encrypt, publish
"$PY" scripts/validate.py --touch >/dev/null
"$PY" scripts/encrypt_data.py
git add -A
if git diff --cached --quiet; then
  echo "nothing staged — no push"
  exit 0
fi
git -c user.name="${GIT_AUTHOR_NAME:-mcsk}" -c user.email="${GIT_AUTHOR_EMAIL:-mcsk@Mac.Home}" \
    commit -q -m "${1:-wall: update $(date '+%Y-%m-%d %H:%M')}"
GIT_SSH_COMMAND="ssh -o BatchMode=yes" git push -q origin main

"$PY" -c "import hashlib;open('$MARK','w').write(hashlib.sha256(open('data/todos.json','rb').read()).hexdigest())"
echo "✅ published — $("$PY" -c "import json;print(len(json.load(open('data/todos.json'))['items']))") items live at https://mcsikic.github.io/bigass-calendar/"
