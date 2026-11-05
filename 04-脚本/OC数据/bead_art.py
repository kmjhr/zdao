# -*- coding: utf-8 -*-
"""把 OC 角色渲染成拼豆图纸（16x16 颜色矩阵 → PNG）
产品验证：文 → 角色提取 → 拼豆图纸 的第 3 步渲染器
"""
from PIL import Image, ImageDraw

# 16x16 拼豆图纸：姐姐（深灰大衣 · 栗色卷发 · 轻声细语）
# 图例: H=栗发 h=深栗发 S=肤色 E=眼 C=大衣 c=大衣深
ROWS = [
    "HHHHHHHHHHHHHHHH",
    "HHHHHHHHHHHHHHHH",
    "HHHhhHHHHHHhhHHH",
    "HHhSSSSSSSSSShHH",
    "HHhSSSSSSSSSShHH",
    "HhSSSSSSSSSSSShH",
    "HhSSSSSSSSSSSShH",
    "HHhSSEESSEESShHH",
    "HhSSSSSSSSSSSShH",
    "HhSSSSSSSSSSSShH",
    "HhSSSSSSSSSSSShH",
    "HhSSSSSSSSSSSShH",
    "HHhSSSSSSSSSShHH",
    "HHCCCCCCCCCCCCHH",
    "HCCccCCCCCCccCCH",
    "HHCCCCCCCCCCCCHH",
]

COLORS = {
    "H": (123, 74, 47),    # 栗发  #7B4A2F
    "h": (90, 53, 32),     # 深栗  #5A3520
    "S": (242, 201, 160),  # 肤色  #F2C9A0
    "E": (62, 44, 30),     # 眼    #3E2C1E
    "C": (74, 74, 74),     # 大衣  #4A4A4A
    "c": (52, 52, 52),     # 大衣深 #343434
}
BOARD = (246, 241, 231)    # 拼豆板底 #F6F1E7

GRID, BEAD, RADIUS, MARGIN = 34, 30, 9, 22
n = len(ROWS[0])
for row in ROWS:
    assert len(row) == n, f"行宽错误: {row}"

size = MARGIN * 2 + GRID * n
img = Image.new("RGB", (size, size), BOARD)
d = ImageDraw.Draw(img)
for r, row in enumerate(ROWS):
    for c, ch in enumerate(row):
        x = MARGIN + c * GRID + (GRID - BEAD) // 2
        y = MARGIN + r * GRID + (GRID - BEAD) // 2
        d.rounded_rectangle([x, y, x + BEAD, y + BEAD], radius=RADIUS, fill=COLORS[ch])

import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = os.path.join(ROOT, "03-美术资产", "OC数据", "bead_oc_jiejie.png")
img.save(out)
print("saved", out, size, "x", size)
