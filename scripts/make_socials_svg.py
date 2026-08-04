#!/usr/bin/env python3
"""Render a self-hosted socials strip for the profile README.

Scrapes the public profile HTML (no token) for follower/following/repo
counts and renders a terminal-styled links row with the user's socials.

Usage: python make_socials_svg.py [username]
Output: socials.svg
Set STATIC=1 to emit a frozen frame for local preview.
"""
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "motius"
BG = "#0d1117"
FG = "#c9d1d9"
DIM = "#8b949e"
ACCENT = "#58a6ff"
FONT = "'JetBrains Mono','Fira Code','Menlo','Consolas',monospace"
STATIC = os.environ.get("STATIC") == "1"

SOCIALS = [
    ("instagram", "mo_tius", "https://instagram.com/mo_tius"),
    ("tiktok", "motius_ke", "https://tiktok.com/@motius_ke"),
    ("web", "ignadevs.online", "https://ignadevs.online"),
    ("github", "Motius", "https://github.com/Motius"),
]


def fetch_counts():
    resp = requests.get(f"https://github.com/{USERNAME}", timeout=30,
                        headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    def num(label):
        if label == "repositories":
            m = re.search(r"repositor[a-z]*\s+(\d+)|(\d[\d,]*|one|two|three|four|five|six|seven|eight|nine)\s+repositor", text, re.I)
            if m:
                val = m.group(1) or m.group(2)
                if val.isalpha():
                    return str(["zero", "one", "two", "three", "four", "five",
                                "six", "seven", "eight", "nine"].index(val.lower()))
                return val.replace(",", "")
            return "?"
        m = re.search(r"(\d[\d,]*)\s*" + label, text, re.I)
        return m.group(1).replace(",", "") if m else "?"
    return num("followers"), num("following"), num("repositories")


def main():
    followers, following, repos = fetch_counts()
    chips = [f"@{USERNAME} · {followers} followers · {following} following · {repos} repos"]
    width = 490
    y0 = 34
    pitch = 34

    chip = ""
    for i, chip_text in enumerate(chips):
        fade = "" if STATIC else (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.2s" fill="freeze"/>'
        )
        chip = (f'<g opacity="1">'
                f'<rect x="24" y="{y0 - 22}" width="{width - 48}" height="24" rx="4" fill="#161b22" stroke="#30363d"/>'
                f'<text x="36" y="{y0 - 5}" font-family="{FONT}" font-size="12" fill="{ACCENT}">gh</text>'
                f'<text x="58" y="{y0 - 5}" font-family="{FONT}" font-size="12" fill="{FG}">{chip_text}</text>'
                f'{fade}</g>')

    links = []
    for i, (name, handle, url) in enumerate(SOCIALS):
        y = y0 + 24 + i * pitch
        fade = "" if STATIC else (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{0.5 + i * 0.15:.2f}s" fill="freeze"/>'
            f'<animate attributeName="transform" type="translate" from="0 5" to="0 0" dur="0.4s" begin="{0.5 + i * 0.15:.2f}s" fill="freeze"/>'
        )
        links.append(
            f'<g opacity="1">'
            f'<text x="36" y="{y}" font-family="{FONT}" font-size="12" fill="{ACCENT}">{name}</text>'
            f'<text x="140" y="{y}" font-family="{FONT}" font-size="12" fill="{FG}">{handle}</text>'
            f'<text x="300" y="{y}" font-family="{FONT}" font-size="11" fill="{DIM}">{url}</text>'
            f'{fade}</g>'
        )
    height = y0 + 24 + len(SOCIALS) * pitch + 12

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="{BG}"/>
{chip}
{chr(10).join(links)}
</svg>
"""
    out = Path("socials.svg")
    out.write_text(svg)
    print(f"wrote {out}: followers={followers} following={following} repos={repos}")


if __name__ == "__main__":
    main()
