import math

from PIL import Image, ImageDraw

W, H = 512, 640
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

BLACK = (0, 0, 0)
LW = 5  # uniform line width, like MS Paint's straight-line tool

cx = W // 2

# ground line
d.line([(40, 560), (W - 40, 560)], fill=BLACK, width=LW)

# head: plain circle
head_r = 62
head_c = (cx, 150)
d.ellipse(
    [head_c[0] - head_r, head_c[1] - head_r, head_c[0] + head_r, head_c[1] + head_r],
    outline=BLACK,
    width=LW,
)

# angry eyebrows, slanting down and inward
d.line([(cx - 40, 128), (cx - 8, 142)], fill=BLACK, width=LW)
d.line([(cx + 8, 142), (cx + 40, 128)], fill=BLACK, width=LW)

# small dot eyes
d.ellipse([cx - 22, 150, cx - 10, 162], fill=BLACK)
d.ellipse([cx + 10, 150, cx + 22, 162], fill=BLACK)

# frowning mouth
d.line([(cx - 24, 190), (cx, 178), (cx + 24, 190)], fill=BLACK, width=LW)

# neck
d.line([(cx, 212), (cx, 232)], fill=BLACK, width=LW)

# body
d.line([(cx, 232), (cx, 360)], fill=BLACK, width=LW)

# shoulders: arms outstretched to the sides (T shape)
d.line([(cx - 95, 278), (cx + 95, 278)], fill=BLACK, width=LW)

# inverted-V legs, spread apart
d.line([(cx, 360), (cx - 80, 540), (cx - 80, 560)], fill=BLACK, width=LW)
d.line([(cx, 360), (cx + 80, 540), (cx + 80, 560)], fill=BLACK, width=LW)

img.save("stickman_clean.png")
print("Saved stickman_clean.png")