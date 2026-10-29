#!/usr/bin/env python3
"""Generates the FerryOS logo files in this folder.

The emblem is six boat hulls arranged in a ring around a sun, in one color.
The wordmark is converted to outlines, so the SVGs don't need the font installed.

Usage: python3 generate.py path/to/outfit-latin-600-normal.woff
Needs: pip install fonttools brotli shapely
"""

import math
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

OUT = Path(__file__).parent
FASTFETCH_LOGO = OUT.parent / "system_files/usr/share/ferryos/ferryos-fastfetch.txt"

TEAL = "#0E8A8A"
TEAL_LIGHT = "#5CC8C2"
NAVY = "#12324A"
SAND = "#F6EFE3"

CENTER = (256, 256)
SUN_RADIUS = 40
GAP = 10

# "FerryOS" in figlet's standard font
WORDMARK_ASCII = r"""
 _____                     ___  ____
|  ___|__ _ __ _ __ _   _ / _ \/ ___|
| |_ / _ \ '__| '__| | | | | | \___ \
|  _|  __/ |  | |  | |_| | |_| |___) |
|_|  \___|_|  |_|   \__, |\___/|____/
                    |___/
""".strip("\n").splitlines()


def hull(angle, inner=70, outer=140, length=250, slant=52, shift=50):
    """One boat hull (trapezoid) on the ring; the narrow keel side faces outward."""
    normal = (math.cos(angle), -math.sin(angle))
    tangent = (-math.sin(angle), -math.cos(angle))

    def point(u, v):
        return (CENTER[0] + u * tangent[0] + v * normal[0], CENTER[1] + u * tangent[1] + v * normal[1])

    return Polygon([
        point(-length / 2 + shift, inner),
        point(length / 2 + shift, inner),
        point(length / 2 - slant + shift, outer),
        point(-length / 2 + slant + shift, outer),
    ])


def emblem_shapes(gap=GAP):
    """The six hulls, each cut back where the previous one lies on top, plus the sun."""
    hulls = [hull(math.radians(90 + 60 * k)) for k in range(6)]
    cut = [hulls[k].difference(hulls[k - 1].buffer(gap, join_style=2)) for k in range(6)]
    return cut + [Point(CENTER).buffer(SUN_RADIUS, quad_segs=32)]


def svg_path(shape):
    parts = getattr(shape, "geoms", [shape])
    return " ".join(
        "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in list(p.exterior.coords)[:-1]) + " Z" for p in parts
    )


def emblem(color, x=0, y=0, size=512, extra=""):
    paths = "".join(f'<path d="{svg_path(s)}"{extra}/>' for s in emblem_shapes())
    return f'<g transform="translate({x} {y}) scale({size / 512})" fill="{color}">{paths}</g>'


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


def symbolic_svg():
    """KDE symbolic icon: follows the color scheme's text color."""
    style = '<style id="current-color-scheme">.ColorScheme-Text { color: #232629; }</style>'
    return svg(512, 512, style + "\n" + emblem("currentColor", extra=' class="ColorScheme-Text"'))


def ascii_art(cols=38, rows=19, full="#", top='"', bottom=","):
    """Rasterizes the emblem; each character cell covers two vertically stacked samples.

    Uses wider gaps than the SVG, otherwise they vanish at character resolution.
    """
    shape = unary_union(emblem_shapes(gap=24))
    minx, miny, maxx, maxy = shape.bounds
    step_x = (maxx - minx) / cols
    step_y = (maxy - miny) / (rows * 2)

    def filled(cx, cy):
        # Majority vote of a 3x3 grid of samples inside the half-cell
        hits = sum(
            shape.contains(Point(minx + (cx + (i + 0.5) / 3) * step_x, miny + (cy + (j + 0.5) / 3) * step_y))
            for i in range(3) for j in range(3)
        )
        return hits >= 5

    lines = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            upper, lower = filled(c, 2 * r), filled(c, 2 * r + 1)
            line += full if upper and lower else top if upper else bottom if lower else " "
        lines.append(line.rstrip())
    return lines


def with_wordmark(lines):
    pad = " " * max(0, (max(map(len, lines)) - len(WORDMARK_ASCII[1])) // 2)
    return lines + [""] + [pad + line for line in WORDMARK_ASCII]


def main():
    font = TTFont(sys.argv[1])

    (OUT / "ferryos-logo.svg").write_text(svg(512, 512, emblem(TEAL)))
    (OUT / "ferryos-logo-on-dark.svg").write_text(svg(512, 512, emblem(TEAL_LIGHT)))
    (OUT / "ferryos-logo-symbolic.svg").write_text(symbolic_svg())

    body, width = wordmark(font, 148, 98, 112, NAVY, TEAL)
    total = int(148 + width + 16)
    (OUT / "ferryos-lockup.svg").write_text(svg(total, 128, emblem(TEAL, 0, 0, 128) + "\n" + body))
    body, _ = wordmark(font, 148, 98, 112, SAND, TEAL_LIGHT)
    (OUT / "ferryos-lockup-dark.svg").write_text(svg(total, 128, emblem(TEAL_LIGHT, 0, 0, 128) + "\n" + body))

    (OUT / "ferryos-ascii.txt").write_text("\n".join(with_wordmark(ascii_art())) + "\n")
    # fastfetch: block characters in color slot $1
    blocks = ascii_art(full="█", top="▀", bottom="▄")
    FASTFETCH_LOGO.write_text("$1" + "\n".join(with_wordmark(blocks)) + "\n")


if __name__ == "__main__":
    main()
