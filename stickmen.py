"""Generate hand-drawn MS-Paint-style stick men, procedurally (no AI).

Geometry is modeled on the reference image set: a short body, long legs that
form a pure inverted V meeting at the crotch (no vertical shin segments), a
wide oval head, two exactly-plain arms angled down-out, small plain dot eyes
with no lashes, and subtle natural brows + mouth driven by mood.

Emotions: happy | mad-happy | mad-sad | sad | random
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

BLACK = (8, 8, 8)
WHITE = (255, 255, 255)

EMOTIONS = {
    "happy":    ("none",  "smile"),
    "mad-happy":("angry", "smile"),
    "mad-sad":  ("angry", "frown"),
    "sad":      ("sad",   "frown"),
}


class StickMan:
    def __init__(self, seed: int = 0, w: int = 512, h: int = 640):
        self.rng = random.Random(seed)
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w, h), WHITE)
        self.d = ImageDraw.Draw(self.img)

    # --- smooth hand-drawn stroke primitives (gentle, low wobble) ---
    def _smooth_stroke(self, base, width, amp, freq, phase):
        pts = []
        prev = None
        n = len(base)
        for i, (x, y) in enumerate(base):
            if prev is not None:
                dx, dy = x - prev[0], y - prev[1]
                L = math.hypot(dx, dy) or 1.0
                nx, ny = -dy / L, dx / L
            else:
                nx, ny = 0.0, -1.0
            t = i / max(1, n - 1)
            off = amp * math.sin(2 * math.pi * freq * t + phase)
            pts.append((x + nx * off, y + ny * off))
            prev = (x, y)
        self.d.line(pts, fill=BLACK, width=width, joint="curve")

    def line(self, p1, p2, width=5, amp=1.2):
        (ax, ay), (bx, by) = p1, p2
        seg = 14
        base = [(ax + (bx - ax) * s / seg, ay + (by - ay) * s / seg) for s in range(seg + 1)]
        self._smooth_stroke(base, width, amp, self.rng.uniform(1.0, 1.5),
                            self.rng.uniform(0, 2 * math.pi))

    def oval(self, center, rx, ry, width=5, amp=1.2):
        cx0, cy0 = center
        n = 48
        waves = self.rng.randint(1, 2)
        phase = self.rng.uniform(0, 2 * math.pi)
        pts = []
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            r = 1.0 + (amp / rx) * math.sin(waves * a + phase)
            pts.append((cx0 + rx * r * math.cos(a), cy0 + ry * r * math.sin(a)))
        self.d.line(pts, fill=BLACK, width=width, joint="curve")

    def arc(self, p0, ctrl, p1, width=4, amp=1.0):
        ax, ay = p0
        bx, by = p1
        cx0, cy0 = ctrl
        n = 24
        base = []
        for i in range(n + 1):
            t = i / n
            u = 1 - t
            x = u * u * ax + 2 * u * t * cx0 + t * t * bx
            y = u * u * ay + 2 * u * t * cy0 + t * t * by
            base.append((x, y))
        self._smooth_stroke(base, width, amp, self.rng.uniform(1.0, 1.5),
                            self.rng.uniform(0, 2 * math.pi))

    def dot(self, center, r):
        x, y = center
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=BLACK)

    # --- face ---
    def _face(self, cx, cy, rx, ry, brow, mouth, rng):
        eye_y = cy + rng.uniform(-6, 2)
        ex = rx * rng.uniform(0.34, 0.40)
        Lx, Rx = cx - ex, cx + ex
        r1 = rng.uniform(2.6, 3.4)
        r2 = rng.uniform(2.6, 3.4)
        self.dot((Lx, eye_y), r1)
        self.dot((Rx, eye_y + rng.uniform(-2, 2)), r2)

        # brows
        b_w = rx * rng.uniform(0.18, 0.24)
        b_y = eye_y - ry * rng.uniform(0.26, 0.32)
        if brow == "angry":          # inner ends slant down
            self.line((Lx - b_w, b_y - 3), (Lx + b_w * 0.4, b_y + 2), width=4, amp=0.6)
            self.line((Rx + b_w, b_y - 3), (Rx - b_w * 0.4, b_y + 2), width=4, amp=0.6)
        elif brow == "sad":          # inner ends slant up (worried)
            self.line((Lx - b_w, b_y + 2), (Lx + b_w * 0.4, b_y - 3), width=4, amp=0.6)
            self.line((Rx + b_w, b_y + 2), (Rx - b_w * 0.4, b_y - 3), width=4, amp=0.6)

        # mouth
        m_y = cy + ry * rng.uniform(0.30, 0.38)
        m_w = rx * rng.uniform(0.22, 0.28)
        if mouth == "smile":         # ends up, center dips
            self.arc((cx - m_w, m_y), (cx, m_y + rng.uniform(4, 6)), (cx + m_w, m_y), width=4, amp=0.8)
        elif mouth == "frown":       # ends down, center rises
            self.arc((cx - m_w, m_y), (cx, m_y - rng.uniform(4, 6)), (cx + m_w, m_y), width=4, amp=0.8)
        else:                        # flat / neutral
            self.line((cx - m_w, m_y), (cx + m_w, m_y), width=4, amp=0.6)

    def draw(self, emotion: str = "random", seed: int = 0, cx: int = None) -> Image.Image:
        rng = self.rng
        if emotion == "random":
            emotion = rng.choice(list(EMOTIONS))
        brow, mouth = EMOTIONS[emotion]

        cx = cx or (self.w // 2)
        W, H = self.w, self.h

        # --- proportions: head 1 : torso 1.3 : legs 1.7 ---
        head_rx = rng.uniform(84, 92)            # wide oval head
        head_ry = rng.uniform(62, 68)            # half-height
        head_h = head_ry * 2
        torso_len = head_h * 1.3
        legs_len = head_h * 1.7

        head_x = cx + rng.uniform(-6, 6)
        head_top = rng.uniform(46, 56)
        head_y = head_top + head_ry               # center of head
        head_bottom = head_top + head_h
        cr = head_bottom + torso_len              # crotch
        feet_y = cr + legs_len                    # feet

        self.oval((head_x + rng.uniform(-4, 4), head_y + rng.uniform(-4, 4)),
                  head_rx, head_ry, width=5, amp=1.0)
        self._face(head_x, head_y, head_rx, head_ry, brow, mouth, rng)

        # torso: single line from chin to crotch
        bx = cx + rng.uniform(-5, 5)
        self.line((bx, head_bottom + rng.uniform(0, 6)), (bx, cr), width=5, amp=1.0)

        # arms: exactly two straight lines, angled down-out from the shoulders
        shoulder_y = head_bottom + head_ry * rng.uniform(0.40, 0.52)
        arm_len = head_ry * rng.uniform(1.60, 1.80)
        arm_drop = head_ry * rng.uniform(0.80, 1.00)
        self.line((bx, shoulder_y), (bx - arm_len, shoulder_y + arm_drop), width=4, amp=0.9)
        self.line((bx, shoulder_y), (bx + arm_len, shoulder_y + arm_drop), width=4, amp=0.9)

        # legs: inverted V, feet fairly apart
        spread = head_ry * rng.uniform(1.05, 1.20)
        foot_l = feet_y + rng.choice([0, 3, 5])
        foot_r = feet_y + rng.choice([0, 3, 5])
        self.line((bx, cr), (bx - spread, foot_l), width=5, amp=1.2)
        self.line((bx, cr), (bx + spread, foot_r), width=5, amp=1.2)

        return self.img


def make_stickman(seed: int, w: int = 512, h: int = 640, emotion: str = "random") -> Image.Image:
    return StickMan(seed, w, h).draw(emotion=emotion)


if __name__ == "__main__":
    import argparse
    import base64

    ap = argparse.ArgumentParser(description="Generate hand-drawn MS-Paint-style stick men")
    ap.add_argument("--count", type=int, default=12)
    ap.add_argument("--out", type=str, default="batch")
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=640)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--emotion", type=str, default="random",
                    help="happy | mad-happy | mad-sad | sad | random")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cards = []
    for i in range(args.count):
        seed = args.seed + i
        img = make_stickman(seed, args.width, args.height, args.emotion)
        fn = out / f"stickman_{seed:04d}.png"
        img.save(fn)
        b64 = base64.b64encode(fn.read_bytes()).decode()
        cards.append(
            "<div style='margin:10px'><img src='data:image/png;base64,{b}' width='180'>"
            "<div style='color:#ccc;text-align:center;font-size:12px'>{n}</div></div>".format(b=b64, n=fn.name)
        )
        print(f"wrote {fn}")

    html = (
        "<html><body style='background:#222;font-family:sans-serif;margin:0;padding:20px'>"
        "<h2 style='color:#fff'>MS-Paint stick men ({c})</h2>"
        "<div style='display:flex;flex-wrap:wrap'>{cards}</div></body></html>"
    ).format(c=args.count, cards="".join(cards))
    (out / "gallery.html").write_text(html, encoding="utf-8")
    print(f"gallery -> {out / 'gallery.html'}")