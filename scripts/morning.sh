#!/bin/bash
# What launchd runs at 08:30 every day.
#
# Two jobs, in this order, on purpose:
#   1. PUBLISH anything edited since the last deploy. This is the self-heal:
#      if a session edited the wall and nobody published it, the phones still
#      get it the next morning instead of silently showing stale content.
#   2. SEND the digest — but only if something is actually due today.
#      Silence is a feature.
cd "$(dirname "$0")/.."
echo "───── $(date '+%Y-%m-%d %H:%M:%S') ─────"
scripts/deploy.sh "wall: morning auto-publish" || echo "⚠️  deploy failed — phones may be stale"
/usr/bin/python3 scripts/send_push.py --digest 2>&1 | grep -v "NotOpenSSLWarning\|warnings.warn"
