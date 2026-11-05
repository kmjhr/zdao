# -*- coding: utf-8 -*-
"""在预览图上标注每根手指的名字"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "03-美术资产", "手建模", "hand_3d_preview.png")
OUT = os.path.join(ROOT, "03-美术资产", "手建模", "hand_3d_labeled.png")
S = 9
img = Image.open(SRC).convert("RGBA")
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)
except Exception:
    f = ImageFont.load_default()

# 格坐标 (x, y) -> 像素
def P(x, y):
    return ((x + 28.0) * S, (36.0 - y) * S)

MARKS = [
    ("食指", -10.4, 21.0, "center"),
    ("中指", -2.9, 27.0, "center"),
    ("无名指", 4.6, 23.5, "center"),
    ("小指", 11.8, 17.5, "center"),
    ("拇指", -20.0, -3.0, "center"),
    ("手腕", 0.5, -32.0, "center"),
]

for name, gx, gy, anchor in MARKS:
    tx, ty = P(gx, gy)
    if name in ("食指", "拇指", "手腕"):
        tx += 8 if name == "食指" else 0
    d.text((tx, ty), name, font=f, fill=(26, 26, 26, 255), anchor="mm",
           stroke_width=3, stroke_fill=(255, 255, 255, 235))

img.save(OUT)
print("saved", OUT)
