#!/usr/bin/env python3
"""Prep a flat photo for ASCII conversion:
   1. Remove the background (rembg) so the subject is isolated.
   2. Boost local contrast with OpenCV CLAHE.
   3. Composite onto pure white so the background maps to spaces.

Usage: python prep_photo.py source-photo.jpg
Output: source-prepped.png
"""
import sys
from pathlib import Path

from PIL import Image
import numpy as np
import cv2
from rembg import remove


def main():
    if len(sys.argv) != 2:
        print("usage: python prep_photo.py <photo.jpg>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"no such file: {src}")
        sys.exit(1)

    print("loading photo...")
    img = Image.open(src).convert("RGBA")

    print("removing background...")
    img = remove(img)  # returns RGBA with subject isolated

    print("boosting contrast (CLAHE)...")
    rgb = np.array(img)
    alpha = rgb[:, :, 3:4] / 255.0
    gray = cv2.cvtColor(rgb[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    print("compositing onto white...")
    white = np.full_like(gray, 255)
    out = (gray.astype(np.float32) * alpha[..., 0] +
           white.astype(np.float32) * (1.0 - alpha[..., 0]))
    out = out.astype(np.uint8)

    dst = src.with_name("source-prepped.png")
    Image.fromarray(out, "L").save(dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
