import base64
import random
import time
from pathlib import Path

import requests

PROMPT = (
    "A monochrome pictogram of a simple line-drawn stick figure man, like a minimalist "
    "flat clip-art icon. Thin plain black outline strokes ONLY. No color, no filled body, "
    "no skin, no clothing, no realistic features, no background shapes. Large plain "
    "black-outline circular head with two small black dot eyes, a short frowning line for "
    "a mouth, and two sharp angry diagonal eyebrows slanting down and inward. The body is "
    "a single thin black vertical line splitting at the bottom into two thin legs spread "
    "wide apart in an inverted V. From the shoulders, two thin straight arms extend out to "
    "the sides forming a T shape. Pure solid white background. Flat 2D line icon, outline only."
)

OUT = Path(__file__).parent.resolve()
N = 9
SEEDS = [random.randint(100, 99999) for _ in range(N)]


def fetch(seed: int) -> tuple[int, bytes]:
    url = ("https://image.pollinations.ai/prompt/{q}?width=1024&height=1024"
           "&model=flux&seed={seed}").format(q=urllib_quote(), seed=seed)
    r = requests.get(url, timeout=110)
    r.raise_for_status()
    return seed, r.content


def urllib_quote():
    from urllib.parse import quote
    return quote(PROMPT)


def main() -> None:
    entries = []
    for idx, seed in enumerate(SEEDS):
        _, data = fetch(seed)
        fn = OUT / f"var_{seed}.jpg"
        fn.write_bytes(data)
        b64 = base64.b64encode(data).decode()
        entries.append((fn.name, seed, b64))
        print(f"{fn.name}: {len(data)} bytes")
        if idx < len(SEEDS) - 1:
            time.sleep(16)

    cards = "".join(
        "<div style='margin:10px'><img src='data:image/jpeg;base64,{b64}' width='240'>"
        "<div style='color:#ccc;text-align:center;font-size:12px'>{name}<br>seed {seed}</div></div>".format(
            name=n, seed=s, b64=b
        )
        for (n, s, b) in entries
    )
    html = (
        "<html><body style='background:#222;font-family:sans-serif;margin:0;padding:20px'>"
        "<h2 style='color:#fff'>Angry stick-figure variants (random seeds, model=flux)</h2>"
        "<div style='display:flex;flex-wrap:wrap'>{cards}</div></body></html>"
    ).format(cards=cards)
    (OUT / "gallery.html").write_text(html, encoding="utf-8")
    print("Wrote gallery.html")


if __name__ == "__main__":
    main()