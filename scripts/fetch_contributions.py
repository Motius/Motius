#!/usr/bin/env python3
"""Fetch a user's real contribution calendar — no token needed.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions. Parse the day cells
with BeautifulSoup and write data/contributions.json with raw days plus
derived stats (current streak, longest streak, best day, monthly totals).

Usage: python fetch_contributions.py [username]
Output: data/contributions.json
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "motius"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse_count(td):
    try:
        return int(td.get("data-count", "0"))
    except ValueError:
        return 0


def count_from_tooltip(tooltip):
    """New calendar format: <tool-tip> holds the exact count text,
    e.g. 'No contributions on August 3rd.' or '3 contributions on March 2nd.'"""
    text = tooltip.get_text(" ", strip=True)
    m = re.search(r"(\d+)\s+contributions?", text)
    if m:
        return int(m.group(1))
    return 0


def main():
    url = f"https://github.com/users/{USERNAME}/contributions"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    tooltips = {t.get("for"): t for t in soup.select("tool-tip")}
    days = []
    for td in soup.select("td[data-date]"):
        count = parse_count(td)
        if count == 0 and td.get("id") and td["id"] in tooltips:
            count = count_from_tooltip(tooltips[td["id"]])
        days.append({"date": td["data-date"], "count": count})
    if not days:
        print("no day cells found — did the page change?")
        sys.exit(1)

    days.sort(key=lambda d: d["date"])
    by_day = {d["date"]: d["count"] for d in days}
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    today = date.today()
    current = 0
    for i in range(400):
        day = (today - timedelta(days=i)).isoformat()
        if by_day.get(day, 0) > 0:
            current += 1
        else:
            break

    longest = 0
    run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "current_streak": current,
        "longest_streak": longest,
        "monthly": dict(monthly),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT}: {len(days)} days, {total} contributions")


if __name__ == "__main__":
    main()
