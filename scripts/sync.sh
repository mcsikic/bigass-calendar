#!/bin/bash
# Hourly safety net: if the wall on the Mac is ahead of the wall on the internet,
# publish it. Silent by design — nothing is sent to the phones, no notification.
#
# This exists because "the session publishes after editing" is a rule, and rules
# get missed (12 Aug: 29 items edited, never published, phones stale all day).
# deploy.sh no-ops when nothing changed, so running this every hour is free.
#
# Only writes to the log when it ACTUALLY publishes, or when something breaks —
# so a quiet log means everything is in sync.
cd "$(dirname "$0")/.."
OUT=$(scripts/deploy.sh "wall: hourly auto-publish" 2>&1)
CODE=$?
if [ $CODE -ne 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S')  ⚠️  publish FAILED (exit $CODE)"
  echo "$OUT" | sed 's/^/    /'
elif echo "$OUT" | grep -q "published"; then
  echo "$(date '+%Y-%m-%d %H:%M:%S')  $(echo "$OUT" | grep 'published')"
fi
exit 0
