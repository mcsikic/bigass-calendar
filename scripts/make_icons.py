#!/usr/bin/env python3
"""BAC icons — three tilted post-its on cream paper. Pure Pillow, no assets."""
from PIL import Image, ImageDraw
import os, math

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

PAPER = (245, 239, 223, 255)
INK = (43, 38, 32, 255)
PITS = [(255, 243, 163, 255), (211, 242, 194, 255), (255, 209, 224, 255)]  # M yellow / I green / both pink
RED = (224, 52, 43, 255)


def rounded(draw, xy, r, fill):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def make(size):
    img = Image.new("RGBA", (size, size), PAPER)
    d = ImageDraw.Draw(img)
    s = size / 512.0
    # frame
    d.rectangle([int(18 * s)] * 2 + [size - int(18 * s)] * 2, outline=INK, width=max(2, int(14 * s)))
    # three post-its, tilted
    specs = [(-8, 96, 120, PITS[0]), (6, 196, 210, PITS[1]), (-4, 296, 150, PITS[2])]
    for ang, ox, oy, col in specs:
        pit = Image.new("RGBA", (int(190 * s), int(170 * s)), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pit)
        pd.rectangle([0, 0, pit.width - 1, pit.height - 1], fill=col, outline=INK, width=max(1, int(4 * s)))
        # tape
        pd.rectangle([int(pit.width * 0.33), 0, int(pit.width * 0.67), int(24 * s)], fill=(255, 255, 255, 160))
        # scribble lines
        for i in range(3):
            y = int((60 + i * 34) * s)
            pd.line([int(22 * s), y, int(pit.width - 30 * s), y + int(4 * math.sin(i))], fill=INK, width=max(1, int(7 * s)))
        pit = pit.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(pit, (int(ox * s), int(oy * s)))
    # red asterisk-ish star top-right
    cx, cy, r = int(400 * s), int(112 * s), int(46 * s)
    for a in range(0, 180, 30):
        dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        d.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=RED, width=max(2, int(14 * s)))
    return img.convert("RGB")


for sz in (180, 192, 512):
    make(sz).save(os.path.join(OUT, f"icon-{sz}.png"))
    print(f"icon-{sz}.png ok")
