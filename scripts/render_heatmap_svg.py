#!/usr/bin/env python3
"""Render the contributions JSON as a 53-week x 7-day calendar SVG.

Rounded boxes colored with a GitHub-ish green ramp, revealed once with
a diagonal line-after-line slide-down (CSS keyframes that play on load
and freeze), plus a Less->More legend and a stats footer.

Usage: python render_heatmap_svg.py [username]
Input: data/contributions.json (from fetch_contributions.py)
Output: contrib-heatmap.svg
Set STATIC=1 to emit a frozen frame for local preview.
"""
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

PITCH = 13
CELL = 11
RAD = 2
MARGIN_L = 34
MARGIN_T = 34
WEEKS = 53

BG = "#0d1117"
TEXT = "#8b949e"
BRIGHT = "#c9d1d9"

STATIC = os.environ.get("STATIC") == "1"


def level_for(count):
    if count <= 0:
        return 0
    if count <= 3:
        return 1
    if count <= 6:
        return 2
    if count <= 9:
        return 3
    if count <= 19:
        return 4
    return 5


def build_weeks(days_by_date, today):
    """Return list of 53 week-lists, each 7 entries (Sun..Sat) or None."""
    weeks = []
    for w in range(WEEKS - 1, -1, -1):
        sunday = today - timedelta(days=today.weekday() + 1) - timedelta(weeks=w)
        week = [days_by_date.get((sunday + timedelta(days=i)).isoformat(), 0)
                for i in range(7)]
        weeks.append(week)
    return weeks


def main():
    data_path = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
    if not data_path.exists():
        print(f"missing {data_path} (run fetch_contributions.py first)")
        sys.exit(1)
    data = json.loads(data_path.read_text())

    today = date.today()
    days_by_date = {d["date"]: d["count"] for d in data["days"]}
    weeks = build_weeks(days_by_date, today)

    canvas_w = MARGIN_L + WEEKS * PITCH + 14
    canvas_h = MARGIN_T + 7 * PITCH + 46

    cells = []
    for w, week in enumerate(weeks):
        for r, count in enumerate(week):
            x = MARGIN_L + w * PITCH
            y = MARGIN_T + r * PITCH
            delay = f"{((w + r) * 0.012):.3f}s"
            cls = "" if STATIC else f' class="cell" style="animation-delay:{delay}"'
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
                f'fill="{PALETTE[level_for(count)]}"{cls}/>'
            )

    labels = []
    seen_months = set()
    for w in range(WEEKS):
        sunday = today - timedelta(days=today.weekday() + 1) - timedelta(weeks=WEEKS - 1 - w)
        m = sunday.strftime("%b")
        if m not in seen_months:
            labels.append(f'<text x="{MARGIN_L + w * PITCH}" y="20" font-family="monospace" font-size="10" fill="{TEXT}">{m}</text>')
            seen_months.add(m)

    weekdays = ["Mon", "Wed", "Fri"]
    wd_labels = "".join(
        f'<text x="0" y="{MARGIN_T + (r * 2 + 1) * PITCH + 3}" text-anchor="middle" font-family="monospace" font-size="10" fill="{TEXT}">{w}</text>'
        for r, w in enumerate(weekdays)
    )

    legend = "".join(
        f'<rect x="{614 + i * 17}" y="{MARGIN_T + 7 * PITCH + 8}" width="11" height="11" rx="2" fill="{PALETTE[i]}"/>'
        for i in range(6)
    )
    legend = (
        f'<text x="570" y="{MARGIN_T + 7 * PITCH + 17}" font-family="monospace" font-size="10" fill="{TEXT}">Less</text>'
        + legend
        + f'<text x="{614 + 6 * 17}" y="{MARGIN_T + 7 * PITCH + 17}" font-family="monospace" font-size="10" fill="{TEXT}">More</text>'
    )

    total = data.get("total", sum(d["count"] for d in data["days"]))
    footer = (
        f'<text x="{MARGIN_L}" y="{canvas_h - 10}" font-family="monospace" font-size="12" fill="{BRIGHT}">'
        f'{total:,} contributions in the last year · '
        f'best day {data["best_day"]["count"]} · '
        f'current streak {data["current_streak"]} · '
        f'longest streak {data["longest_streak"]}</text>'
    )

    style = "" if STATIC else """
<style>
.cell { animation: drop 0.45s both; }
@keyframes drop { from { opacity: 0; transform: translateY(-9px); } to { opacity: 1; transform: translateY(0); } }
</style>
"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">
<rect width="100%" height="100%" fill="{BG}"/>
{style}{chr(10).join(labels)}
{wd_labels}
{chr(10).join(cells)}
{legend}
{footer}
</svg>
"""
    out = Path("contrib-heatmap.svg")
    out.write_text(svg)
    print(f"wrote {out} ({len(cells)} cells, animated={not STATIC})")


if __name__ == "__main__":
    main()
