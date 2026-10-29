#!/usr/bin/env python3
"""Generates the FerryOS logo SVGs in this folder.

The wordmark is converted to outlines, so the SVGs don't need the font installed.
Usage: python3 generate.py path/to/outfit-latin-600-normal.woff
"""

import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).parent

TEAL = "#0E8A8A"
NAVY = "#12324A"
SAND = "#F6EFE3"
SUNSET = "#FF8A4C"


def symbol(x=0, y=0, size=512):
    """The app icon: ferry on two waves with a rising sun, on a teal tile."""
    s = size / 512
    return f"""<g transform="translate({x} {y}) scale({s})">
  <rect width="512" height="512" rx="112" fill="{TEAL}"/>
  <g transform="translate(0 -14)">
  <circle cx="334" cy="214" r="72" fill="{SUNSET}"/>
  <rect x="268" y="170" width="30" height="54" rx="6" fill="#FFFFFF"/>
  <rect x="164" y="214" width="166" height="74" rx="14" fill="#FFFFFF"/>
  <rect x="186" y="236" width="30" height="24" rx="5" fill="{TEAL}"/>
  <rect x="232" y="236" width="30" height="24" rx="5" fill="{TEAL}"/>
  <rect x="278" y="236" width="30" height="24" rx="5" fill="{TEAL}"/>
  <path d="M100 300 H412 L384 352 Q376 366 360 366 H152 Q136 366 128 352 Z" fill="#FFFFFF"/>
  <path d="M96 396 q40 -26 80 0 t80 0 t80 0 t80 0" fill="none" stroke="#FFFFFF" stroke-width="16" stroke-linecap="round"/>
  <path d="M136 436 q40 -26 80 0 t80 0 t80 0" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="16" stroke-linecap="round"/>
  </g>
</g>"""


def symbolic(size=16):
    """Single-color icon for small sizes (panels, favicons): hull and one wave."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 512 512">
  <path d="M60 236 H452 L414 312 Q404 332 382 332 H130 Q108 332 98 312 Z" fill="currentColor"/>
  <rect x="150" y="140" width="190" height="80" rx="16" fill="currentColor"/>
  <path d="M56 410 q50 -36 100 0 t100 0 t100 0 t100 0" fill="none" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
</svg>
"""


def text_path(font, text, x, y, size):
    """Converts text to one SVG path with its baseline at (x, y). Returns (path, width)."""
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyph_set)
    advance = 0
    for char in text:
        name = cmap[ord(char)]
        transform = (scale, 0, 0, -scale, x + advance * scale, y)
        glyph_set[name].draw(TransformPen(pen, transform))
        advance += glyph_set[name].width
    return pen.getCommands(), advance * scale


def wordmark(font, x, y, size, ferry_color, os_color):
    ferry, ferry_width = text_path(font, "ferry", x, y, size)
    os_path, os_width = text_path(font, "os", x + ferry_width, y, size)
    paths = f'<path d="{ferry}" fill="{ferry_color}"/>\n<path d="{os_path}" fill="{os_color}"/>'
    return paths, ferry_width + os_width


def svg(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n{body}\n</svg>\n'
    )


def main():
    font = TTFont(sys.argv[1])

    (OUT / "ferryos-logo.svg").write_text(svg(512, 512, symbol()))
    (OUT / "ferryos-logo-symbolic.svg").write_text(symbolic())

    # Horizontal lockup: icon + wordmark, for light backgrounds
    body, width = wordmark(font, 152, 98, 112, NAVY, TEAL)
    total = int(152 + width + 16)
    (OUT / "ferryos-lockup.svg").write_text(svg(total, 128, symbol(0, 0, 128) + "\n" + body))

    # Same for dark backgrounds
    body, width = wordmark(font, 152, 98, 112, SAND, "#3CC4C4")
    (OUT / "ferryos-lockup-dark.svg").write_text(svg(total, 128, symbol(0, 0, 128) + "\n" + body))


if __name__ == "__main__":
    main()
