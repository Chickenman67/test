"""Extract the geometric style spec from the reference stick-man PNGs.

Measures only what's needed to replicate the drawings: stroke width, head
geometry, eye style, arm count/angles, and leg structure (pure-V vs vertical).
"""

import os

from PIL import Image

DIR = r"C:\VIBE_CODE_CENTRAL\test"
FILES = [
    "standard stickman happy.png",
    "standard stickman mad happy.png",
    "standard stickman mad sad.png",
    "standard stickman sad.png",
]

THRESH = 128


def ink_mask(im):
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    mask = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if px[x, y] < THRESH:
                mask[y][x] = 1
    return mask, w, h


def stroke_width(mask, w, h):
    """Median horizontal ink run length -- proxy for stroke thickness."""
    runs = []
    for y in range(h):
        run = 0
        for x in range(w + 1):
            if x < w and mask[y][x]:
                run += 1
            else:
                if run >= 3:
                    runs.append(run)
                run = 0
    if not runs:
        return 0
    runs.sort()
    return runs[len(runs) // 2]


def column_hist(mask, w, h):
    return [sum(mask[y][x] for y in range(h)) for x in range(w)]


def row_hist(mask, w, h):
    return [sum(mask[y][x] for x in range(w)) for y in range(h)]


def head_region(mask, w, h):
    """Find the top-most horizontal ink span (the head)."""
    row = row_hist(mask, w, h)
    for y in range(h):
        if row[y] > 0:
            top = y
            break
    # head is where the horizontal span is widest in the top third
    best_y, best_span = top, 0
    for y in range(top, min(h, top + 160)):
        span = 0
        x = 0
        while x < w:
            if mask[y][x]:
                s0 = x
                while x < w and mask[y][x]:
                    x += 1
                span = max(span, x - s0)
            else:
                x += 1
        if span > best_span:
            best_span, best_y = span, y
    # head bbox around best_y
    xmin, xmax = w, -1
    ymin = min(y for y in range(top, best_y + 1) if row[y] > 0)
    for y in range(ymin, min(h, ymin + 80)):
        for x in range(w):
            if mask[y][x]:
                xmin = min(xmin, x)
                xmax = max(xmax, x)
    return xmin, xmax, ymin, best_span


def leg_structure(mask, w, h):
    """Return True if legs are a pure inverted V, else False (vertical shins)."""
    col = column_hist(mask, w, h)
    # below the head+body, look for two tall narrow vertical ink columns
    mid = size_of_interest(mask, w, h)
    ytop = int(mid * 0.70)
    vertical_cols = 0
    for x in range(w):
        if col[x] >= (h - ytop) * 0.35:  # long continuous vertical run
            vertical_cols += 1
    return vertical_cols, mid


def size_of_interest(mask, w, h):
    """Approx fraction of height the figure occupies below the head."""
    row = row_hist(mask, w, h)
    last = max(y for y in range(h) if row[y] > 0)
    first = min(y for y in range(h) if row[y] > 0)
    return (last + first) / 2.0


for f in FILES:
    im = Image.open(os.path.join(DIR, f))
    mask, w, h = ink_mask(im)
    sw = stroke_width(mask, w, h)
    xmin, xmax, ymin, head_span = head_region(mask, w, h)
    head_w = xmax - xmin + 1
    vcols, cy = leg_structure(mask, w, h)
    print(f"--- {f}  ({w}x{h})")
    print(f"  stroke_width(med horiz run): {sw}px")
    print(f"  head span(at widest row): {head_span}px, head bbox width: {head_w}px")
    print(f"  figure vertical extent below head near y={int(cy)}")
    print(f"  long vertical ink columns (leg shins if >=2): {vcols}")
    print()