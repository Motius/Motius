#!/usr/bin/env python3
"""Convert a prepped grayscale photo into a self-typing ASCII SVG.

Reads source-prepped.png, downsamples to a character grid, picks a glyph
from a density ramp per cell, and renders one <text> row per grid row.
Each row is clipped by a horizontally-expanding rect and a small block
cursor rides the wipe edge, staggered top to bottom. Plays once, freezes.

Usage: python make_ascii_svg.py [prepped.png]
Output: motius-ascii.svg
Set STATIC=1 to emit a frozen frame (no animation) for local preview.
"""
import os
import sys
from pathlib import Path

from PIL import Image
import numpy as np

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

FONT_SIZE = 10
CELL_W = FONT_SIZE * 0.6
CELL_H = FONT_SIZE * 1.15
COLS = 100
ROWS = 53

FG = "#c9d1d9"
BG = "#0d1117"
CURSOR = "#58a6ff"
FONT_FAMILY = "'JetBrains Mono','Fira Code','Menlo','Consolas',monospace"

STATIC = os.environ.get("STATIC") == "1"


def load_grid(path):
    img = Image.open(path).convert("L")
    w, h = img.size
    scale = min((COLS - 2) / w, (ROWS - 2) / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    return np.asarray(img), nw, nh


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-prepped.png")
    if not src.exists():
        print(f"no prepped image found: {src} (run prep_photo.py first)")
        sys.exit(1)

    grid, nw, nh = load_grid(src)
    canvas_w = COLS * CELL_W
    canvas_h = ROWS * CELL_H
    x_off = (COLS - nw) * CELL_W / 2
    y_off = (ROWS - nh) * CELL_H / 2

    rows = []
    for j in range(nh):
        s = "".join(RAMP[int((255 - grid[j, i]) / 255 * (len(RAMP) - 1) + 0.5)]
                    for i in range(nw))
        rows.append((j, s))

    dur = 1.1
    stagger = 0.055

    if STATIC:
        body = "".join(
            f'<text x="{x_off:.1f}" y="{y_off + (j + 1) * CELL_H - CELL_H * 0.28:.1f}" '
            f'font-family="{FONT_FAMILY}" font-size="{FONT_SIZE}" '
            f'letter-spacing="0" fill="{FG}">{s}</text>\n'
            for j, s in rows
        )
    else:
        defs = []
        texts = []
        cursors = []
        for j, s in rows:
            row_y = y_off + (j + 1) * CELL_H - CELL_H * 0.28
            total_w = len(s) * CELL_W
            clip_id = f"row{j}"
            begin = f"{j * stagger:.2f}s"
            defs.append(
                f'<clipPath id="{clip_id}"><rect x="{x_off:.1f}" y="{row_y - CELL_H + CELL_H * 0.28:.1f}" '
                f'height="{CELL_H:.2f}">'
                f'<animate attributeName="width" from="0" to="{total_w:.1f}" '
                f'dur="{dur}s" begin="{begin}" fill="freeze"/>'
                f"</rect></clipPath>"
            )
            texts.append(
                f'<text x="{x_off:.1f}" y="{row_y:.1f}" clip-path="url(#{clip_id})" '
                f'font-family="{FONT_FAMILY}" font-size="{FONT_SIZE}" fill="{FG}">{s}</text>'
            )
            cursors.append(
                f'<rect y="{row_y - CELL_H + CELL_H * 0.28:.1f}" width="7" height="{CELL_H:.2f}" '
                f'fill="{CURSOR}" opacity="0.85">'
                f'<animate attributeName="x" from="-7" to="{x_off + total_w - 7:.1f}" '
                f'dur="{dur}s" begin="{begin}" fill="freeze"/>'
                f"</rect>"
            )
        body = (
            "<defs>\n" + "\n".join(defs) + "\n</defs>\n"
            + "\n".join(texts) + "\n" + "\n".join(cursors)
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.0f}" height="{canvas_h:.0f}" viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}">
<rect width="100%" height="100%" fill="{BG}"/>
{body}
</svg>
"""
    out = Path("motius-ascii.svg")
    out.write_text(svg)
    print(f"wrote {out} ({nw}x{nh} chars, animated={not STATIC})")


if __name__ == "__main__":
    main()
