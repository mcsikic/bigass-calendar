#!/usr/bin/env python3
"""Validate data/todos.json against the BAC contract. Stdlib only.

Usage:
  python3 scripts/validate.py           # check
  python3 scripts/validate.py --touch   # check + refresh "updated" timestamp
"""
import json, sys, os, re, datetime

ROOT = os.path.join(os.path.dirname(__file__), "..")
PATH = os.path.join(ROOT, "data", "todos.json")
OWNERS = {"M", "I", "both", "info"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def fail(msg):
    print(f"❌ {msg}"); sys.exit(1)

with open(PATH) as f:
    data = json.load(f)

items = data.get("items", [])
ids = [it.get("id") for it in items]
if len(ids) != len(set(ids)):
    fail("duplicate ids: " + str(sorted({i for i in ids if ids.count(i) > 1})))

per_day = {}
warnings = []
for it in items:
    ctx = it.get("id", "<no-id>")
    for field in ("id", "title", "owner", "date"):
        if not it.get(field):
            fail(f"{ctx}: missing '{field}'")
    if it["owner"] not in OWNERS:
        fail(f"{ctx}: owner '{it['owner']}' not in {OWNERS}")
    if not DATE_RE.match(it["date"]):
        fail(f"{ctx}: bad date '{it['date']}' (want YYYY-MM-DD)")
    datetime.date.fromisoformat(it["date"])  # raises if invalid
    if it.get("blocked_by") and it["blocked_by"] not in ids:
        fail(f"{ctx}: blocked_by '{it['blocked_by']}' does not exist")
    if it["owner"] != "info" and not it.get("action"):
        warnings.append(f"{ctx}: no next action (spec rule: every deadline carries one)")
    if it.get("minutes", 0) and it["minutes"] > 30 and it["owner"] != "info":
        warnings.append(f"{ctx}: action is {it['minutes']} min (>30 — split it?)")
    per_day.setdefault(it["date"], 0)
    per_day[it["date"]] += 1

for day, n in sorted(per_day.items()):
    if n > 3:
        warnings.append(f"{day}: {n} post-its — the wall works because it is SPARSE")

print(f"✅ {len(items)} items valid · {len([i for i in items if i.get('done')])} done · "
      f"{len([i for i in items if i.get('hard')])} hard dates")
for w in warnings:
    print(f"⚠️  {w}")

if "--touch" in sys.argv:
    data["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"🕐 updated → {data['updated']}")
