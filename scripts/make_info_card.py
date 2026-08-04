#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG.

A title bar with traffic-light dots, then colored key/value rows
(Now, Prev, Stack, Highlights). Each line fades and slides in on a
short stagger so the panel looks like it's printing.

Usage: python make_info_card.py
Output: info-card.svg
Set STATIC=1 to emit a frozen frame for local preview.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 490, 370
BG = "#0d1117"
BORDER = "#30363d"
VALUE = "#c9d1d9"
DIM = "#8b949e"

FONT = "'JetBrains Mono','Fira Code','Menlo','Consolas',monospace"
STATIC = os.environ.get("STATIC") == "1"

USERNAME = "motius"

# key, value, key color
ROWS = [
    ("user", "motius", "#79c0ff"),
    ("os", "github", "#7ee787"),
    ("host", "profile", "#7ee787"),
    ("shell", "markdown", "#ffa657"),
    ("editor", "readme.md", "#ffa657"),
    ("now", "building open tools", "#d2a8ff"),
    ("prev", "infra & automation", "#d2a8ff"),
    ("stack", "python · go · kubernetes · terraform", "#ff7b72"),
    ("highlights", "open source · cloud native · edge", "#ff7b72"),
]

TITLE = f"{USERNAME}@github"


def make_line(y, key, value, color, index):
    begin = f"{0.15 + index * 0.22:.2f}s"
    if STATIC:
        anim = ""
    else:
        anim = (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{begin}" fill="freeze"/>'
            f'<animate attributeName="transform" type="translate" from="0 6" to="0 0" dur="0.35s" begin="{begin}" fill="freeze"/>'
        )
    return (
        f'<g opacity="1">'
        f'<text x="24" y="{y}" font-family="{FONT}" font-size="13" fill="{color}">{escape(key)}</text>'
        f'<text x="140" y="{y}" font-family="{FONT}" font-size="13" fill="{VALUE}">{escape(value)}</text>'
        f"{anim}"
        f"</g>"
    )


def main():
    lines = [make_line(78 + i * 27, k, v, c, i) for i, (k, v, c) in enumerate(ROWS)]
    last_y = 78 + (len(ROWS) - 1) * 27
    footer_y = last_y + 38

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="6" fill="{BG}" stroke="{BORDER}"/>
<rect x="1" y="1" width="{W - 2}" height="30" rx="6" fill="#161b22"/>
<circle cx="22" cy="16" r="5" fill="#ff5f56"/>
<circle cx="40" cy="16" r="5" fill="#ffbd2e"/>
<circle cx="58" cy="16" r="5" fill="#27c93f"/>
<text x="{W / 2:.0f}" y="21" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{DIM}">{TITLE}</text>
{chr(10).join(lines)}
<line x1="24" y1="{footer_y - 16}" x2="{W - 24}" y2="{footer_y - 16}" stroke="{BORDER}"/>
<text x="24" y="{footer_y}" font-family="{FONT}" font-size="12" fill="{DIM}">2 packages · 0 open issues · README.md</text>
</svg>
"""
    out = Path("info-card.svg")
    out.write_text(svg)
    print(f"wrote {out} (animated={not STATIC})")


if __name__ == "__main__":
    main()
