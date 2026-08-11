#!/usr/bin/env python3
"""Send BAC web-push notifications. Backend = this script, run from Claude sessions
or launchd/GitHub Actions.

Usage:
  python3 scripts/send_push.py --test "hello wall"
  python3 scripts/send_push.py --digest          # today's post-its (morning ping)
  python3 scripts/send_push.py --tomorrow        # tomorrow preview (evening ping)
  python3 scripts/send_push.py --item adami-105  # one specific post-it

Setup (once): pip3 install -r requirements.txt ; python3 scripts/gen_vapid.py
Subscriptions live in data/subscriptions.json:
  [ {"name": "inna", "sub": { ...subscription JSON from the app's 🔔 flow... }} ]
"""
import argparse, json, os, sys, datetime

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Lisbon")
except Exception:
    TZ = None

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

def today(offset=0):
    now = datetime.datetime.now(TZ) if TZ else datetime.datetime.now()
    return (now.date() + datetime.timedelta(days=offset)).isoformat()

def fmt(it):
    mins = f" — {it['minutes']} min" if it.get("minutes") else ""
    return f"{'✱ ' if it.get('hard') else ''}{it['title']}: {it.get('action') or 'it just happens'}{mins}"

def build(args, items):
    if args.test:
        return {"title": "BIG ASS CALENDAR ✳", "body": args.test, "tag": "bac-test"}
    if args.item:
        it = next((i for i in items if i["id"] == args.item), None)
        if not it:
            sys.exit(f"❌ no item '{args.item}'")
        return {"title": f"post-it: {it['title']}", "body": fmt(it), "tag": f"bac-{it['id']}"}
    day = today(1 if args.tomorrow else 0)
    due = [i for i in items if i["date"] == day and not i.get("done") and i["owner"] != "info"]
    if not due:
        return None
    label = "tomorrow" if args.tomorrow else "today"
    title = f"{len(due)} post-it{'s' if len(due) > 1 else ''} {label} ✳"
    return {"title": title, "body": " • ".join(fmt(i) for i in due)[:900], "tag": f"bac-{label}"}

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--test")
    g.add_argument("--digest", action="store_true")
    g.add_argument("--tomorrow", action="store_true")
    g.add_argument("--item")
    args = p.parse_args()

    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        sys.exit("❌ pip3 install -r requirements.txt first (needs 'pywebpush')")

    payload = build(args, load("todos.json")["items"])
    if payload is None:
        print("nothing due — no ping (silence is a feature)")
        return

    subs = load("subscriptions.json")
    if not subs:
        sys.exit("❌ data/subscriptions.json is empty — file Inna's blob from the app's 🔔 flow")
    priv = os.path.join(DATA, "vapid_private.pem")
    if not os.path.exists(priv):
        sys.exit("❌ no VAPID key — run scripts/gen_vapid.py")

    ok = 0
    for entry in subs:
        try:
            webpush(
                subscription_info=entry["sub"],
                data=json.dumps(payload),
                vapid_private_key=priv,
                vapid_claims={"sub": "mailto:contact@marcocontisikic.art"},
            )
            ok += 1
            print(f"📬 {entry.get('name', '?')} ✓")
        except WebPushException as e:
            code = getattr(e.response, "status_code", "?")
            print(f"⚠️  {entry.get('name', '?')}: {code} — {e}")
            if code in (404, 410):
                print("   subscription expired → she re-taps 🔔, you re-file the blob")
    print(f"done: {ok}/{len(subs)} delivered · payload: {payload['title']}")

if __name__ == "__main__":
    main()
